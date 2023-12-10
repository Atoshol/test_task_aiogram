from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from typing import Final


MENU_KB_UK: Final = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text="Профіль"), KeyboardButton(text="Надіслати показники лічильника")],
    [KeyboardButton(text="Змінити мову")]
], one_time_keyboard=True)
MENU_KB_EN: Final = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text="Profile"), KeyboardButton(text="Send meter reading")],
    [KeyboardButton(text="Change Language")]
], one_time_keyboard=True)

METER_TYPE_KB_UK: Final = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text="Газ"), KeyboardButton(text="Вода"), KeyboardButton(text="Світло")]
])
METER_TYPE_KB_EN: Final = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text="Gas"), KeyboardButton(text="Water"), KeyboardButton(text="Light")]
])


REMOVE_KB: Final = ReplyKeyboardRemove()


def get_menu_kb(l_code):
    if l_code == "uk":
        return MENU_KB_UK
    return MENU_KB_EN


def get_type_meter_kb(l_code):
    if l_code == 'uk':
        return METER_TYPE_KB_UK
    return METER_TYPE_KB_EN

