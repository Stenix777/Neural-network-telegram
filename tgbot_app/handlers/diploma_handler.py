from aiogram import F, Router
from aiogram.enums import ChatAction
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message, URLInputFile
from aiogram.utils.chat_action import ChatActionSender

from common.db_api import change_balance, create_service_query
from common.enums import ServiceModels
from common.models import User
from common.settings import settings
from tgbot_app.keyboards import (gen_confirm_start_work_kb,
                                 gen_diploma_struct_kb, gen_error_kb,
                                 gen_services_back_kb, gen_type_work_kb)
from tgbot_app.utils.callbacks import DiplomaCallback, LearningCallback
from tgbot_app.utils.enums import DiplomaAction, LearningButtons
from tgbot_app.utils.generation_workers import run_service_generation
from tgbot_app.utils.misc import parse_user_work_struct, send_no_balance_msg
from tgbot_app.utils.states import DiplomaState
from tgbot_app.utils.text_variables import (DIPLOMA_MAIN_TEXT,
                                            DIPLOMA_MODE_TEXT,
                                            DIPLOMA_START_GEN_TEXT,
                                            DIPLOMA_STRUCT_TEXT,
                                            ERROR_MAIN_TEXT, PROGRESS_TEXT)

router = Router()


@router.callback_query(LearningCallback.filter(F.type == LearningButtons.WORKS))
async def start_diploma(callback: CallbackQuery):
    await callback.message.answer(
        text=DIPLOMA_MAIN_TEXT.format(cost=settings.MODELS[ServiceModels.DIPLOMA].cost),
        reply_markup=await gen_type_work_kb()
    )
    await callback.answer()


@router.callback_query(DiplomaCallback.filter(F.action == DiplomaAction.SET_TYPE))
async def set_type_diploma(callback: CallbackQuery, callback_data: DiplomaCallback, state: FSMContext):
    await state.set_state(DiplomaState.THEME_WORK)
    await state.set_data({"type": callback_data.value})

    await callback.message.answer(text="Введите тему для Вашей работы:", reply_markup=await gen_services_back_kb())
    await callback.answer()


@router.message(DiplomaState.THEME_WORK)
async def set_diploma_theme(message: Message, state: FSMContext):
    theme = message.text.strip()
    await state.update_data({"theme": theme})

    await message.answer(text=DIPLOMA_MODE_TEXT.format(theme=theme), reply_markup=await gen_diploma_struct_kb())


@router.callback_query(DiplomaCallback.filter(F.action == DiplomaAction.GET_STRUCT))
async def get_diploma_struct(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer(text=DIPLOMA_STRUCT_TEXT, reply_markup=await gen_services_back_kb())
    await callback.answer()

    await state.set_state(DiplomaState.STRUCT_WORK)


@router.callback_query(DiplomaCallback.filter(F.action == DiplomaAction.CONFIRM))
@router.message(DiplomaState.STRUCT_WORK)
async def set_diploma_struct(message: Message | CallbackQuery, state: FSMContext):
    data = await state.get_data()
    theme = data["theme"]

    text = f"Тема Вашей работы: <b>{theme}</b>."

    if isinstance(message, Message):
        raw_struct = message.text
        struct = parse_user_work_struct(message.text)

        if not struct:
            await message.answer(
                text="Мы не смогли распознать Ваш план. Попробуйте ещё раз." + "\n\n" + DIPLOMA_STRUCT_TEXT,
                reply_markup=await gen_services_back_kb(),
            )
            return

        text += "\n\n" + "План Вашей работы:\n\n" + raw_struct

        await state.update_data({"struct": struct})

    else:
        await message.answer()
        message = message.message

    text += "\n\nГенерация займёт от 40 до 80 минут.\n\nПродолжить?"

    await message.answer(text=text, reply_markup=await gen_confirm_start_work_kb())


@router.callback_query(DiplomaCallback.filter(F.action == DiplomaAction.START))
async def run_diploma_generation(callback: CallbackQuery, user: User, state: FSMContext):
    if user.token_balance < settings.MODELS[ServiceModels.DIPLOMA].cost:
        await send_no_balance_msg(user=user, bot=callback.bot)

    data = await state.get_data()
    type_work = data.get("type")
    theme = data.get("theme")
    struct = data.get("struct")

    await state.clear()
    await callback.answer()

    status_1 = await callback.message.answer(DIPLOMA_START_GEN_TEXT.format(theme=theme))
    status_2 = await callback.message.answer(PROGRESS_TEXT.format(progress="1%"))

    result = await run_service_generation(model=ServiceModels.DIPLOMA, status=status_2, theme=theme, struct=struct,
                                          type_work=type_work)

    await status_1.delete()
    await status_2.delete()

    if not result.success:
        await callback.message.answer(text=ERROR_MAIN_TEXT, reply_markup=await gen_error_kb())
        return

    async with ChatActionSender(bot=callback.message.bot, chat_id=callback.message.from_user.id,
                                action=ChatAction.UPLOAD_DOCUMENT):
        await create_service_query(user_id=user.id, type=ServiceModels.DIPLOMA, result=result.result)
        await change_balance(user=user, model=settings.MODELS[ServiceModels.REWRITE])
        await callback.message.answer_document(document=URLInputFile(
            url=result.result, filename=f"{theme.replace(' ', '_')}.docx"
        ))
