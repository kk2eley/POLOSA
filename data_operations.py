import logging
import json

logger = logging.getLogger(__name__)

async def load_data(redis, sku):
    serialized_data = await redis.get(sku)
    if not serialized_data:
        logger.warning("No data!")
        return
    logger.debug("Data loaded")
    return json.loads(serialized_data)


async def load_basket(redis, user_id):
    serialized_basket = await redis.hget("users_baskets", user_id)
    if not serialized_basket:
        logger.warning("No basket")
        return
    logger.debug("Basket loaded")
    return json.loads(serialized_basket)


async def dump_data(redis, data, sku):
    serialized_data = json.dumps(data)
    await redis.set(sku, serialized_data)  # await is needed here
    logger.debug("Data dumped")


async def dump_basket(redis, basket, user_id):
    serialized_data = json.dumps(basket)
    await redis.hset("users_baskets", user_id, serialized_data)  # await is needed here
    logger.debug("Basket dumped")
