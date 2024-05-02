from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from aiogram.utils.chat_action import ChatActionSender

from common.db_api import change_balance, create_service_query
from common.enums import ServiceModels
from common.models import User
from common.services import neiro_api
from common.settings import settings
from tgbot_app.keyboards import gen_error_kb, gen_services_back_kb
from tgbot_app.utils.callbacks import LearningCallback
from tgbot_app.utils.enums import LearningButtons
from tgbot_app.utils.misc import delete_file, send_no_balance_msg
from tgbot_app.utils.states import CommonState
from tgbot_app.utils.text_variables import (ERROR_MAIN_TEXT,
                                            VISION_NO_CAPTION_TEXT,
                                            VISION_PROCESS, VISION_TEXT)

router = Router()


@router.callback_query(LearningCallback.filter(F.type == LearningButtons.PHOTO))
async def vision_handler(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer(text=VISION_TEXT.format(cost=settings.MODELS[ServiceModels.VISION].cost),
                                  reply_markup=await gen_services_back_kb())
    await callback.answer()

    await state.set_state(CommonState.VISION)


@router.message(CommonState.VISION, F.photo)
async def get_data_vision(message: Message, user: User, state: FSMContext):
    if user.token_balance < settings.MODELS[ServiceModels.VISION].cost:
        await state.clear()
        await send_no_balance_msg(user=user, bot=message.bot)

    if not message.caption:
        await message.answer(VISION_NO_CAPTION_TEXT)
        return

    status = await message.answer(VISION_PROCESS)

    file_id = message.photo[-1].file_id
    image_path = f"{settings.MEDIA_DIR}/tmp/{file_id}.png"
    image_url = f"{settings.DOMAIN}/tmp/{file_id}.png"

    await message.bot.download(file=file_id, destination=image_path)

    async with ChatActionSender(bot=message.bot, chat_id=message.from_user.id):
        result = await neiro_api.vision(img_url=image_url, prompt=message.caption)

        delete_file(image_path)
        await status.delete()

        if not result.success:
            await message.answer(text=ERROR_MAIN_TEXT, reply_markup=await gen_error_kb())
            return

        await change_balance(user=user, model=settings.MODELS[ServiceModels.VISION])
        await create_service_query(user_id=user.id, type=ServiceModels.VISION, result=result.result)

        await message.answer(result.result)
