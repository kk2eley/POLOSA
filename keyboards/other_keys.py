from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram import types


async def create_faq_buttons():
    builder = InlineKeyboardBuilder()
    builder.add(types.InlineKeyboardButton(text="Доставка", callback_data="delivery"))
    builder.add(types.InlineKeyboardButton(text="Бронирование", callback_data="booking"))
    builder.add(types.InlineKeyboardButton(text="Возврат/Обмен", callback_data="refund_exchange"))
    builder.add(types.InlineKeyboardButton(text="Оплата", callback_data="payment"))
    builder.add(types.InlineKeyboardButton(text="Самовывоз", callback_data="self_delivery"))
    builder.add(types.InlineKeyboardButton(text="Подбор размера", callback_data="size_chosing"))
    builder.add(types.InlineKeyboardButton(text="Вернуться в дополнительное меню", callback_data="more"))
    builder.adjust(2, 2, 2, 1)
    return builder

async def back_faq_keys():
    builder = InlineKeyboardBuilder()
    builder.row(types.InlineKeyboardButton(text="Назад", callback_data="faq"))
    return builder.as_markup()

async def create_contacts_buttons():
    builder = InlineKeyboardBuilder()
    builder.row(types.InlineKeyboardButton(text="ВК", url="https://vk.com/polosabrand"))
    builder.row(types.InlineKeyboardButton(text="Telegram", url="t.me/polosa_brand"))
    builder.row(types.InlineKeyboardButton(text="Instagram", url="https://www.instagram.com/polosa.brand/"))
    builder.row(types.InlineKeyboardButton(text="Назад", callback_data="more"))
    return builder.as_markup()
