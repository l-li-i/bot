from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties # Добавляем импорт
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from telegram_bot.config import BOT_TOKEN

# Инициализируем свойства бота
default_properties = DefaultBotProperties(parse_mode=ParseMode.HTML)

# Передаем свойства в бот
bot = Bot(token=BOT_TOKEN, default=default_properties)

dp = Dispatcher(storage=MemoryStorage())
