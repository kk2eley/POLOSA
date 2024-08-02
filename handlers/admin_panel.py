from aiogram import Router
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State, default_state
from aiogram import types
from keyboards import admin_keys
from aiogram import F
from aiogram.utils.keyboard import InlineKeyboardBuilder
from middlewares.album_saver import AlbumsMiddleware
import os
import json
import re

router = Router()
router.message.middleware(AlbumsMiddleware(wait_time_seconds=2))


class FSMAdmin(StatesGroup):
    # Часть с добавлением нового товара
    add_sku = State()
    add_main_photo = State()
    add_additional_photos = State()
    add_name = State()
    add_cost = State()
    add_description = State()
    add_sizes = State()
    add_available = State()
    save_data = State()


@router.message(Command("panel"))
async def cmd_create_admin_panel(message: types.Message, state: FSMContext, admins):
    await state.clear()
    if str(message.from_user.id) not in admins:
        return
    builder = admin_keys.create_admin_keyboard()
    await message.answer("Панель администратора", reply_markup=builder.as_markup())


@router.message(StateFilter(default_state), Command(commands=["cancel"]))
async def cmd_cancel_no_state(message: types.Message, state: FSMContext):
    await state.set_data({})
    await message.answer(
        text="Нечего отменять",
    )


@router.message(StateFilter(FSMAdmin) and Command(commands=["cancel"]))
async def cmd_cancel(message: types.Message, state: FSMContext):
    all_data = await state.get_data()
    for_remove = []
    if 'additional_photos' in all_data:
        for_remove = [item['unique_id'] for item in all_data['additional_photos']]
    if 'main_photo' in all_data:
        for_remove.append(all_data['main_photo']['unique_id'])
    for item in for_remove:
        file_path = f"photos/{item}.jpg"
        if os.path.exists(file_path):
            os.remove(file_path)
            print(f"Файл {file_path} был успешно удален.")
        else:
            print(f"Файл {file_path} не существует.")
    await state.clear()
    await message.answer(
        text="Действие отменено",
    )


@router.callback_query(StateFilter(default_state), F.data == "add_item")
async def cmd_add_item(callback: types.CallbackQuery, state: FSMContext):
    await state.set_state(FSMAdmin.add_sku)
    await callback.message.answer(text="Пришлите артикул")


@router.message(StateFilter(FSMAdmin.add_sku))
async def cmd_add_name(message: types.Message, state: FSMContext):
    await state.update_data(sku=message.text)
    await state.set_state(FSMAdmin.add_main_photo)
    await message.answer("Пришлите фото для превью")


@router.message(StateFilter(FSMAdmin.add_main_photo), F.photo)
async def cmd_add_main_photo(message: types.Message, state: FSMContext):
    photo_data = {"unique_id": message.photo[-1].file_unique_id,
                  "file_id": message.photo[-1].file_id,
                  "bot_id": message.bot.id}

    os.makedirs("photos", exist_ok=True)
    await message.bot.download(
        message.photo[-1],
        destination=f"photos/{message.photo[-1].file_unique_id}.jpg"
    )
    await state.update_data(main_photo=photo_data)
    await state.set_state(FSMAdmin.add_additional_photos)
    await message.answer("Пришлите дополнительные фото")


@router.message(StateFilter(FSMAdmin.add_main_photo))
async def cmd_add_main_photo(message: types.Message, state: FSMContext):
    await message.answer("Это не похоже на фото, попробуйте ещё раз")


@router.message(StateFilter(FSMAdmin.add_additional_photos), F.photo)
async def cmd_add_additional_photos(message: types.Message, state: FSMContext, **data):
    album_messages = data.get('album_messages', [])
    additional_photos_data = []
    for msg in album_messages:
        if msg.photo:
            file_id = msg.photo[-1].file_id
            unique_id = msg.photo[-1].file_unique_id
            bot_id = msg.bot.id

            os.makedirs("photos", exist_ok=True)
            await msg.bot.download(
                msg.photo[-1],
                destination=f"photos/{unique_id}.jpg"
            )

            photo_data = {
                "unique_id": unique_id,
                "file_id": file_id,
                "bot_id": bot_id
            }
            additional_photos_data.append(photo_data)

    await state.update_data(additional_photos=additional_photos_data)
    await message.answer("Фото получены и сохраняются. Пришлите название")
    await state.set_state(FSMAdmin.add_name)


