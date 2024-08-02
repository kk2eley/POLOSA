from aiogram import Router
from aiogram.filters import Command
from aiogram import types
from aiogram.enums import ParseMode
from aiogram.utils.keyboard import InlineKeyboardBuilder
from keyboards import menu_keys
from aiogram import F
from keyboards.menu_keys import create_main_menu_keyboard, create_additional_menu_keyboard

router = Router()


@router.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer(
        text="Это бот бренда <b>ПОЛОСА</b>. Здесь вы можете посмотреть наши новинки, оформить заказ, и получить ответы на свои вопросы.",
        parse_mode=ParseMode.HTML,
        # reply_markup=builder.as_markup()
    )


@router.message(Command("menu"))
async def cmd_create_menu(message: types.Message):
    await message.answer(text="Меню", reply_markup=await create_main_menu_keyboard())


@router.callback_query(F.data == "more")
async def cmd_show_more_options(callback: types.CallbackQuery):
    await callback.message.edit_text(text="Дополнительное меню", reply_markup=await create_additional_menu_keyboard())


@router.callback_query(F.data == "back_to_main_menu")
async def cmd_back_to_main_menu(callback: types.CallbackQuery):
    await callback.message.edit_text(text="Меню", reply_markup=await create_main_menu_keyboard())
