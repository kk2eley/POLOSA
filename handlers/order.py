from aiogram import Router
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State, default_state
from aiogram import F
from aiogram.types import CallbackQuery, Message
import logging
from aiogram.filters import StateFilter, Command
from keyboards.order_keys import create_location_button, create_delivery_buttons

router = Router()
logger = logging.getLogger(__name__)


class FSMOrder(StatesGroup):
    name = State()
    mail = State()
    phone = State()
    address = State()
    delivery = State()
    offer_confirmation = State()
    payment_type = State()
    payment = State()


async def get_info(state: FSMContext, key):
    data = await state.get_data()
    logger.debug(f"Info got: {data}")
    if key in data:
        return data[key]
    return None


async def set_info(state: FSMContext, key, field, value):
    data = await get_info(state, key)
    if data:
        data[field] = value
    else:
        data = {field: value}
    await state.update_data(order=data)


@router.message(Command("cancel"))
async def cmd_cancel_order(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(text="Заказ отменён")


@router.callback_query(F.data == "create_order")
async def cmd_create_order(callback: CallbackQuery, state: FSMContext):
    await state.set_state(FSMOrder.name)
    await callback.message.answer(text="Пришлите <b>Имя и Фамилию</b>")


@router.message(StateFilter(FSMOrder.name))
async def cmd_name(message: Message, state: FSMContext):
    await set_info(state, "order", "name", message.text)
    await state.set_state(FSMOrder.mail)
    await message.answer(text="Пришлите e-mail")


@router.message(StateFilter(FSMOrder.mail))
async def cmd_mail(message: Message, state: FSMContext):
    entities = message.entities or []
    for item in entities:
        if item.type == "email":
            await set_info(state, "order", "mail", message.text[item.offset: item.offset + item.length])
            await state.set_state(FSMOrder.phone)
            await message.answer(text="Пришлите номер телефона")
            break
    else:
        await message.answer(text="Я не вижу здесь email, попробуйте ещё раз")
        return


@router.message(StateFilter(FSMOrder.phone))
async def cmd_phone(message: Message, state: FSMContext):
    entities = message.entities or []
    for item in entities:
        if item.type == "phone_number":
            await set_info(state, "order", "phone", message.text[item.offset: item.offset + item.length])
            await state.set_state(FSMOrder.address)
            await message.answer(
                text="Пришлите адресс доставки. Так мы поймём какие пункты выдачи к вам ближе всего или куда доставлять заказ курьеру",
                reply_markup=await create_location_button())
            break
    else:
        await message.answer(text="Я не вижу здесь номера телефона, попробуйте ещё раз")
        return


@router.message(StateFilter(FSMOrder.address))
async def cmd_phone(message: Message, state: FSMContext):
    if message.location:
        await set_info(state, "order", "location", message.location)
    else:
        await set_info(state, "order", "address", message.text)
    await state.set_state(FSMOrder.delivery)
    await message.answer(text="Выберите способ доставки", reply_markup=await create_delivery_buttons())

# basket = await load_basket(redis, callback.from_user.id)
# await callback.message.answer(text=f"<b>Ваш заказ:</b>\n"
#                                    f"", reply_markup=
