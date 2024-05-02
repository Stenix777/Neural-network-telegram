from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from common.db_api import change_balance, create_service_query
from common.enums import ServiceModels
from common.models import User
from common.settings import settings
from tgbot_app.keyboards import gen_services_back_kb
from tgbot_app.utils.callbacks import OtherServicesCallback
from tgbot_app.utils.enums import OtherServicesButtons
from tgbot_app.utils.misc import handle_voice_prompt, send_no_balance_msg
from tgbot_app.utils.states import CommonState
from tgbot_app.utils.text_variables import STT_NO_VOICE_TEXT, STT_TEXT

router = Router()


@router.callback_query(OtherServicesCallback.filter(F.type == OtherServicesButtons.STT))
async def stt_handler(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer(text=STT_TEXT.format(cost=settings.MODELS[ServiceModels.STT].cost),
                                  reply_markup=await gen_services_back_kb())
    await callback.answer()
    await state.set_state(CommonState.STT)


@router.message(CommonState.STT)
async def run_stt(message: Message, user: User, state: FSMContext):
    if not message.voice:
        await message.answer(text=STT_NO_VOICE_TEXT, reply_markup=await gen_services_back_kb())
        return

    if user.token_balance < settings.MODELS[ServiceModels.STT].cost:
        await state.clear()
        await send_no_balance_msg(user=user, bot=message.bot)

    text = await handle_voice_prompt(message=message, user=user, check_premium=False)

    await message.answer(text)

    await create_service_query(user_id=user.id, type=ServiceModels.STT, result=text)
    await change_balance(user=user, model=settings.MODELS[ServiceModels.STT])
