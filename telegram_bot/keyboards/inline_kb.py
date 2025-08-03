from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def main_menu_keyboard():
    buttons = [
        [InlineKeyboardButton(text="Участвовать", callback_data="participate")],
        [InlineKeyboardButton(text="Мои лоты", callback_data="my_lots")],
        [InlineKeyboardButton(text="Личный кабинет", callback_data="profile")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def create_lot_keyboard(lot_id: int):
    buttons = [
        [InlineKeyboardButton(text="Участвовать", callback_data=f"participate_{lot_id}")],
        [InlineKeyboardButton(text="Подробности", callback_data=f"lot_details_{lot_id}")],
        [InlineKeyboardButton(text="Пожаловаться", callback_data=f"complain_lot_{lot_id}")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

async def create_bid_keyboard(lot_id: int):
    buttons = [
        [
            InlineKeyboardButton(text="+100 ₽", callback_data=f"bid_{lot_id}_100"),
            InlineKeyboardButton(text="+500 ₽", callback_data=f"bid_{lot_id}_500"),
            InlineKeyboardButton(text="+1000 ₽", callback_data=f"bid_{lot_id}_1000")
        ],
        [InlineKeyboardButton(text="Своя сумма", callback_data=f"bid_{lot_id}_custom")],
        [InlineKeyboardButton(text="Отмена", callback_data=f"cancel_bid_{lot_id}")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def profile_keyboard():
    buttons = [
        [InlineKeyboardButton(text="Мои ставки", callback_data="my_bids")],
        [InlineKeyboardButton(text="Настройки", callback_data="settings")],
        [InlineKeyboardButton(text="Назад", callback_data="main_menu")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def user_settings_keyboard():
    buttons = [
        [InlineKeyboardButton(text="Автоставки (выкл)", callback_data="toggle_autobid")],
        [InlineKeyboardButton(text="Назад", callback_data="profile")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def admin_panel_keyboard():
    buttons = [
        [InlineKeyboardButton(text="Создать лот", callback_data="create_lot")],
        [InlineKeyboardButton(text="Удалить лот", callback_data="delete_lot")],
        [InlineKeyboardButton(text="Просмотр финансов", callback_data="view_finances")],
        [InlineKeyboardButton(text="Выдать страйк", callback_data="issue_strike")],
        [InlineKeyboardButton(text="Назад в главное меню", callback_data="main_menu")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def back_keyboard():
    buttons = [
        [InlineKeyboardButton(text="Назад", callback_data="back_to_admin_menu")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def confirm_lot_keyboard():
    buttons = [
        [InlineKeyboardButton(text="✅ Подтвердить", callback_data="confirm_create_lot")],
        [InlineKeyboardButton(text="❌ Отменить", callback_data="cancel_create_lot")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)