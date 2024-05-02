from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from common.settings import settings
from tgbot_app.utils.callbacks import FAQCallback
from tgbot_app.utils.enums import (FAQFinancesButtons, FAQMainButtons,
                                   FAQProblemsButtons, FAQRecButtons,
                                   MainButtons)


async def gen_back_faq_kb(to_chapter=None) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    if not to_chapter:
        to_chapter = MainButtons.FAQ

    builder.button(text="↩️ Назад", callback_data=FAQCallback(chapter=to_chapter))

    return builder.adjust(1).as_markup()


async def gen_main_faq_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    for btn in FAQMainButtons:
        builder.button(text=btn.value, callback_data=FAQCallback(chapter=btn))

    return builder.adjust(1).as_markup()


async def gen_faq_rec_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    for btn in FAQRecButtons:
        builder.button(
            text=btn.value,
            callback_data=FAQCallback(chapter=FAQMainButtons.RECOMMENDATIONS, sub_chapter=btn.name),
        )

    builder.button(text="↩️ Назад", callback_data=FAQCallback(chapter=MainButtons.FAQ))

    return builder.adjust(1).as_markup()


async def gen_faq_problems_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    for btn in FAQProblemsButtons:
        builder.button(text=btn.value, callback_data=FAQCallback(chapter=FAQMainButtons.PROBLEMS, sub_chapter=btn.name))

    builder.button(text="Перезапустить бота", callback_data="start")
    builder.button(text="↩️ Назад", callback_data=FAQCallback(chapter=MainButtons.FAQ))

    return builder.adjust(1).as_markup()


async def gen_faq_inline_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    builder.button(text="Добавить бота в группу", url=f"https://t.me/{settings.BOT_USERNAME}?startgroup")
    builder.button(
        text="Какие команды есть у бота?",
        callback_data=FAQCallback(chapter=FAQMainButtons.INLINE, sub_chapter="cmds"),
    )
    builder.button(text="↩️ Назад", callback_data=FAQCallback(chapter=MainButtons.FAQ))

    return builder.adjust(1).as_markup()


async def gen_faq_finances_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    for btn in FAQFinancesButtons:
        builder.button(text=btn.value, callback_data=FAQCallback(chapter=FAQMainButtons.FINANCES, sub_chapter=btn.name))

    builder.button(text="↩️ Назад", callback_data=FAQCallback(chapter=MainButtons.FAQ))

    return builder.adjust(1).as_markup()


async def gen_faq_finances_sub_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="🧑‍🏭Написать в тех-поддержку", url=f"https://t.me/{settings.SUPPORT_USERNAME}")
    builder.button(text="↩️ Назад", callback_data=FAQCallback(chapter=FAQMainButtons.FINANCES))

    return builder.adjust(1).as_markup()
