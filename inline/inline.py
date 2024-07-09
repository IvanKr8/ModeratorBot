from aiogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup

RPSKeyboard = InlineKeyboardMarkup(inline_keyboard=[
    [
        InlineKeyboardButton(text="Камень", callback_data="rock"),
        InlineKeyboardButton(text="Ножницы", callback_data="scissors"),
        InlineKeyboardButton(text="Бумага", callback_data="paper")
    ]
])

RPSAgainKeyboard = InlineKeyboardMarkup(inline_keyboard=[
    [
        InlineKeyboardButton(text="Еще разок?", callback_data="play_rps_again")
    ]
])
