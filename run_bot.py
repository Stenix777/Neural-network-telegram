import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.types import (BotCommand, BotCommandScopeAllGroupChats,
                           BotCommandScopeAllPrivateChats)
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger
from loguru import logger

from common.settings import settings
from tgbot_app.handlers import main_router
from tgbot_app.middlewares import ChannelMiddleware, UserMiddleware
from tgbot_app.utils.enums import DefaultCommands
from tgbot_app.utils.schedulers import (daily_limits_update,
                                        recurrent_payments, send_report, update_users_files)


def _set_loggers() -> None:
    logger.add("logs/bot.log", rotation="00:00", level="ERROR", enqueue=True)
    if settings.DEBUG:
        logging.basicConfig(level=logging.INFO)
    else:
        logging.basicConfig(level=logging.WARNING)


def _connect_middlewares(dp: Dispatcher) -> None:
    dp.message.middleware.register(UserMiddleware())
    dp.callback_query.middleware.register(UserMiddleware())
    dp.message.middleware.register(ChannelMiddleware())
    dp.callback_query.middleware.register(ChannelMiddleware())


def _set_schedulers(bot: Bot) -> None:
    scheduler = AsyncIOScheduler(timezone="Europe/Moscow")
    scheduler.add_job(daily_limits_update, trigger=IntervalTrigger(minutes=5))
    scheduler.add_job(recurrent_payments, trigger=IntervalTrigger(minutes=15))
    scheduler.add_job(send_report, trigger=CronTrigger(hour=0, minute=5), kwargs={"bot": bot})
    scheduler.add_job(update_users_files, trigger=CronTrigger(hour=0, minute=0))
    scheduler.start()


async def _set_default_commands(bot: Bot) -> None:
    await bot.delete_my_commands()

    await bot.set_my_commands(commands=[], scope=BotCommandScopeAllGroupChats())
    await bot.set_my_commands(
        commands=[BotCommand(command=cmd.name, description=cmd.value) for cmd in DefaultCommands],
        scope=BotCommandScopeAllPrivateChats()
    )


async def main() -> None:
    _set_loggers()

    bot = Bot(token=settings.TG_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp = Dispatcher()

    await _set_default_commands(bot)
    _set_schedulers(bot)
    dp.include_router(main_router)
    _connect_middlewares(dp)

    logger.info("Start polling...")

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())
