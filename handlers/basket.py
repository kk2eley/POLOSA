from aiogram import Router
from aiogram import types
from aiogram.filters import Command
from aiogram import F
import json
from keyboards.basket_keys import create_value_buttons, BasketCallbackFactory, create_buy_button
import logging
from data_operations import load_data, dump_data, load_basket, dump_basket
from aiogram.fsm.context import FSMContext

router = Router()
logger = logging.getLogger(__name__)


@router.callback_query(F.data == "basket")
async def cmd_basket(callback: types.CallbackQuery, redis, state: FSMContext):
    basket = await load_basket(redis, callback.from_user.id)
    logger.debug(f"Basket value: {basket}")

    total = 0
    basket_messages = []
    for sku, sub_basket in basket.items():
        logger.debug(f"Sku: {sku}, sub_basket: {sub_basket}")
        for size, quantity in sub_basket.items():
            logger.debug(f"Size: {size}, quantity: {quantity}")
            data = await load_data(redis, sku)
            logger.debug(f"Data value: {data}")
            cost = int(data["cost"])
            interim = cost * quantity
            total += interim
            logger.debug(f"total: {total}")
            logger.debug(f"interim: {interim} = {cost} * {quantity}")
            if data['main_photo']['bot_id'] == callback.message.bot.id and data['main_photo']['file_id'] != '':
                # Отправка фото по file_id
                file = data['main_photo']['file_id']
                logger.debug(f"Using photo id: {file}")
            else:
                file = types.FSInputFile(f"photos/{data['main_photo']['unique_id']}.jpg")
                logger.debug(f"Using file: {file}")
            basket_message = await callback.message.answer_photo(
                photo=file,
                caption=f"<b>{data['name']} {size}</b>\n"
                        f"<i>Цена: {cost} RUB</i>\n"
                        f"<i>Итого: <b>{interim} RUB</b></i>\n",
                reply_markup=(await create_value_buttons(sku, size, quantity)).as_markup()
            )
            basket_messages.append({"chat_id": basket_message.chat.id,
                                    "message_id": basket_message.message_id})
            await state.update_data(basket_messages=basket_messages)

        logger.debug("Message sent")
    if total == 0:
        total_message = await callback.message.answer(text=f"Корзина пуста")
    else:
        total_message = await callback.message.answer(text=f"Всего в корзине на: <i>{total} RUB</i>",
                                                      reply_markup=(await create_buy_button()).as_markup())
    await state.update_data(total_message={'message_id': total_message.message_id, 'chat_id': total_message.chat.id})
    logger.debug(f"Absorbed total_message: {total_message}")


@router.callback_query(BasketCallbackFactory.filter())
async def cmd_sub_one(callback: types.CallbackQuery, callback_data: BasketCallbackFactory, redis, state: FSMContext):
    basket = await load_basket(redis, callback.from_user.id)
    logger.debug(f"Basket value: {basket}")

    sku = callback_data.sku
    size = callback_data.size
    logger.debug(f"sku: {sku}, size: {size}")

    data = await load_data(redis, sku)
    cost = int(data['cost'])
    logger.debug(f"cost: {cost}")

    if callback_data.type == "-1":
        basket[sku][size] -= 1
        logger.debug(f"Fetched -1, subbed quantity: {basket[sku][size]}")
        if basket[sku][size] == 0:
            del basket[sku][size]
            logger.debug(f"Size {size} were deleted from {sku} yet")
    elif callback_data.type == "delete":
        logger.debug(f"Fetched delete")
        del basket[sku][size]
        logger.debug(f"Size {size} were deleted from {sku} yet")
    elif callback_data.type == "+1":
        logger.debug(f"Fetched +1")
        basket[sku][size] += 1
        logger.debug(f"Quantity were added 1")
    logger.debug(f"Basket after manipulations: {basket}")
    await dump_basket(redis, basket, callback.from_user.id)

    total = 0
    for sub_sku, sub_basket in basket.items():
        logger.debug(f"sub_sku: {sub_sku}, sub_basket: {sub_basket}")
        for sub_size, sub_quantity in sub_basket.items():
            logger.debug(f"sub_size: {sub_size}, sub_quantity: {sub_quantity}")
            data = await load_data(redis, sub_sku)
            sub_cost = int(data["cost"])
            logger.debug(f"total: {total} += {sub_cost} * {sub_quantity}")
            total += sub_cost * sub_quantity
    quantity = basket[sku].get(size, 0)
    interim = cost * quantity
    logger.debug(f"interim: {interim} = {cost} * {quantity}")

    if callback_data.type != "delete" and quantity != 0:
        logger.debug(f"Editing message callback_data.type: {callback_data.type}")
        await callback.message.edit_caption(
            caption=f"<b>{data['name']} {size}</b>\n"
                    f"<i>Цена: {cost} RUB</i>\n"
                    f"<i>Итого: <b>{interim} RUB</b></i>\n",
            reply_markup=(await create_value_buttons(sku, size, quantity)).as_markup()
        )
    else:
        logger.debug(f"Message deleting")
        await callback.message.delete()

    total_message = (await state.get_data())['total_message']
    if total_message:
        logger.debug(f"Total editing, total: {total}")
        if total == 0:
            await callback.bot.edit_message_text(chat_id=total_message['chat_id'],
                                                 message_id=total_message['message_id'],
                                               text=f"Корзина пуста")
        else:
            await callback.bot.edit_message_text(chat_id=total_message['chat_id'],
                                                 message_id=total_message['message_id'],
                                                 text=f"Всего в корзине на: <i>{total} RUB</i>",
                                                 reply_markup=(await create_buy_button()).as_markup())
