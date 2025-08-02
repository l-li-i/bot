from aiogram import Router, F
from aiogram.types import CallbackQuery, Message, InputMediaPhoto, FSInputFile
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from auction_app.models import Lot, LotImage, Bid
from users_app.models import UserProfile
from telegram_bot.keyboards.inline_kb import create_lot_keyboard, create_bid_keyboard
from django.db.models import F as D_F
from django.utils import timezone
import asyncio
from support_app.models import Complaint

router = Router()

# Состояния для FSM (Finite State Machine)
class BidState(StatesGroup):
    waiting_for_bid_amount = State()

class ComplaintState(StatesGroup):
    waiting_for_complaint_text = State()

@router.callback_query(F.data == "participate")
async def show_active_lots_handler(callback: CallbackQuery):
    active_lots = await Lot.objects.filter(status='active', end_time__gt=timezone.now()).select_related('seller').prefetch_related('images').order_by('end_time')

    if not active_lots:
        await callback.message.edit_text("Сейчас нет активных лотов. Загляните позже!")
        await callback.answer()
        return

    for lot in active_lots:
        images = await lot.images.all()
        media_group = []
        caption_text = (
            f"✨ <b>АКТИВНЫЙ ЛОТ</b> ✨\n\n"
            f"<b>{lot.title}</b>\n"
            f"Текущая цена: {lot.current_price} ₽\n"
            f"Продавец: <a href='{lot.telegram_link}'>{lot.seller.username}</a>\n"
            f"Окончание: {lot.end_time.strftime('%d.%m.%Y %H:%M')}\n\n"
        )
        keyboard = create_lot_keyboard(lot.id)

        # Отправляем изображения лота
        if images:
            for i, img in enumerate(images):
                image_path = img.image.path
                media_group.append(InputMediaPhoto(media=FSInputFile(image_path), caption=caption_text if i == 0 else None))
            await callback.message.answer_media_group(media=media_group)
        else:
            await callback.message.answer(caption_text)

        await callback.message.answer("Выберите действие:", reply_markup=keyboard)

    await callback.answer()

@router.callback_query(F.data.startswith("participate_"))
async def participate_callback_handler(callback: CallbackQuery, state: FSMContext) -> None:
    """
    Обрабатывает нажатие кнопки "Участвовать".
    Перенаправляет пользователя в личное сообщение с ботом для ставки.
    """
    lot_id = int(callback.data.split("_")[1])
    user_id = callback.from_user.id

    try:
        lot = await Lot.objects.aget(id=lot_id, status='active')
        user_profile = await UserProfile.objects.aget(telegram_id=user_id)
    except (Lot.DoesNotExist, UserProfile.DoesNotExist):
        await callback.answer("Лот не найден или вы не зарегистрированы.", show_alert=True)
        return

    await callback.bot.send_message(
        chat_id=user_id,
        text=f"Вы хотите сделать ставку на лот: <b>{lot.title}</b>\n"
             f"Текущая цена: <b>{lot.current_price} ₽</b>\n"
             f"Минимальная ставка: <b>{lot.current_price + 1} ₽</b> (или больше)\n\n"
             f"Выберите сумму или введите свою:",
        reply_markup=await create_bid_keyboard(lot_id)
    )
    await callback.answer("Перенаправляю вас для ставки в личное сообщение с ботом.", show_alert=True)

