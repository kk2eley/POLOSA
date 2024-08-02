import logging

from aiogram import Router
from aiogram import types
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.filters.command import Command
from aiogram import F
from aiogram.types import FSInputFile, URLInputFile, BufferedInputFile
from aiogram.enums import ParseMode
from aiogram.filters.callback_data import CallbackData
from aiogram.utils.media_group import MediaGroupBuilder
import json
from aiogram.fsm.context import FSMContext


class StuffCallbackFactory(CallbackData, prefix="more_info"):
    sku: str | int
    size: str
    type: str


router = Router()
logger = logging.getLogger(__name__)


# Присылает сообщения со всеми товарами с подписью "подробнее"
@router.callback_query(F.data == "all_stuff")
async def cmd_catalog(callback: types.CallbackQuery, redis, state: FSMContext):
    sku_list = await redis.lrange('sku_list', 0, -1)
    catalog_messages = []
    for sku, i in zip(sku_list, range(1, len(sku_list) + 1)):
        builder = InlineKeyboardBuilder()
        builder.add(types.InlineKeyboardButton(
            text="Подробнее",
            callback_data=StuffCallbackFactory(sku=sku, size="no_size", type="no_type").pack())
        )
        if i == len(sku_list):
            builder.add(types.InlineKeyboardButton(
                text="Назад к меню",
                callback_data="back_to_the_menu"
            ))
            builder.adjust(1, 1)
        serialized_data = await redis.get(sku)
        if not serialized_data:
            break
        # Десериализация данных
        data = json.loads(serialized_data)
        if not data['in_stock'] == 'is_available':
            break
        if data['main_photo']['bot_id'] == callback.message.bot.id and data['main_photo']['file_id'] != '':
            # Отправка фото по file_id
            file = data['main_photo']['file_id']
        else:
            file = types.FSInputFile(f"photos/{data['main_photo']['unique_id']}.jpg")
        catalog_message = await callback.message.answer_photo(
            photo=file,
            caption=f"<b>{data['name']}</b>\n"
                    f"<i>{data['cost']} RUB</i>\n",
            parse_mode=ParseMode.HTML,
            reply_markup=builder.as_markup()
        )
        catalog_messages.append({"chat_id": catalog_message.chat.id,
                                 "message_id": catalog_message.message_id})
    logger.debug(f'catalog_message: {catalog_messages}')
    logger.debug(f'catalog_messages: {catalog_messages}')
    await state.update_data(catalog_messages=catalog_messages)
    logger.debug('state updated')


@router.callback_query(F.data == "back_to_the_menu")
async def cmd_back_to_the_catalog(callback: types.CallbackQuery, state: FSMContext):
    messages = (await state.get_data())["catalog_messages"]
    for message in messages:
        await callback.bot.delete_message(chat_id=message['chat_id'], message_id=message['message_id'])


@router.callback_query(StuffCallbackFactory.filter(F.type == "resize"))
async def cmd_resize(callback: types.CallbackQuery, callback_data: StuffCallbackFactory, redis):
    sku = callback_data.sku
    serialized_data = await redis.get(sku)
    if not serialized_data:
        return
    # Десериализация данных
    data = json.loads(serialized_data)
    builder = InlineKeyboardBuilder()
    for size in data['sizes']:
        builder.add(types.InlineKeyboardButton(text=size,
                                               callback_data=StuffCallbackFactory(sku=sku, size=size,
                                                                                  type="no_type").pack()))
    builder.add(
        types.InlineKeyboardButton(text="Назад к каталогу",
                                   callback_data=StuffCallbackFactory(sku=callback_data.sku,
                                                                      size="no_size",
                                                                      type="back_to_the_catalog").pack()))
    builder.adjust(len(data['sizes']), 1)

    await callback.message.edit_reply_markup(reply_markup=builder.as_markup())


@router.callback_query(StuffCallbackFactory.filter(F.size == "no_size"),
                       StuffCallbackFactory.filter(F.type == "no_type"))
