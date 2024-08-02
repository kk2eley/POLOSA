from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder
from aiogram.types import InlineKeyboardButton, KeyboardButton


# async def create_order_confirmation_keyboard():
#     builder = InlineKeyboardBuilder()
#     builder.row(InlineKeyboardButton(text="Подтвердить", callback_data=), )


async def create_location_button():
    builder = ReplyKeyboardBuilder()
    location_button = KeyboardButton(text="Прислать геолокацию", request_location=True)
    builder.add(location_button)
    return builder.as_markup(resize_keyboard=True)


async def create_delivery_buttons():
    builder = ReplyKeyboardBuilder()
    builder.row(KeyboardButton(text="СДЭК Пункт Выдачи от 6 дней от 386,25 RUB"))
    builder.row(KeyboardButton(text="СДЭК Курьерот 6 дней от 576,25 RUB"))
    builder.row(KeyboardButton(text="Доставка по Миру от 14 дней 3 000 RUB"))
    return builder.as_markup()
