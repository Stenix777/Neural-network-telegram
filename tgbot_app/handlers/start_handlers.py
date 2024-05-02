from aiogram import F, Router
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from common.models import User
from common.settings import settings
from tgbot_app.keyboards import main_kb
from tgbot_app.utils.text_variables import START_TEXT

router = Router()


@router.message(CommandStart())
@router.callback_query(F.data == "start")
async def start(message: Message | CallbackQuery, user: User, state: FSMContext):
    await state.clear()

    if isinstance(message, CallbackQuery):
        await message.answer()
        message = message.message

    await message.answer(text=START_TEXT.format(app_name=settings.APP_NAME), reply_markup=await main_kb(user))
