from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

def main_menu():
    keyboard = [
        [KeyboardButton(text="Проверить товар")],
        [KeyboardButton(text="Баланс")],
        [KeyboardButton(text="Пополнить баланс")]
    ]
    return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)


from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def confirm_payment_keyboard():
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="✅ Подтвердить", callback_data="confirm_payment"),
                InlineKeyboardButton(text="❌ Отмена", callback_data="cancel_payment")
            ]
        ]
    )
    return keyboard