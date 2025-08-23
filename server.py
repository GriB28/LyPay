from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from os import getenv
from dotenv import load_dotenv

from scripts import tracker
from scripts.f import send_message as f_send_message


load_dotenv()

storage = MemoryStorage()
disp = Dispatcher(storage=storage)
bot = Bot(getenv("LYPAY_SUB_SERVER_TOKEN"), default=DefaultBotProperties(parse_mode=ParseMode.HTML))


async def send_message_(to: int,
                        message: str,
                        file: str | None = None, file_mode: str | None = None,
                        reset_keyboard: bool = False):
    try:
        await f_send_message(
            bot=bot, to=to, message=message,
            file=file, file_mode=file_mode,
            reset_keyboard=reset_keyboard
        )
    except Exception as e:
        tracker.error(
            e=e,
            userID=0
        )
