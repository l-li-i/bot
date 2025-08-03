from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InputMediaPhoto, FSInputFile
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.filters.state import StateFilter
from users_app.models import UserProfile
from auction_app.models import Lot, LotImage, Bid
from telegram_bot.keyboards.inline_kb import admin_panel_keyboard, confirm_lot_keyboard, back_keyboard
from django.utils import timezone
from datetime import datetime
import asyncio
import os
import io

router = Router()


class CreateLot(StatesGroup):
    waiting_for_title = State()
    waiting_for_description = State()
    waiting_for_start_price = State()
    waiting_for_end_time = State()
    waiting_for_photos = State()
    waiting_for_confirmation = State()


@router.message(F.text == "/admin")
async def show_admin_panel(message: Message) -> None:
    """Проверяет права и показывает админ-панель."""
    user_id = message.from_user.id
    try:
        user_profile = await UserProfile.objects.aget(telegram_id=user_id)
        # Проверяем права администратора напрямую через поле is_admin в UserProfile
        if not user_profile.is_admin:
            await message.answer("У вас нет прав для доступа к админ-панели.")
            return

        await message.answer("Добро пожаловать в админ-панель.", reply_markup=admin_panel_keyboard())
    except UserProfile.DoesNotExist:
        await message.answer("Вы не зарегистрированы.")


@router.callback_query(F.data == "create_lot")
async def start_lot_creation_from_button(callback: CallbackQuery, state: FSMContext) -> None:
    await state.set_state(CreateLot.waiting_for_title)
    await callback.message.edit_text("Отлично! Давайте создадим новый лот. Введите его название:",
                                     reply_markup=back_keyboard())


@router.callback_query(F.data == "back_to_admin_menu")
async def back_to_admin_menu(callback: CallbackQuery, state: FSMContext) -> None:
    """Возвращает в админ-панель."""
    await state.clear()
    await callback.message.edit_text("Вы вернулись в админ-панель.", reply_markup=admin_panel_keyboard())


@router.message(F.text == "Назад", StateFilter("*"))
async def back_button_handler(message: Message, state: FSMContext) -> None:
    """Обрабатывает текстовую кнопку "Назад" """
    await state.clear()
    await message.answer("Создание лота отменено.")


@router.message(CreateLot.waiting_for_title)
async def process_title(message: Message, state: FSMContext) -> None:
    await state.update_data(title=message.text)
    await state.set_state(CreateLot.waiting_for_description)
    await message.answer("Теперь введите подробное описание лота:", reply_markup=back_keyboard())


@router.message(CreateLot.waiting_for_description)
async def process_description(message: Message, state: FSMContext) -> None:
    await state.update_data(description=message.text)
    await state.set_state(CreateLot.waiting_for_start_price)
    await message.answer("Введите стартовую цену лота (только число):", reply_markup=back_keyboard())


@router.message(CreateLot.waiting_for_start_price, F.text.regexp(r'^\d+(\.\d{1,2})?$'))
async def process_start_price(message: Message, state: FSMContext) -> None:
    await state.update_data(start_price=float(message.text))
    await state.set_state(CreateLot.waiting_for_end_time)
    await message.answer("Введите время окончания торгов в формате ГГГГ-ММ-ДД ЧЧ:ММ (например, 2025-12-31 15:00):",
                         reply_markup=back_keyboard())


@router.message(CreateLot.waiting_for_start_price)
async def process_start_price_invalid(message: Message) -> None:
    await message.answer("Пожалуйста, введите корректную числовую сумму.")


@router.message(CreateLot.waiting_for_end_time)
async def process_end_time(message: Message, state: FSMContext) -> None:
    try:
        end_time = datetime.strptime(message.text, '%Y-%m-%d %H:%M')
        if end_time < datetime.now():
            await message.answer("Время окончания торгов не может быть в прошлом. Попробуйте еще раз.")
            return

        await state.update_data(end_time=end_time.isoformat())
        await state.set_state(CreateLot.waiting_for_photos)
        await message.answer("Отправьте фотографии лота (можно несколько, одним сообщением):",
                             reply_markup=back_keyboard())
    except ValueError:
        await message.answer("Неверный формат даты. Пожалуйста, используйте формат ГГГГ-ММ-ДД ЧЧ:ММ.")


@router.message(CreateLot.waiting_for_photos, F.photo)
async def process_photos(message: Message, state: FSMContext) -> None:
    photos = message.photo
    if 'photos' not in await state.get_data():
        await state.update_data(photos=[])

    data = await state.get_data()
    data['photos'].extend([photo.file_id for photo in photos])
    await state.set_data(data)

    await state.set_state(CreateLot.waiting_for_confirmation)

    lot_data = await state.get_data()
    confirmation_text = (
        f"<b>Проверьте данные лота:</b>\n\n"
        f"<b>Название:</b> {lot_data['title']}\n"
        f"<b>Описание:</b> {lot_data['description']}\n"
        f"<b>Стартовая цена:</b> {lot_data['start_price']} ₽\n"
        f"<b>Окончание торгов:</b> {lot_data['end_time']}\n"
        f"<b>Фото:</b> {len(lot_data['photos'])} шт."
    )

    await message.answer(confirmation_text, reply_markup=confirm_lot_keyboard())


@router.callback_query(F.data == "confirm_create_lot", StateFilter(CreateLot.waiting_for_confirmation))
async def finalize_lot_creation(callback: CallbackQuery, state: FSMContext) -> None:
    data = await state.get_data()
    user_id = callback.from_user.id
    try:
        user_profile = await UserProfile.objects.aget(telegram_id=user_id)
        end_time_dt = datetime.fromisoformat(data['end_time'])

        lot = await Lot.objects.acreate(
            title=data['title'],
            description=data['description'],
            start_price=data['start_price'],
            current_price=data['start_price'],
            start_time=timezone.now(),
            end_time=end_time_dt,
            seller=user_profile,
            telegram_link=f'https://t.me/{user_profile.username}' if user_profile.username else None,
            status='in_buffer',
        )

        for photo_file_id in data['photos']:
            await LotImage.objects.acreate(
                lot=lot,
                file_id=photo_file_id
            )

        support_group_id = -1001234567891
        await callback.bot.send_message(
            chat_id=support_group_id,
            text=f"✅ <b>НОВАЯ ЗАЯВКА НА ЛОТ</b>: {lot.title}\n\n"
                 f"От администратора: {user_profile.username or user_profile.telegram_id}\n"
                 f"<i>Лот ожидает одобрения в админ-панели.</i>"
        )

        await callback.message.edit_text("Заявка на лот успешно создана и отправлена на модерацию!")

    except Exception as e:
        await callback.message.edit_text(f"Произошла ошибка при сохранении лота: {e}")

    finally:
        await state.clear()


@router.callback_query(F.data == "cancel_create_lot", StateFilter(CreateLot.waiting_for_confirmation))
async def cancel_lot_creation(callback: CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    await callback.message.edit_text("Создание лота отменено.")


# хендлеры для админов
@router.callback_query(F.data == "view_history")
async def view_history(callback: CallbackQuery) -> None:
    await callback.answer("Здесь будет история торгов.")


@router.callback_query(F.data == "view_finances")
async def view_finances(callback: CallbackQuery) -> None:
    await callback.answer("Здесь будет просмотр финансов.")


@router.callback_query(F.data == "issue_strike")
async def issue_strike(callback: CallbackQuery) -> None:
    await callback.answer("Здесь будет система выдачи страйков.")