import logging

from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder
from aiogram import types
from aiogram.filters import Command
from aiogram import Router
from aiogram.filters import ChatMemberUpdatedFilter, KICKED
from aiogram.types import ChatMemberUpdated
from aiogram.filters.callback_data import CallbackData

router = Router()
logger = logging.getLogger()


@router.my_chat_member(ChatMemberUpdatedFilter(member_status_changed=KICKED))
async def process_user_blocked_bot(event: ChatMemberUpdated):
    print(f'Пользователь {event.from_user.id} заблокировал бота')


@router.callback_query()
async def all_callback(callback: types.CallbackQuery):
    logger.debug(f"Callback data: {callback.data}")
