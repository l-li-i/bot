from aiogram import Router, F
from aiogram.types import CallbackQuery
from telegram_bot.keyboards.inline_kb import profile_keyboard, main_menu_keyboard

router = Router()

@router.callback_query(F.data == "profile")
async def show_profile_handler(callback: CallbackQuery) -> None:
    keyboard = profile_keyboard()
    await callback.message.edit_text(
        "Это ваш личный кабинет. Выберите действие:",
        reply_markup=keyboard
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

@router.callback_query(F.data == "my_balance")
async def my_balance_handler(callback: CallbackQuery) -> None:
    # Здесь будет логика для получения баланса пользователя из джанго
    await callback.answer("Здесь будет отображаться ваш баланс.")

@router.callback_query(F.data == "my_bids")
async def my_bids_handler(callback: CallbackQuery) -> None:
    # Здесь будет некая логика для получения истории ставок пользователя
    await callback.answer("Здесь будет отображаться история ваших ставок.")

@router.callback_query(F.data == "settings")
async def settings_handler(callback: CallbackQuery) -> None:
    # Здесь будет логика для настроек пользователя
    await callback.answer("Здесь будут настройки вашего профиля.")