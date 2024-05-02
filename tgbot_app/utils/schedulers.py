import asyncio
from datetime import datetime, timedelta

from aiogram import Bot
from loguru import logger
from sqlalchemy import select, update

from common.db_api import (create_invoice, get_admins_id,
                           get_users_for_recurring, unsubscribe_user,
                           update_object, get_obj_by_id, get_users_id, create_report)
from common.models import Tariff, User, db
from common.services import robokassa
from common.settings import settings
from tgbot_app.utils.text_generators import gen_report_text


async def daily_limits_update() -> None:
    logger.info("SCHEDULER | DailyLimitsUpdate | START")
    now = datetime.now()
    async with (db.async_session_factory() as session):
        stmt_free_users = update(User).where(
            User.update_daily_limits_time < now, User.is_active, User.tariff_id.is_(None)).values(
            update_daily_limits_time=now + timedelta(hours=24),
            gemini_daily_limit=settings.FREE_GEMINI_QUERIES,
            kandinsky_daily_limit=settings.FREE_KANDINSKY_QUERIES,
            sd_daily_limit=settings.FREE_SD_QUERIES
        )
        stmt_premium_users = update(User).where(  # TODO Review
            User.update_daily_limits_time < now, User.is_active, User.tariff_id.is_not(None)).values(
            update_daily_limits_time=now + timedelta(hours=24),
            gemini_daily_limit=select(Tariff.gemini_daily_limit).where(Tariff.id == User.tariff_id),
            kandinsky_daily_limit=select(Tariff.kandinsky_daily_limit).where(Tariff.id == User.tariff_id),
            sd_daily_limit=select(Tariff.sd_daily_limit).where(Tariff.id == User.tariff_id),
        )
        result_free = await session.execute(stmt_free_users)
        result_premium = await session.execute(stmt_premium_users)
        await session.commit()

        logger.info(f"SCHEDULER | DailyLimitsUpdate | FINISH ({result_free.rowcount + result_premium.rowcount})")


async def recurrent_payments() -> None:
    logger.info("SCHEDULER | RecurrentPayments | START")

    users = await get_users_for_recurring()
    if not users:
        logger.info("SCHEDULER | RecurrentPayments | NO USERS")

    tasks_for_unsubscribe = []
    tasks_for_update_users = []
    tasks_for_recurring = []

    for user in users:
        if user.payment_tries >= 4 or not user.recurring:
            tasks_for_unsubscribe.append(asyncio.create_task(unsubscribe_user(user)))
            continue

        tasks_for_update_users.append(asyncio.create_task(
            update_object(user,
                          payment_time=user.payment_time + timedelta(hours=24 if user.payment_tries == 1 else 12),
                          payment_tries=user.payment_tries + 1)
        ))

        if user.tariff.is_trial:
            tariff = await get_obj_by_id(Tariff, user.tariff.main_tariff_id)
        else:
            tariff = user.tariff

        invoice = await create_invoice(user_id=user.id, mother_invoice_id=user.mother_invoice_id, tariff_id=tariff.id)

        tasks_for_recurring.append(asyncio.create_task(
            robokassa.async_recurring_request(user_id=user.id, inv_id=invoice.id, price=tariff.price,
                                              desc=tariff.description, mother_inv_id=user.mother_invoice_id)
        ))

    await asyncio.gather(*tasks_for_unsubscribe)
    await asyncio.gather(*tasks_for_update_users)
    await asyncio.gather(*tasks_for_recurring)

    logger.info(f"SCHEDULER | RecurrentPayments | FINISH ({len(users)})")


async def send_report(bot: Bot) -> None:
    logger.info("SCHEDULER | SendReport | START")

    admins = await get_admins_id()
    report = await create_report()
    text = gen_report_text(report)

    for admin in admins:
        await bot.send_message(chat_id=admin, text=text)

    logger.info(f"SCHEDULER | SendReport | FINISH ({len(admins)})")


async def update_users_files() -> None:
    free_users_id = await get_users_id(premium=False)
    premium_users_id = await get_users_id(premium=True)

    with open(f"{settings.MEDIA_DIR}/users_files/free_users.txt", "w", encoding="utf-8") as file:
        file.write("\n".join(map(str, free_users_id)))

    with open(f"{settings.MEDIA_DIR}/users_files/premium_users.txt", "w", encoding="utf-8") as file:
        file.write("\n".join(map(str, premium_users_id)))
