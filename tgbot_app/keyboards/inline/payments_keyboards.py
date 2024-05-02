from aiogram.types import InlineKeyboardMarkup, WebAppInfo
from aiogram.utils.keyboard import InlineKeyboardBuilder

from common.db_api import get_tariffs
from common.models import Tariff, User
from common.settings import settings
from tgbot_app.utils.callbacks import PaymentCallback, ProfileCallback
from tgbot_app.utils.enums import PaymentAction, ProfileButtons


async def gen_no_tokens_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="💎 Купить токенов", callback_data=ProfileCallback(action=ProfileButtons.TOKENS))
    builder.button(text="💳 Оформить подписку", callback_data=ProfileCallback(action=ProfileButtons.PREMIUM))

    return builder.adjust(1).as_markup()


async def gen_premium_kb(user: User) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    if not user.tariff:
        tariffs = await get_tariffs(is_trial=user.first_payment)

        for tariff in tariffs:
            builder.button(
                text=f"💳 {tariff.name}",
                callback_data=PaymentCallback(action=PaymentAction.SUBSCRIBE, value=tariff.id),
            )

    else:
        if not user.recurring:
            builder.button(
                text="Возобновить подписку",
                callback_data=PaymentCallback(action=PaymentAction.REACTIVATE, value=False),
            )
        else:
            builder.button(
                text="Отказаться от подписки",
                callback_data=PaymentCallback(action=PaymentAction.CANCEL, value=False),
            )

    return builder.adjust(1).as_markup()


async def gen_confirm_premium_kb(user: User, tariff: Tariff) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(
        text=f"Оплатить {tariff.price}₽",
        web_app=WebAppInfo(url=f"{settings.DOMAIN}/payments/redirect/{tariff.id}/{user.id}/"))

    return builder.as_markup()


async def gen_premium_cancel_kb(refund: bool = False) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    builder.button(text="❌ Отказаться от подписки",
                   callback_data=PaymentCallback(action=PaymentAction.CONFIRM_CANCEL, value=refund))
    builder.button(text="✅ Вернуться в меню", callback_data="start")

    return builder.adjust(1).as_markup()


async def gen_tokens_kb(user: User) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    tariffs = await get_tariffs(is_extra=True)

    for tariff in tariffs:
        if user.tariff and not user.tariff.is_trial:
            price = int(tariff.price / 2)
        else:
            price = tariff.price
        url = f"{settings.DOMAIN}/payments/redirect/{tariff.id}/{user.id}/"

        builder.button(text=f"💎 {tariff.name} / {price} ₽ 💸", web_app=WebAppInfo(url=url))

    return builder.adjust(1).as_markup()
