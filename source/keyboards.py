from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def get_main_menu_keyboard() -> InlineKeyboardMarkup:
    kb = [
        [InlineKeyboardButton(text="Сборка / Декомпиляция (/gamemodes)", callback_data="act_gamemodes")],
        [InlineKeyboardButton(text="Загрузка инклудов (/include)", callback_data="act_include")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=kb)

def get_done_include_keyboard() -> InlineKeyboardMarkup:
    kb = [
        [InlineKeyboardButton(text="Завершить загрузку", callback_data="finish_include")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=kb)
