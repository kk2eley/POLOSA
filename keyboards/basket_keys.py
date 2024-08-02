from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram import types
from aiogram.filters.callback_data import CallbackData


class BasketCallbackFactory(CallbackData, prefix="basket"):
    sku: str
    size: str
    type: str




async def create_value_buttons(sku: str, size: str, quantity: int):
    builder = InlineKeyboardBuilder()
    builder.add(types.InlineKeyboardButton(text="-",
                                           callback_data=BasketCallbackFactory(sku=sku, size=size, type="-1").pack()))
    builder.add(types.InlineKeyboardButton(text=f"{quantity}",
                                           callback_data="quantity"))
    builder.add(types.InlineKeyboardButton(text="+",
                                           callback_data=BasketCallbackFactory(sku=sku, size=size, type="+1").pack()))
    builder.add(types.InlineKeyboardButton(text="Убрать из корзины",
                                           callback_data=BasketCallbackFactory(sku=sku, size=size,
                                                                               type="delete").pack()))
    builder.adjust(3, 1)
    return builder


async def create_buy_button():
    builder = InlineKeyboardBuilder()
    builder.add(types.InlineKeyboardButton(text="Оформить заказ", callback_data="create_order"))
    return builder
