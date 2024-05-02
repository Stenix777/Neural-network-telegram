import os
from datetime import datetime, timedelta

from aiogram import Bot
from aiogram.dispatcher.event.bases import CancelHandler
from aiogram.enums import ChatAction
from aiogram.exceptions import TelegramBadRequest
from aiogram.types import Message, URLInputFile
from aiogram.utils.chat_action import ChatActionSender

from common.db_api import get_last_invoice, get_messages
from common.enums import ImageModels, ServiceModels, TextModels, VideoModels
from common.models import User
from common.services import neiro_api
from common.settings import settings
from tgbot_app.keyboards import gen_error_kb, gen_no_tokens_kb
from tgbot_app.utils.enums import GenerationResult
from tgbot_app.utils.generation_workers import run_service_generation
from tgbot_app.utils.text_variables import (ERROR_MAIN_TEXT, ERROR_STT_TEXT,
                                            ERROR_TRANSLATION_TEXT,
                                            VOICE_CLOSE_TEXT,
                                            VOICE_PROCESS_TEXT)


def decl(num: int, titles: tuple) -> str:
    cases = [2, 0, 1, 1, 1, 2]
    if 4 < num % 100 < 20:
        idx = 2
    elif num % 10 < 5:
        idx = cases[num % 10]
    else:
        idx = cases[5]
    return titles[idx]


def delete_file(path: str) -> None:
    try:
        os.remove(path)
    except:  # noqa
        pass


def can_send_query(user: User, model: ImageModels | TextModels | VideoModels) -> bool:  # TODO Review
    model_cost = settings.MODELS[model].cost
    if not user.tariff:
        if model in (ImageModels.KANDINSKY, ImageModels.STABLE_DIFFUSION, TextModels.GEMINI):
            if model == TextModels.GEMINI:
                return bool(user.gemini_daily_limit) or user.token_balance >= model_cost
            if model == ImageModels.KANDINSKY:
                return bool(user.kandinsky_daily_limit) or user.token_balance >= model_cost
            if model == ImageModels.STABLE_DIFFUSION:
                return bool(user.sd_daily_limit) or user.token_balance >= model_cost
        return user.token_balance >= model_cost
    else:
        if model in (TextModels.GPT_3_TURBO, TextModels.GEMINI, ImageModels.STABLE_DIFFUSION, ImageModels.KANDINSKY):
            return True
        return user.token_balance >= model_cost


async def send_no_balance_msg(user: User, bot: Bot) -> None:
    if not user.tariff:
        text = "🔒 Вам не хватает токенов для генерации! Но вы можете докупить их или оформить подписку на 30 дней."
    else:
        text = ("🔒 Похоже Вы использовали все Ваши токены, предоставленные по подписке. Но Вы можете купить еще "
                "токенов. Для Вас они будут в 2 раза дешевле.")
    markup = await gen_no_tokens_kb()
    await bot.send_message(chat_id=user.id, text=text, reply_markup=markup)
    raise CancelHandler()


async def handle_voice_prompt(message: Message, user: User, check_premium: bool = True) -> str:
    if check_premium and not user.tariff:
        await message.answer(text="🗣️ Голосовые запросы доступны только в тарифе PREMIUM.",
                             reply_markup=await gen_no_tokens_kb())
        raise CancelHandler()

    if message.voice.duration > 30:
        await message.answer(text="🗣️ Длина аудио не должна превышать 30сек. Попробуйте ещё раз.")
        raise CancelHandler()

    path = f"{settings.MEDIA_DIR}/tmp/{user.id}.ogg"
    await message.bot.download(file=message.voice.file_id, destination=path)
    voice_url = f"{settings.DOMAIN}/tmp/{user.id}.ogg"

    result = await neiro_api.speech_to_text(voice_url)

    delete_file(path)

    if not result.success:
        await message.answer(text=ERROR_STT_TEXT, reply_markup=await gen_error_kb())
        raise CancelHandler()

    return result.result


async def send_voice_answer(bot: Bot, user_id: int, text: str, speaker: str) -> GenerationResult:
    status = await bot.send_message(text=VOICE_PROCESS_TEXT, chat_id=user_id)

    async with ChatActionSender(bot=bot, chat_id=user_id, action=ChatAction.RECORD_VOICE):
        result = await run_service_generation(model=ServiceModels.TTS, speaker=speaker, text=text, delay=3)

        await status.delete()

        if not result.success:
            await bot.send_message(chat_id=user_id, text=ERROR_MAIN_TEXT, reply_markup=await gen_error_kb())
            return result

        try:
            await bot.send_voice(chat_id=user_id, voice=URLInputFile(url=result.result))
            return result
        except TelegramBadRequest:
            await bot.send_message(chat_id=user_id, text=VOICE_CLOSE_TEXT)
            return GenerationResult(success=False)


async def gen_conversation(user: User, prompt: str) -> list[dict]:
    if user.txt_model_role_id:
        conversation = [{"role": "system", "content": user.txt_model_role.prompt}]
    else:
        conversation = [{"role": "system", "content": "You are a personal helpful assistant. Fluent Russian speaks."}]

    if user.text_session_id:
        messages = await get_messages(user.text_session_id)  # noqa
        for msg in messages:
            if msg.prompt and msg.result:
                conversation.append({"role": "user", "content": msg.prompt})
                conversation.append({"role": "assistant", "content": msg.result})

    conversation.append({"role": "user", "content": prompt})

    return conversation


async def translate_text(text: str, message: Message) -> str:
    result = await neiro_api.translate(text)

    if result.success:
        return result.result

    await message.answer(text=ERROR_TRANSLATION_TEXT)
    raise CancelHandler()


def parse_user_work_struct(raw_struct: str) -> dict | None:
    struct = {}
    raw_lst = raw_struct.split("\n")
    cur_chapter = ""
    cur_subchapter = ""

    try:
        for row in raw_lst:
            if not row:
                continue
            if row.strip()[0] == "*":
                cur_chapter = row.replace("*", "").strip()
                struct[cur_chapter] = {}
            elif row.strip()[0] == "+":
                cur_subchapter = row.replace("+", "").strip()
                struct[cur_chapter][cur_subchapter] = []
            elif row.strip()[0] == "-":
                struct[cur_chapter][cur_subchapter].append(row.replace("-", "").strip())
            else:
                raise KeyError

    except KeyError:
        return

    return struct


async def can_create_refund(user: User) -> bool:
    if user.tariff.is_trial or not user.tariff:
        return False

    last_invoice = await get_last_invoice(user.id)

    if last_invoice:
        return (datetime.now() < last_invoice.created_at + timedelta(hours=48) and
                user.token_balance >= user.tariff.token_balance)
    return False
