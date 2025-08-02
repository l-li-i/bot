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
        [InlineKeyboardButton(text="Мой баланс", callback_data="my_balance")],
        [InlineKeyboardButton(text="Мои ставки", callback_data="my_bids")],
        [InlineKeyboardButton(text="Настройки", callback_data="settings")],
        [InlineKeyboardButton(text="Назад", callback_data="main_menu")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)