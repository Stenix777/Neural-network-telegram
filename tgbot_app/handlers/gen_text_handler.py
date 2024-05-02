from aiogram import Router
from aiogram.exceptions import TelegramBadRequest
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from aiogram.utils.chat_action import ChatActionSender

from common.db_api import change_balance, create_text_query
from common.models import User
from common.services import neiro_api
from common.settings import settings
from tgbot_app.keyboards import gen_error_kb
from tgbot_app.utils.misc import (can_send_query, gen_conversation,
                                  handle_voice_prompt, send_no_balance_msg,
                                  send_voice_answer)
from tgbot_app.utils.states import GenerationState
from tgbot_app.utils.text_variables import ERROR_MAIN_TEXT

router = Router()


@router.message(GenerationState.TEXT)
async def run_text_generation(message: Message, user: User, state: FSMContext):
    model = user.txt_model

    if not can_send_query(user=user, model=model):
        await send_no_balance_msg(user=user, bot=message.bot)

    await state.set_state(GenerationState.IN_PROCESS)
    status = await message.answer("📄 Мы отвечаем на Ваш вопрос, дождитесь окончания генерации.")

    if message.voice:
        prompt = await handle_voice_prompt(message=message, user=user)
    elif message.text:
        prompt = message.text
    else:
        return

    conversation = await gen_conversation(user=user, prompt=prompt)

    async with ChatActionSender(bot=message.bot, chat_id=message.from_user.id):
        result = await neiro_api.completion(model=model, conversation=conversation)

        if result.success:
            await create_text_query(user_id=user.id, session_id=user.text_session_id, prompt=prompt,
                                    result=result.result, model=model)
            answer = [result.result[x:x+4096] for x in range(0, len(result.result), 4096)] if len(result.result) > 4096 else [result.result]
            markup = None
        else:
            answer = [ERROR_MAIN_TEXT]
            markup = await gen_error_kb()

        await status.delete()

        for part in answer:
            try:
                await message.answer(text=part, parse_mode="Markdown")
            except TelegramBadRequest:
                await message.answer(text=part, reply_markup=markup, parse_mode=None)

    await change_balance(user=user, model=settings.MODELS[model])
    await state.set_state(GenerationState.TEXT)

    if user.tts_mode:
        await send_voice_answer(bot=message.bot, user_id=user.id, text=result.result, speaker=user.tts_mode)
