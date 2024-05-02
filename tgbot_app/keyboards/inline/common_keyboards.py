from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from tgbot_app.utils.callbacks import CommonCallback, FAQCallback
from tgbot_app.utils.enums import CommonChapter, MainButtons


async def gen_error_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="🤖 Нейросети", callback_data=CommonCallback(chapter=CommonChapter.AIS))
    builder.button(text="📲 Сервисы", callback_data=CommonCallback(chapter=CommonChapter.SERVICES))
    builder.button(text="❓Помощь", callback_data=FAQCallback(chapter=MainButtons.FAQ))

    return builder.adjust(1).as_markup()
