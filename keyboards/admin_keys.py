from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram import types


def create_admin_keyboard():
    builder = InlineKeyboardBuilder()
    builder.add(types.InlineKeyboardButton(text="Добавить товар", callback_data="add_item"))
    builder.add(types.InlineKeyboardButton(text="Изменить информацию о товарах", callback_data="change_item"))
    builder.add(types.InlineKeyboardButton(text="Добавить администратора", callback_data="add_admin"))
    builder.add(types.InlineKeyboardButton(text="Забрать права администратора", callback_data="del_admin"))
    builder.adjust(2, 2)
    return builder
