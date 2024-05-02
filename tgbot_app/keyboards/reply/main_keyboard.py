from aiogram.types import ReplyKeyboardMarkup
from aiogram.utils.keyboard import ReplyKeyboardBuilder

from common.models import User
from tgbot_app.utils.enums import MainButtons


async def main_kb(user: User) -> ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()

    for btn in MainButtons:
        builder.button(text=btn)

    if user.is_admin:
        builder.button(text="⚒️ Панель администратора")

    return builder.adjust(2, 2, 1).as_markup(resize_keyboard=True)