@router.callback_query(F.data.startswith("bid_"))
async def bid_preset_callback_handler(callback: CallbackQuery, state: FSMContext) -> None:
    """
    Обрабатывает нажатие на предустановленные суммы ставок.
    """
    parts = callback.data.split("_")
    lot_id = int(parts[1])
    user_id = callback.from_user.id

    try:
        lot = await Lot.objects.aget(id=lot_id, status='active')
        user_profile = await UserProfile.objects.aget(telegram_id=user_id)
    except (Lot.DoesNotExist, UserProfile.DoesNotExist):
        await callback.answer("Лот не найден или вы не зарегистрированы.", show_alert=True)
        return

    if lot.end_time < timezone.now():
        await callback.answer("Торги по этому лоту уже завершены.", show_alert=True)
        return

    if parts[2] == "custom":
        await state.set_state(BidState.waiting_for_bid_amount)
        await state.update_data(lot_id=lot_id)
        await callback.message.answer("Введите желаемую сумму ставки:")
        await callback.answer()
        return

    bid_amount = float(parts[2])

    if bid_amount <= lot.current_price:
        await callback.answer(f"Ваша ставка ({bid_amount} ₽) должна быть больше текущей цены ({lot.current_price} ₽).", show_alert=True)
        return

    async with asyncio.Lock():
        try:
            lot = await Lot.objects.select_for_update().aget(id=lot_id)
            if bid_amount <= lot.current_price:
                await callback.answer(f"Кто-то уже сделал ставку выше вашей. Текущая цена: {lot.current_price} ₽", show_alert=True)
                return

            lot.current_price = bid_amount
            await lot.asave(update_fields=['current_price'])

            await Bid.objects.acreate(
                lot=lot,
                bidder=user_profile,
                amount=bid_amount
            )
            await callback.message.answer(f"Ваша ставка <b>{bid_amount} ₽</b> на лот <b>{lot.title}</b> принята!")
            await callback.answer("Ставка успешно сделана!")

            await callback.bot.send_message(
                chat_id="-1001234567890", # Замените на ID вашего канала аукциона
                text=f"🔥 Новая ставка на лот <b>{lot.title}</b>!\n"
                     f"Текущая цена: <b>{lot.current_price} ₽</b>\n"
                     f"Сделана пользователем: {user_profile.username or user_profile.telegram_id}"
            )

        except Exception as e:
            await callback.answer(f"Произошла ошибка при обработке ставки: {e}", show_alert=True)
            print(f"Ошибка при ставке: {e}")

@router.message(BidState.waiting_for_bid_amount, F.text.regexp(r'^\d+(\.\d{1,2})?$'))
async def process_custom_bid(message: Message, state: FSMContext) -> None:
    """
    Обрабатывает пользовательский ввод суммы ставки.
    """
    data = await state.get_data()
    lot_id = data['lot_id']
    user_id = message.from_user.id
    bid_amount = float(message.text)

    try:
        lot = await Lot.objects.aget(id=lot_id, status='active')
        user_profile = await UserProfile.objects.aget(telegram_id=user_id)
    except (Lot.DoesNotExist, UserProfile.DoesNotExist):
        await message.answer("Лот не найден или вы не зарегистрированы.")
        await state.clear()
        return

    if lot.end_time < timezone.now():
        await message.answer("Торги по этому лоту уже завершены.")
        await state.clear()
        return

    if bid_amount <= lot.current_price:
        await message.answer(f"Ваша ставка ({bid_amount} ₽) должна быть больше текущей цены ({lot.current_price} ₽). Попробуйте еще раз или отмените.",
                             reply_markup=await create_bid_keyboard(lot_id))
        return

    async with asyncio.Lock():
        try:
            lot = await Lot.objects.select_for_update().aget(id=lot_id)
            if bid_amount <= lot.current_price:
                await message.answer(f"Кто-то уже сделал ставку выше вашей. Текущая цена: {lot.current_price} ₽",
                                     reply_markup=await create_bid_keyboard(lot_id))
                await state.clear()
                return

            lot.current_price = bid_amount
            await lot.asave(update_fields=['current_price'])

            await Bid.objects.acreate(
                lot=lot,
                bidder=user_profile,
                amount=bid_amount
            )

            await message.answer(f"Ваша ставка <b>{bid_amount} ₽</b> на лот <b>{lot.title}</b> принята!")
            await state.clear()

            await message.bot.send_message(
                chat_id="-1001234567890", # Замените на ID вашего канала аукциона
                text=f"🔥 Новая ставка на лот <b>{lot.title}</b>!\n"
                     f"Текущая цена: <b>{lot.current_price} ₽</b>\n"
                     f"Сделана пользователем: {user_profile.username or user_profile.telegram_id}"
            )

        except Exception as e:
            await message.answer(f"Произошла ошибка при обработке ставки: {e}")
            print(f"Ошибка при пользовательской ставке: {e}")
            await state.clear()

@router.message(BidState.waiting_for_bid_amount)
async def process_custom_bid_invalid(message: Message) -> None:
    """
    Обрабатывает неверный ввод суммы ставки.
    """
    await message.answer("Пожалуйста, введите корректную числовую сумму ставки (например, 1500.00).")

