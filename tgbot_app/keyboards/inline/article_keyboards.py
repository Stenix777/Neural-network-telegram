from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from tgbot_app.utils.callbacks import ArticleCallback, ServicesCallback
from tgbot_app.utils.enums import (ArticleAction, ArticleModes, SearchEngine,
                                   ServicesButtons, WorkPlanButtons)


async def gen_article_mode_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    for mode in ArticleModes:
        builder.button(text=mode.value, callback_data=ArticleCallback(action=ArticleAction.MODE, value=mode))

    builder.button(text="↩️ Назад", callback_data=ServicesCallback(type=ServicesButtons.WORK))

    return builder.adjust(1).as_markup()


async def gen_article_search_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    for engine in SearchEngine:
        builder.button(text=engine.value, callback_data=ArticleCallback(action=ArticleAction.ENGINE, value=engine))

    builder.button(text="↩️ Назад", callback_data=ServicesCallback(type=ServicesButtons.WORK))

    return builder.adjust(2, 1).as_markup()


async def gen_edit_work_plan_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    for btn in WorkPlanButtons:
        builder.button(text=btn.value, callback_data=ArticleCallback(action=ArticleAction.WORK_PLAN, value=btn))

    builder.button(text="↩️ Назад", callback_data=ServicesCallback(type=ServicesButtons.WORK))

    return builder.adjust(2, 1).as_markup()
