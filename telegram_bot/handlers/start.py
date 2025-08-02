from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command
from users_app.models import UserProfile
from telegram_bot.keyboards.inline_kb import main_menu_keyboard
from django.utils import timezone

router = Router()

@router.message(Command("start"))
async def start_handler(message: Message) -> None:
    user_id = message.from_user.id
    username = message.from_user.username or message.from_user.full_name
    first_name = message.from_user.first_name

    user_profile, created = await UserProfile.objects.aget_or_create(
        telegram_id=user_id,
        defaults={
            'username': username,
            'first_name': first_name,
            'is_active': True,
            'last_login': timezone.now()
        }
    )

    keyboard = main_menu_keyboard()

    if created:
        await message.answer(
            f"Привет, {first_name}! Добро пожаловать на аукцион. Мы зарегистрировали вас в системе.",
            reply_markup=keyboard
        )
    else:
        await message.answer(
            f"С возвращением, {first_name}! Рады снова вас видеть.",
            reply_markup=keyboard
        )