@router.callback_query(F.data.startswith("cancel_bid_"))
async def cancel_bid_handler(callback: CallbackQuery, state: FSMContext) -> None:
    """
    Отменяет процесс ставки.
    """
    await state.clear()
    await callback.message.answer("Процесс ставки отменен.")
    await callback.answer()

@router.callback_query(F.data.startswith("lot_details_"))
async def lot_details_handler(callback: CallbackQuery) -> None:
    """
    Отправляет подробное описание лота и приложенные файлы.
    """
    lot_id = int(callback.data.split("_")[2])
    try:
        lot = await Lot.objects.aget(id=lot_id)
        images = await lot.images.all()
    except Lot.DoesNotExist:
        await callback.answer("Лот не найден.", show_alert=True)
        return

    description_text = (
        f"<b>Лот: {lot.title}</b>\n\n"
        f"<b>Описание:</b> {lot.description}\n"
        f"<b>Стартовая цена:</b> {lot.start_price} ₽\n"
        f"<b>Текущая цена:</b> {lot.current_price} ₽\n"
        f"<b>Продавец:</b> <a href='{lot.telegram_link}'>{lot.seller.username}</a>\n"
        f"<b>Геолокация:</b> {lot.location or 'Не указана'}\n"
        f"<b>Начало торгов:</b> {lot.start_time.strftime('%d.%m.%Y %H:%M')}\n"
        f"<b>Окончание торгов:</b> {lot.end_time.strftime('%d.%m.%Y %H:%M')}\n"
    )

    media_group = []
    for i, img in enumerate(images):
        image_path = img.image.path
        media_group.append(InputMediaPhoto(media=FSInputFile(image_path), caption=description_text if i == 0 else None))

    if media_group:
        await callback.message.answer_media_group(media=media_group)
    else:
        await callback.message.answer(description_text)

    await callback.answer()

@router.callback_query(F.data.startswith("complain_lot_"))
async def complain_lot_handler(callback: CallbackQuery, state: FSMContext) -> None:
    """
    Обрабатывает жалобу на лот.
    """
    lot_id = int(callback.data.split("_")[2])
    user_id = callback.from_user.id

    try:
        lot = await Lot.objects.aget(id=lot_id)
        reporter = await UserProfile.objects.aget(telegram_id=user_id)
    except (Lot.DoesNotExist, UserProfile.DoesNotExist):
        await callback.answer("Ошибка: лот или пользователь не найдены.", show_alert=True)
        return

    await state.set_state(ComplaintState.waiting_for_complaint_text)
    await state.update_data(lot_id=lot_id, reporter_id=reporter.id, target_admin_id=lot.seller.id)
    await callback.message.answer("Пожалуйста, опишите вашу жалобу на лот:")
    await callback.answer()

@router.message(ComplaintState.waiting_for_complaint_text)
async def process_complaint_text(message: Message, state: FSMContext) -> None:
    """
    Сохраняет жалобу в БД и отправляет в систему поддержки.
    """
    data = await state.get_data()
    lot_id = data['lot_id']
    reporter_id = data['reporter_id']
    target_admin_id = data['target_admin_id']
    complaint_text = message.text

    try:
        reporter = await UserProfile.objects.aget(id=reporter_id)
        target_admin = await UserProfile.objects.aget(id=target_admin_id)
        lot = await Lot.objects.aget(id=lot_id)

        await Complaint.objects.acreate(
            reporter=reporter,
            target_admin=target_admin,
            message=complaint_text,
        )

        support_group_id = -1001234567891 # Замените на ID чата вашей группы поддержки
        await message.bot.send_message(
            chat_id=support_group_id,
            text=f"🚨 <b>НОВАЯ ЖАЛОБА!</b> 🚨\n\n"
                 f"От: {reporter.username or reporter.telegram_id}\n"
                 f"На администратора: {target_admin.username or target_admin.telegram_id}\n"
                 f"Лот: {lot.title}\n"
                 f"Сообщение: {complaint_text}\n\n"
                 f"<i>Проверьте в админ-панели.</i>"
        )
        await message.answer("Ваша жалоба успешно отправлена в систему поддержки. Спасибо за ваше обращение!")
    except Exception as e:
        await message.answer(f"Произошла ошибка при отправке жалобы: {e}")
        print(f"Ошибка при сохранении жалобы: {e}")
    finally:
        await state.clear()