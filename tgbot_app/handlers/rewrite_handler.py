from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message, URLInputFile

from common.db_api import change_balance, create_service_query
from common.enums import ServiceModels
from common.models import User
from common.settings import settings
from tgbot_app.keyboards import gen_error_kb, gen_services_back_kb
from tgbot_app.utils.callbacks import LearningCallback, WorkingCallback
from tgbot_app.utils.enums import LearningButtons, WorkingButtons
from tgbot_app.utils.generation_workers import run_service_generation
from tgbot_app.utils.misc import delete_file, send_no_balance_msg
from tgbot_app.utils.states import CommonState
from tgbot_app.utils.text_variables import (ERROR_MAIN_TEXT, PROGRESS_TEXT,
                                            REWRITE_TEXT)

router = Router()


@router.callback_query(WorkingCallback.filter(F.type == WorkingButtons.REWRITE))
@router.callback_query(LearningCallback.filter(F.type == LearningButtons.ANTIPLAGIARISM))
async def rewrite_handler(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer(text=REWRITE_TEXT.format(cost=settings.MODELS[ServiceModels.REWRITE].cost),
                                  reply_markup=await gen_services_back_kb())
    await callback.answer()

    await state.set_state(CommonState.REWRITE)


@router.message(CommonState.REWRITE)
async def get_data_rewrite(message: Message, user: User, state: FSMContext):
    if user.token_balance < settings.MODELS[ServiceModels.REWRITE].cost:
        await state.clear()
        await send_no_balance_msg(user=user, bot=message.bot)

    file_path = url_to_file = text = None

    if message.document:
        file_name = message.document.file_name
        extension = file_name.split(".")[-1]

        if extension not in ("txt", "docx"):
            await message.answer(text="Файл должен быть с разрешением txt или docx. Пожалуйста попробуйте ещё раз.",
                                 reply_markup=await gen_services_back_kb())
            return

        file_path = f"{settings.MEDIA_DIR}/tmp/{message.from_user.id}_{file_name}"
        url_to_file = f"{settings.DOMAIN}/tmp/{message.from_user.id}_{file_name}"
    elif message.text:
        text = message.text
    else:
        await message.answer("Мы не нашли данных для рерайта. Пожалуйста, попробуйте ещё раз.")
        return

    status = await message.answer(PROGRESS_TEXT.format(progress="1%"))

    result = await run_service_generation(model=ServiceModels.REWRITE, status=status, url_to_file=url_to_file,
                                          text=text)

    if file_path:
        delete_file(file_path)

    await status.delete()

    if not result.success:
        await message.answer(text=ERROR_MAIN_TEXT, reply_markup=await gen_error_kb())
        return

    if message.document:
        await message.answer_document(document=URLInputFile(url=result.result, filename=file_name))  # noqa
    else:
        await message.answer(result.result)

    await create_service_query(user_id=user.id, type=ServiceModels.REWRITE, result=result.result)
    await change_balance(user=user, model=settings.MODELS[ServiceModels.REWRITE])
