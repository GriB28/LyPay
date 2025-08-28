from aiogram import Bot, Dispatcher
from aiogram.types import BotCommand
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from os import getenv
from dotenv import load_dotenv
from sys import argv

from asyncio import run, sleep
from colorama import Fore as F, Style as S, init as col_init, just_fix_windows_console

from scripts import j2, tracker, exelink
from scripts.f import read_sublist as f_read_sublist, send_message as f_send_message
from data import config as cfg

from source.MAIN.abstract import rtr as abstract_r
from source.MAIN.registration import rtr as registration_r
from source.MAIN.transfer import rtr as transfer_r
from source.MAIN.store import rtr as store_r
from source.MAIN.coupon import rtr as coupon_r
from source.MAIN.hidden_stuff import rtr as hidden_r
from source.SRV.manual_media_id_1 import rtr as manual_media_id_r

from source.MAIN._keyboards import update_keyboard


col_init(autoreset=True)
just_fix_windows_console()
load_dotenv()

storage = MemoryStorage()
disp = Dispatcher(storage=storage)
disp.include_routers(
    registration_r,  # ВСЕГДА выше, чем abstract
    abstract_r,
    transfer_r,
    store_r,
    coupon_r,
    hidden_r,
    manual_media_id_r
)
bot = Bot(getenv("LYPAY_MAIN_TOKEN"), default=DefaultBotProperties(parse_mode=ParseMode.HTML))


async def send_message_(to: int,
                        message: str,
                        file: str | None = None, file_mode: str | None = None,
                        reset_keyboard: bool = False):
    try:
        await f_send_message(
            bot=bot, to=to, message=message,
            file=file, file_mode=file_mode,
            update_keyboard=update_keyboard, reset_keyboard=reset_keyboard
        )
    except Exception as e:
        tracker.error(
            e=e,
            userID=0
        )


async def edit_text_(chat_id: int, message_id: int, text: str, ccc_refresh_keyboard: bool = False):
    try:
        await bot.edit_message_text(text, chat_id=chat_id, message_id=message_id)
        if ccc_refresh_keyboard:
            await f_send_message(
                bot=bot, to=chat_id, message="Последнее начатое действие было сброшено.",
                update_keyboard=update_keyboard, reset_keyboard=True
            )
    except Exception as e:
        tracker.error(
            e=e,
            userID=0
        )


@disp.startup()
async def ccc_on_startup():
    for key, value in (await f_read_sublist("ccc/main")).items():
        exelink.ccc_remove_keyboard(
            bot='main',
            chat_id=key,
            message_id=value,
            text="Сервер был перезапущен, сообщение с клавиатурой удалено автоматически.",
            userID=int(key)
        )
        await sleep(0.015)
        exelink.sublist(
            mode='remove',
            name='ccc/main',
            key=key,
            userID=int(key)
        )


# -=-=-=-

async def main():
    settings = j2.fromfile(cfg.PATHS.LAUNCH_SETTINGS)
    if settings["launch"] and argv[1] == settings["launch_stamp"]:
        try:
            await bot.delete_webhook(drop_pending_updates=True)
            del_web = F.LIGHTBLACK_EX + S.BRIGHT + "- skipping webhooks... " + S.RESET_ALL + F.LIGHTGREEN_EX + "[OK]"
        except:
            del_web = F.LIGHTBLACK_EX + S.BRIGHT + "- skipping webhooks... " + S.RESET_ALL + F.RED + "[FAILED]"

        set_name = [F.LIGHTBLACK_EX + S.BRIGHT + "- set name..."]
        if settings["update_names"]:
            for name in cfg.NAMES.MAIN:
                try:
                    await bot.set_my_name(name=name[0], language_code=name[1])
                    set_name.append(F.LIGHTBLACK_EX + S.BRIGHT + f"   > {name[1] if name[1] else 'null'} : "
                                    + S.RESET_ALL + F.LIGHTGREEN_EX + "[OK]")
                except:
                    set_name.append(F.LIGHTBLACK_EX + S.BRIGHT + f"   > {name[1] if name[1] else 'null'} : "
                                    + S.RESET_ALL + F.RED + "[FAILED]")
        else:
            set_name[0] += S.RESET_ALL + F.YELLOW + " [SKIPPED]"

        try:
            await bot.set_my_commands([BotCommand(command=cmd[0], description=cmd[1]) for cmd in cfg.COMMANDS.MAIN])
            set_cmd = F.LIGHTBLACK_EX + S.BRIGHT + "- set commands... " + S.RESET_ALL + F.LIGHTGREEN_EX + "[OK]"
        except:
            set_cmd = F.LIGHTBLACK_EX + S.BRIGHT + "- set commands... " + S.RESET_ALL + F.RED + "[FAILED]"

        started = "\nSTARTED!"

        tracker.startup("main", del_web, *set_name, set_cmd, started)

        await disp.start_polling(bot)
    else:
        print("Bad start; you have to use official Launcher!")


if __name__ == "__main__":
    run(main())
