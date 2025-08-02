import asyncio
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'auction_bot_project.settings')
os.environ["DJANGO_ALLOW_ASYNC_UNSAFE"] = "true"
django.setup()


from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from telegram_bot.config import BOT_TOKEN
from telegram_bot.handlers import start, lot_actions
from telegram_bot.handlers import user_profile
# from telegram_bot.handlers import admin_handlers # Пока не реализовано
from telegram_bot.utils.scheduler import setup_scheduler # Пока не используется

async def main() -> None:
    default_properties = DefaultBotProperties(parse_mode=ParseMode.HTML)
    bot = Bot(token=BOT_TOKEN, default=default_properties)
    dp = Dispatcher(storage=MemoryStorage())

    dp.include_router(start.router)
    dp.include_router(lot_actions.router)
    dp.include_router(user_profile.router)
    # dp.include_router(admin_handlers.router) # Пока не реализовано

    # # БЛОК ДЛЯ ЗАДАЧ ПО РАСПИСАНИЮ
    # # scheduler = setup_scheduler(bot)
    # # scheduler.start()

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())