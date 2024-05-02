from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import CallbackQuery, Message

from common.db_api import create_refund, get_obj_by_id, update_object
from common.models import Tariff, User
from tgbot_app.keyboards import (gen_confirm_premium_kb, gen_premium_cancel_kb,
                                 gen_premium_kb, main_kb)
from tgbot_app.utils.callbacks import PaymentCallback, ProfileCallback
from tgbot_app.utils.enums import (DefaultCommands, PaymentAction,
                                   ProfileButtons)
from tgbot_app.utils.misc import can_create_refund
from tgbot_app.utils.text_generators import (gen_confirm_tariff_text,
                                             gen_premium_canceled_text,
                                             gen_refund_text)
from tgbot_app.utils.text_variables import PREMIUM_TEXT, REACTIVATE_RECURRING_TEXT

router = Router()


@router.message(Command(DefaultCommands.subscription.name))
@router.callback_query(ProfileCallback.filter(F.action == ProfileButtons.PREMIUM))
async def premium_handler(message: Message | CallbackQuery, user: User):
    if isinstance(message, CallbackQuery):
        await message.answer()
        message = message.message

    await message.answer(text=PREMIUM_TEXT, reply_markup=await gen_premium_kb(user))


@router.callback_query(PaymentCallback.filter(F.action == PaymentAction.SUBSCRIBE))
async def premium_confirm(callback: CallbackQuery, callback_data: PaymentCallback, user: User):
    tariff = await get_obj_by_id(Tariff, callback_data.value)

    await callback.message.answer(text=await gen_confirm_tariff_text(tariff),
                                  reply_markup=await gen_confirm_premium_kb(user=user, tariff=tariff),
                                  disable_web_page_preview=True)
    await callback.answer()


@router.callback_query(PaymentCallback.filter(F.action == PaymentAction.CANCEL))
async def premium_cancel(callback: CallbackQuery, user: User):
    can_refund = await can_create_refund(user)

    await callback.message.answer(text=gen_refund_text(await can_create_refund(user)),
                                  reply_markup=await gen_premium_cancel_kb(refund=can_refund),
                                  disable_web_page_preview=True)
    await callback.answer()


@router.callback_query(PaymentCallback.filter(F.action == PaymentAction.CONFIRM_CANCEL))
async def premium_cancel_confirm(callback: CallbackQuery, callback_data: PaymentCallback, user: User):
    refund = bool(callback_data.value)

    text = gen_premium_canceled_text(refund)
    markup = await main_kb(user)

    if refund:
        await create_refund(user)
    else:
        await update_object(user, recurring=False)

    await callback.message.answer(text=text, reply_markup=markup)
    await callback.answer()


@router.callback_query(PaymentCallback.filter(F.action == PaymentAction.REACTIVATE))
async def reactivate_recurring(callback: CallbackQuery, user: User):

    await update_object(user, recurring=True)

    await callback.message.answer(text=REACTIVATE_RECURRING_TEXT, reply_markup=await main_kb(user))
    await callback.answer()
