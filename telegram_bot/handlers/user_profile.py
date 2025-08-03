from aiogram import Router, F
from aiogram.types import CallbackQuery
from telegram_bot.keyboards.inline_kb import profile_keyboard, main_menu_keyboard, user_settings_keyboard
from users_app.models import UserProfile

router = Router()


@router.callback_query(F.data == "profile")
async def show_profile_handler(callback: CallbackQuery) -> None:
    user_id = callback.from_user.id
    user_profile = await UserProfile.objects.aget(telegram_id=user_id)

    can_autobid = user_profile.balance >= 500 or user_profile.success_payments_count >= 10

    profile_text = (
        f"<b>Личный кабинет</b>\n"
        f"Баланс: <b>{user_profile.balance} ₽</b>\n"
        f"Успешных оплат: {user_profile.success_payments_count}\n"
        f"Статус автоставок: {'✅ Доступно' if can_autobid else '❌ Недоступно'}"
    )

    await callback.message.edit_text(
        profile_text,
        reply_markup=profile_keyboard()
    )
    await callback.answer()


@router.callback_query(F.data == "main_menu")
async def back_to_main_menu_handler(callback: CallbackQuery) -> None:
    keyboard = main_menu_keyboard()
    await callback.message.edit_text(
        "Вы вернулись в главное меню. Выберите действие:",
        reply_markup=keyboard
    )
    await callback.answer()


@router.callback_query(F.data == "my_bids")
async def my_bids_handler(callback: CallbackQuery) -> None:
    await callback.answer("Здесь будет отображаться история ваших ставок.")


@router.callback_query(F.data == "settings")
async def settings_handler(callback: CallbackQuery) -> None:
    await callback.message.edit_text(
        "Настройки профиля:",
        reply_markup=user_settings_keyboard()
    )
    await callback.answer()


@router.callback_query(F.data == "toggle_autobid")
async def toggle_autobid(callback: CallbackQuery) -> None:
    # Здесь будет логика включения/выключения автоставок
    await callback.answer("Функционал автоставок будет реализован здесь.")