@router.message(StateFilter(FSMAdmin.add_additional_photos))
async def cmd_add_main_photo(message: types.Message, state: FSMContext):
    await message.answer("Это не похоже на фото, попробуйте ещё раз")


@router.message(StateFilter(FSMAdmin.add_name))
async def cmd_add_name(message: types.Message, state: FSMContext):
    await state.update_data(name=message.text)
    await state.set_state(FSMAdmin.add_cost)
    await message.answer("Пришлите цену")


@router.message(StateFilter(FSMAdmin.add_cost))
async def cmd_add_name(message: types.Message, state: FSMContext):
    if message.text.replace(' ', '').isalnum():
        await state.update_data(cost=message.text.replace(' ', ''))
    else:
        await message.answer("Это не похоже на цену, введите только число без других символов")
        return
    await state.set_state(FSMAdmin.add_description)
    await message.answer("Пришлите описание с HTML форматированием, если необходимо. Можно использовать теги:\n"
                         "1. Тег <b>TEXT</b> Жирный текст\n"
                         "2. Тег <code>TEXT</code> Текст для лёгкого копирования (Моноширинный)\n"
                         "3. Тег <i>TEXT</i> Наклонённый текст\n"
                         "4. Тег <a href = 'https://qiwi.com/n/XACER'>TEXT</a> Ссылка в тексте\n"
                         "5. <u>TEXT</u> Подчёркнутый текст\n"
                         "6. <s>TEXT</s> Зачёркнутый текст\n")


@router.message(StateFilter(FSMAdmin.add_description))
async def cmd_add_name(message: types.Message, state: FSMContext):
    await state.update_data(description=message.text)
    await state.set_state(FSMAdmin.add_sizes)
    print(await state.get_data())
    await message.answer("Пришлите размеры в формате S M L XL")


@router.message(StateFilter(FSMAdmin.add_sizes))
async def cmd_add_name(message: types.Message, state: FSMContext):
    await state.update_data(sizes=re.split(" |  |\n", message.text.upper()))
    await state.set_state(FSMAdmin.add_available)
    builder = InlineKeyboardBuilder()
    builder.add(types.InlineKeyboardButton(text="В наличие", callback_data="is_available"))
    builder.add(types.InlineKeyboardButton(text="Нет в наличие", callback_data="not_available"))
    await message.answer(text="Товар имеется в наличие?", reply_markup=builder.as_markup())


@router.callback_query(StateFilter(FSMAdmin.add_available), F.data.in_({"is_available", "not_available"}))
async def cmd_is_available(callback: types.CallbackQuery, state: FSMContext):
    await state.update_data(in_stock=callback.data)
    await state.set_state(FSMAdmin.save_data)
    await callback.message.answer(
        str(await state.get_data()).replace('{', '{\n').replace('}', '}\n').replace(',', ',\n'))
    builder = InlineKeyboardBuilder()
    builder.add(types.InlineKeyboardButton(text="Сохранить", callback_data="save"))
    builder.add(types.InlineKeyboardButton(text="Отменить изменения", callback_data="back"))
    await callback.message.answer("Подтвердите, что хотите сохранить данные", reply_markup=builder.as_markup())


@router.message(StateFilter(FSMAdmin.add_available))
async def warning_not_available(message: types.Message, state: FSMContext):
    await message.answer(text="Пожалуйста, воспользуйтесь кнопками")


@router.callback_query(StateFilter(FSMAdmin.save_data), F.data == "save")
async def cmd_save_data(callback: types.CallbackQuery, state: FSMContext, redis):
    # Сериализация данных
    data = await state.get_data()
    serialized_data = json.dumps(data)

    # Сохранение сериализованных данных в Redis
    await redis.set(data['sku'], serialized_data)
    await redis.rpush('sku_list', data['sku'])


@router.callback_query(StateFilter(FSMAdmin.save_data), F.data == "back")
async def cmd_back_data(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.answer("Подтвердите, что хотите отменить изменения прислав комманду /cancel")
