from aiogram import Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from common.db_api import update_object
from common.enums import TextModels
from common.models import User
from tgbot_app.handlers.gen_text_handler import run_text_generation
from tgbot_app.handlers.rewrite_handler import get_data_rewrite
from tgbot_app.handlers.vision_handler import get_data_vision

router = Router()


@router.message()
async def no_query_model(message: Message, user: User, state: FSMContext):
    if message.photo:
        await get_data_vision(message, user, state)
    elif message.document:
        await get_data_rewrite(message, user, state)
    elif message.text or message.voice:
        model = TextModels.GPT_3_TURBO if user.tariff_id else TextModels.GEMINI

        if user.txt_model != model:
            await update_object(user, txt_model=model)

        await run_text_generation(message, user, state)
