from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram import types
from aiogram import Bot


async def create_main_menu_keyboard():
    builder = InlineKeyboardBuilder()
    builder.add(types.InlineKeyboardButton(text="Каталог", callback_data="all_stuff"))
    builder.add(types.InlineKeyboardButton(text="Корзина", callback_data="basket"))
    builder.add(types.InlineKeyboardButton(text="Дополнительно", callback_data="more"))
    builder.adjust(1, 1, 1)
    return builder.as_markup()


async def create_additional_menu_keyboard():
    builder = InlineKeyboardBuilder()
    builder.add(types.InlineKeyboardButton(text="Вернуться в основное меню", callback_data="back_to_main_menu"))
    builder.add(types.InlineKeyboardButton(text="FAQ", callback_data="faq"))
    builder.add(types.InlineKeyboardButton(text="Возврат", callback_data="refund"))
    builder.add(types.InlineKeyboardButton(text="Контакты", callback_data="contacts"))
    builder.add(types.InlineKeyboardButton(text="Архив", callback_data="archive"))
    builder.add(types.InlineKeyboardButton(text="Оферта", url="https://polosabrand.com/oferta"))
    builder.add(types.InlineKeyboardButton(text="Политика конфиденциальности", url="https://polosabrand.com/privacy"))
    builder.adjust(1, 3, 3)
    return builder.as_markup()


async def set_users_main_menu(bot: Bot):
    main_menu_commands = [
        types.BotCommand(command="/menu", description="Главное меню"),
    ]
    await bot.set_my_commands(main_menu_commands)


async def set_admins_main_menu(bot: Bot):
    main_menu_commands = [
        types.BotCommand(command="/menu", description="Главное меню"),
        types.BotCommand(command="/panel", description="Панель администратора"),
        types.BotCommand(command="/cancel", description="Прервать оф"),
    ]
    await bot.set_my_commands(main_menu_commands)
