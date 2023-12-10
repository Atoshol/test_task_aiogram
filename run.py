import asyncio
import logging
import sys

from aiogram import Bot, Dispatcher, Router, types
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.utils.i18n.core import I18n
from aiogram.utils.i18n.middleware import I18nMiddleware, ConstI18nMiddleware

from handlers.user.main import register_user_routers
from handlers.user.callbacks import register_callback

from utils.defaults import BOT_TOKEN, WORKDIR



async def main() -> None:
    bot = Bot(BOT_TOKEN, parse_mode=ParseMode.HTML)
    dp = Dispatcher(storage=MemoryStorage())

    main_router = Router()
    dp.include_router(main_router)

    await register_user_routers(main_router)
    register_callback(main_router)

    await dp.start_polling(bot, skip_updates=True)


if __name__ == "__main__":
    try:
        logging.basicConfig(level=logging.INFO, stream=sys.stdout)
        asyncio.run(main())
    except KeyboardInterrupt:
        logging.info("Stop bot")
