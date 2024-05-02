from aiogram import F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from common.db_api import reset_session
from common.models import User
from common.settings import settings
from tgbot_app.keyboards import (gen_ai_types_kb, gen_img_model_kb,
                                 gen_main_video_kb, gen_txt_settings_kb)
from tgbot_app.utils.callbacks import AiTypeCallback, CommonCallback
from tgbot_app.utils.enums import (AiTypeButtons, CommonChapter,
                                   DefaultCommands, MainButtons)
from tgbot_app.utils.states import GenerationState
from tgbot_app.utils.text_generators import (gen_img_settings_text,
                                             gen_txt_settings_text)
from tgbot_app.utils.text_variables import (AIS_TEXT, RECONSTRUCTION_TEXT,
                                            VIDEO_MAIN_TEXT)

router = Router()


@router.message(Command(DefaultCommands.ais.name))
@router.message(F.text == MainButtons.AIS.value)
@router.callback_query(CommonCallback.filter(F.chapter == CommonChapter.AIS))
async def show_ai_types(message: Message | CallbackQuery, state: FSMContext):
    await state.clear()

    if isinstance(message, CallbackQuery):
        await message.answer()
        message = message.message

    await message.answer(text=AIS_TEXT.format(app_name=settings.APP_NAME), reply_markup=await gen_ai_types_kb())


@router.callback_query(AiTypeCallback.filter(F.type == AiTypeButtons.TEXT))
async def text_generation_handler(callback: CallbackQuery, user: User, state: FSMContext):
    await reset_session(user)

    await callback.message.answer(text=gen_txt_settings_text(user), reply_markup=await gen_txt_settings_kb(user))
    await callback.answer()

    await state.set_state(GenerationState.TEXT)


@router.callback_query(AiTypeCallback.filter(F.type == AiTypeButtons.IMAGE))
async def image_generation_handler(callback: CallbackQuery, user: User, state: FSMContext):
    await callback.message.answer(text=gen_img_settings_text(user), reply_markup=await gen_img_model_kb(user))
    await callback.answer()

    await state.set_state(GenerationState.IMAGE)


@router.callback_query(AiTypeCallback.filter(F.type == AiTypeButtons.VIDEO))
async def video_generation_handler(callback: CallbackQuery, state: FSMContext):
    await state.clear()

    await callback.message.answer(text=VIDEO_MAIN_TEXT, reply_markup=await gen_main_video_kb())
    await callback.answer()


@router.callback_query(AiTypeCallback.filter(F.type == AiTypeButtons.MUSIC))
async def music_generation_handler(callback: CallbackQuery, state: FSMContext):
    await state.clear()

    await callback.answer(RECONSTRUCTION_TEXT, show_alert=True)
