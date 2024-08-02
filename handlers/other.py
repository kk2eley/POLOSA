from aiogram import Router
from aiogram import F
from aiogram import types
from keyboards.other_keys import create_faq_buttons, create_contacts_buttons, back_faq_keys
from lexicon import FAQ

router = Router()


@router.callback_query(F.data == "faq")
async def cmd_faq(callback: types.CallbackQuery):
    await callback.message.edit_text(text="FAQ", reply_markup=(await create_faq_buttons()).as_markup())


@router.callback_query(F.data == "delivery")
async def delivery_faq(callback: types.CallbackQuery):
    await callback.message.edit_text(text=FAQ["delivery"], reply_markup=await back_faq_keys())

@router.callback_query(F.data == "booking")
async def delivery_faq(callback: types.CallbackQuery):
    await callback.message.edit_text(text=FAQ["booking"], reply_markup=await back_faq_keys())

@router.callback_query(F.data == "refund_exchange")
async def delivery_faq(callback: types.CallbackQuery):
    await callback.message.edit_text(text=FAQ["refund_exchange"], reply_markup=await back_faq_keys())

@router.callback_query(F.data == "payment")
async def delivery_faq(callback: types.CallbackQuery):
    await callback.message.edit_text(text=FAQ["payment"], reply_markup=await back_faq_keys())

@router.callback_query(F.data == "self_delivery")
async def delivery_faq(callback: types.CallbackQuery):
    await callback.message.edit_text(text=FAQ["self_delivery"], reply_markup=await back_faq_keys())

@router.callback_query(F.data == "size_chosing")
async def delivery_faq(callback: types.CallbackQuery):
    await callback.message.edit_text(text=FAQ["size_chosing"], reply_markup=await back_faq_keys())

@router.callback_query(F.data == "contacts")
async def cmd_contacts(callback: types.CallbackQuery):
    await callback.message.edit_text(text="Контакты\n"
                                       "ИП Григорьев Николай Владимирович\n"
                                       "ИНН: 525813154725\n"
                                       "ОГРН: 320527500000492\n"
                                       "Почта: support@polosabrand.com\n",
                                  reply_markup=await create_contacts_buttons())
