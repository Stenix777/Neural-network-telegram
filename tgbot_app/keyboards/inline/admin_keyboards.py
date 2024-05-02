from aiogram.types import InlineKeyboardMarkup, WebAppInfo
from aiogram.utils.keyboard import InlineKeyboardBuilder

from common.settings import settings
from tgbot_app.utils.callbacks import AdminCallback, AdminLinksCallback
from tgbot_app.utils.enums import AdminLinksButtons, AdminMainButtons


async def gen_admin_main_kb(user_id: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    for btn in AdminMainButtons:
        builder.button(text=btn.value, callback_data=AdminCallback(chapter=btn))

    return builder.adjust(1).as_markup()


async def gen_admin_links_kb(user_id: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    builder.button(text=AdminLinksButtons.CREATE.value,
                   callback_data=AdminLinksCallback(command=AdminLinksButtons.CREATE))
    builder.button(text="📈 Мои ссылки",
                   web_app=WebAppInfo(url=f"{settings.DOMAIN}/reports/links/{user_id}/"))

    return builder.adjust(2).as_markup()