async def cmd_show_info(callback: types.CallbackQuery, callback_data: StuffCallbackFactory, redis, state: FSMContext):
    sku = callback_data.sku
    serialized_data = await redis.get(sku)
    if not serialized_data:
        return
    # Десериализация данных
    data = json.loads(serialized_data)

    album_builder = MediaGroupBuilder(caption=f"<b>{data['name']}</b>\n"
                                              f"<i>{data['cost']} RUB</i>\n")
    for item in data['additional_photos']:
        if item['bot_id'] == callback.message.bot.id and item['file_id'] != '':
            # Отправка фото по file_id
            file = item['file_id']
        else:
            file = types.FSInputFile(f"photos/{item['unique_id']}.jpg")
        album_builder.add(type="photo", media=file)

    album_messages = await callback.message.answer_media_group(
        # Не забудьте вызвать build()
        media=album_builder.build()
    )
    builder = InlineKeyboardBuilder()
    for size in data['sizes']:
        builder.add(types.InlineKeyboardButton(text=size,
                                               callback_data=StuffCallbackFactory(sku=sku, size=size,
                                                                                  type="no_type").pack()))
    builder.add(
        types.InlineKeyboardButton(text="Назад к каталогу", callback_data=StuffCallbackFactory(sku=callback_data.sku,
                                                                                               size="no_size",
                                                                                               type="back_to_the_catalog").pack()))
    builder.adjust(len(data['sizes']), 1)
    inline_message = await callback.message.answer(text=data['description'].replace('\\n', '\n'),
                                                   reply_markup=builder.as_markup())

    messages_info = {
        sku: [{"chat_id": album_message.chat.id,
               "message_id": album_message.message_id} for album_message in album_messages] + [
                 {"chat_id": inline_message.chat.id,
                  "message_id": inline_message.message_id}]
    }
    await state.update_data(more_info_messages=messages_info)


@router.callback_query(StuffCallbackFactory.filter(F.type == "back_to_the_catalog"))
async def cmd_back_to_the_catalog(callback: CallbackData, callback_data: StuffCallbackFactory, state: FSMContext):
    messages = (await state.get_data())["more_info_messages"][callback_data.sku]
    for message in messages:
        await callback.bot.delete_message(chat_id=message['chat_id'], message_id=message['message_id'])


@router.callback_query(StuffCallbackFactory.filter(F.type != "picked"))
async def cmd_add_to_basket(callback: types.CallbackQuery, callback_data: StuffCallbackFactory, state: FSMContext):
    builder = InlineKeyboardBuilder()
    builder.add(types.InlineKeyboardButton(text="Добавить в корзину",
                                           callback_data=StuffCallbackFactory(sku=callback_data.sku,
                                                                              size=callback_data.size,
                                                                              type="picked").pack()))
    builder.add(
        types.InlineKeyboardButton(text="Изменить размер", callback_data=StuffCallbackFactory(sku=callback_data.sku,
                                                                                              size="no_size",
                                                                                              type="resize").pack()))
    builder.add(
        types.InlineKeyboardButton(text="Назад к каталогу", callback_data=StuffCallbackFactory(sku=callback_data.sku,
                                                                                               size="no_size",
                                                                                               type="back_to_the_catalog").pack()))
    builder.adjust(2, 1)
    await callback.message.edit_reply_markup(reply_markup=builder.as_markup())


@router.callback_query(StuffCallbackFactory.filter(F.type == "picked"))
async def cmd_adding_to_basket(callback: types.CallbackQuery, callback_data: StuffCallbackFactory, redis, state: FSMContext):
    serialized_data = await redis.hget("users_baskets", callback.from_user.id)
    if serialized_data:
        data = json.loads(serialized_data)
        if callback_data.sku in data:
            data[callback_data.sku][callback_data.size] = data[callback_data.sku].get(callback_data.size, 0) + 1
        else:
            data[callback_data.sku] = {callback_data.size: 1}
    else:
        data = {callback_data.sku: {callback_data.size: 1}}
    serialized_data = json.dumps(data)
    await redis.hset('users_baskets', callback.from_user.id, serialized_data)
    await callback.message.edit_reply_markup()
    await callback.answer(text=f"Товар добавлен в корзину")
    messages = (await state.get_data())["more_info_messages"][callback_data.sku]
    for message in messages:
        await callback.bot.delete_message(chat_id=message['chat_id'], message_id=message['message_id'])

