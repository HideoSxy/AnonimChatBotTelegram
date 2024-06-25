import asyncio
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.redis import RedisStorage, Redis
import logging
from environs import Env
from handlers.user_handler import USER


async def main():
    env = Env()
    env.read_env(path='.env')
    bot = Bot(token=env('TOKEN'))
    redis = Redis()
    storage = RedisStorage(redis=redis)
    dp = Dispatcher(storage=storage)

    logging.basicConfig(
        level=logging.INFO,
        format='%(filename)s:%(lineno)d #%(levelname)-8s '
               '[%(asctime)s] - %(name)s - %(message)s'
    )

    logging.info('Starting bot')

    # dp.update.outer_middleware(...)

    logging.info('Connecting to the routers..')

    dp.include_router(USER)


    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())
