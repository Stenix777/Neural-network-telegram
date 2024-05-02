from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from tgbot_app.utils.callbacks import (CommonCallback, LearningCallback,
                                       OtherServicesCallback, ServicesCallback,
                                       WorkingCallback)
from tgbot_app.utils.enums import (CommonChapter, LearningButtons,
                                   OtherServicesButtons, ServicesButtons,
                                   WorkingButtons)


async def gen_services_back_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="↩️ Назад", callback_data=CommonCallback(chapter=CommonChapter.SERVICES))

    return builder.as_markup()


async def gen_services_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    for service in ServicesButtons:
        builder.button(text=service.value, callback_data=ServicesCallback(type=service))

    return builder.adjust(1).as_markup()


async def gen_learning_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    for service in LearningButtons:
        builder.button(text=service.value, callback_data=LearningCallback(type=service))

    builder.button(text="↩️ Назад", callback_data=CommonCallback(chapter=CommonChapter.SERVICES))

    return builder.adjust(1).as_markup()


async def gen_working_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    for service in WorkingButtons:
        builder.button(text=service.value, callback_data=WorkingCallback(type=service))

    builder.button(text="↩️ Назад", callback_data=CommonCallback(chapter=CommonChapter.SERVICES))

    return builder.adjust(1).as_markup()


async def gen_other_services_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    for service in OtherServicesButtons:
        builder.button(text=service.value, callback_data=OtherServicesCallback(type=service))

    builder.button(text="↩️ Назад", callback_data=CommonCallback(chapter=CommonChapter.SERVICES))

    return builder.adjust(1).as_markup()
