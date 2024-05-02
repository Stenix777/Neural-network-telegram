from aiogram import F, Router
from aiogram.exceptions import TelegramBadRequest
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from common.db_api import change_balance, create_service_query
from common.enums import ServiceModels
from common.models import User
from common.settings import settings
from tgbot_app.keyboards import (gen_main_speaker_kb, gen_speaker_category_kb,
                                 gen_tts_kb)
from tgbot_app.utils.callbacks import OtherServicesCallback, SileroCallback
from tgbot_app.utils.enums import OtherServicesButtons, SileroAction
from tgbot_app.utils.misc import send_no_balance_msg, send_voice_answer
from tgbot_app.utils.states import CommonState
from tgbot_app.utils.text_variables import TTS_NO_TEXT_TEXT, TTS_TEXT

router = Router()


@router.callback_query(OtherServicesCallback.filter(F.type == OtherServicesButtons.TTS))
async def tts_handler(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer(text=TTS_TEXT.format(cost=settings.MODELS[ServiceModels.TTS].cost),
                                  reply_markup=await gen_tts_kb(cur_speaker="eugene"))
    await callback.answer()

    await state.set_state(CommonState.TTS)
    await state.set_data({"speaker": "eugene"})


@router.callback_query(SileroCallback.filter(F.action == SileroAction.BACK_TO_SERVICE))
async def back_to_tts(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_reply_markup(
        reply_markup=await gen_tts_kb(cur_speaker=(await state.get_data()).get("speaker")))
    await callback.answer()


@router.callback_query(SileroCallback.filter(F.action == SileroAction.START_SERVICE))
async def choice_speaker_tts(callback: CallbackQuery, state: FSMContext):
    markup = await gen_main_speaker_kb(cur_speaker=(await state.get_data()).get("speaker"), is_service=True)
    await callback.message.edit_reply_markup(reply_markup=markup)
    await callback.answer()


@router.callback_query(SileroCallback.filter(F.action == SileroAction.SHOW_CATEGORY_STATE))
async def show_speaker_category_tts(callback: CallbackQuery, callback_data: SileroCallback, state: FSMContext):
    category = callback_data.category
    subcategory = callback_data.subcategory

    markup = await gen_speaker_category_kb(cur_speaker=(await state.get_data()).get("speaker"), category=category,
                                           cur_subcategory=subcategory, is_service=True)
    try:
        await callback.message.edit_reply_markup(reply_markup=markup)
    except TelegramBadRequest:
        pass
    await callback.answer()


@router.callback_query(SileroCallback.filter(F.action == SileroAction.SET_STATE))
async def set_speaker_handler_tts(callback: CallbackQuery, callback_data: SileroCallback, state: FSMContext):
    speaker = callback_data.value
    category = callback_data.category
    subcategory = callback_data.subcategory

    await state.set_data({"speaker": speaker})

    markup = await gen_speaker_category_kb(cur_speaker=speaker, category=category, cur_subcategory=subcategory,
                                           is_service=True)
    try:
        await callback.message.edit_reply_markup(reply_markup=markup)
    except TelegramBadRequest:
        pass
    await callback.answer()


@router.message(CommonState.TTS)
async def run_tts(message: Message, user: User, state: FSMContext):
    if user.token_balance < settings.MODELS[ServiceModels.TTS].cost:
        await state.clear()
        await send_no_balance_msg(user=user, bot=message.bot)

    if not message.text:
        await message.answer(TTS_NO_TEXT_TEXT)
        return

    speaker = (await state.get_data()).get("speaker")

    if not speaker:
        return

    result = await send_voice_answer(bot=message.bot, user_id=user.id, text=message.text, speaker=speaker)

    if result.success:
        await create_service_query(user_id=user.id, type=ServiceModels.TTS, result=result.result)
        await change_balance(user=user, model=settings.MODELS[ServiceModels.TTS])
