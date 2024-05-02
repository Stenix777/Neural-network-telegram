from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from common.settings import settings
from tgbot_app.utils.callbacks import ProfileCallback
from tgbot_app.utils.enums import ProfileButtons


async def gen_profile_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    for btn in ProfileButtons:
        builder.button(text=btn.value, callback_data=ProfileCallback(action=btn))

    builder.button(text="🧑‍🏭 Техподдержка", url=f"https://t.me/{settings.SUPPORT_USERNAME}")

    builder.adjust(1)

    return builder.as_markup()
