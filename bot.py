import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.filters import StateFilter
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.redis import RedisStorage
from aiogram.utils.callback_answer import CallbackAnswerMiddleware
from config_reader import config
from handlers import stuff, menu, admin_panel, basket, other, order
import test
from keyboards.menu_keys import set_users_main_menu
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
import aioredis
from keyboards import menu_keys


async def main():
    logging.basicConfig(level=logging.DEBUG, format='#%(levelname)-8s %(filename)15s:'
                                                    '%(lineno)4d - %(name)15s - %(message)s')

    bot = Bot(token=config.bot_token.get_secret_value(), default=DefaultBotProperties(parse_mode=ParseMode.HTML))

    await menu_keys.set_users_main_menu(bot)
    # Инициализируем aioredis
    redis = await aioredis.Redis(host='localhost', port=6379, db=0)
    storage = RedisStorage(redis=redis)
    dp = Dispatcher(storage=storage)
    dp['redis'] = redis

    # Асинхронное получение элементов списка
    elements = await redis.lrange('admins', 0, -1)
    elements = [element.decode('utf-8') for element in elements]  # Декодирование байтовых строк

    admins = elements + [config.super_user_id.get_secret_value()]
    dp['admins'] = admins
    dp.callback_query.middleware(CallbackAnswerMiddleware())
    dp.include_routers(admin_panel.router, menu.router, basket.router, stuff.router, other.router, order.router, )
    dp.include_router(test.router)

    # Запускаем бота и пропускаем все накопленные входящие
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

    # Закрытие соединения с Redis при завершении работы
    redis.close()
    await redis.wait_closed()


if __name__ == "__main__":
    asyncio.run(main())
