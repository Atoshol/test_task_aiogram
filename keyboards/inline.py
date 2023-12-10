from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from typing import Final

language_kb: Final = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="Українська", callback_data="uk"),
         InlineKeyboardButton(text="English", callback_data="en"),]
    ]
)

profile_data_uk: Final = InlineKeyboardMarkup(inline_keyboard=[
    [
        InlineKeyboardButton(text="Адреса", callback_data="address"),
        InlineKeyboardButton(text="Особовий рахунок", callback_data="account_id")
    ],
    [
        InlineKeyboardButton(text="Повернутись в меню", callback_data="go_to_menu"),
    ]
])

profile_data_en: Final = InlineKeyboardMarkup(inline_keyboard=[
    [
        InlineKeyboardButton(text="Address", callback_data="address"),
        InlineKeyboardButton(text="Account ID", callback_data="account_id")],
    [
        InlineKeyboardButton(text="Back to Menu", callback_data="go_to_menu"),
    ]
])


def get_profile_data_kb(l_code):
    if l_code == 'uk':
        return profile_data_uk
    return profile_data_en

