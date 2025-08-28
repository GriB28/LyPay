from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import BotCommand
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

from source.LPAA.abstract import rtr as abstract_r
from source.LPAA.registration import rtr as register_r
from source.LPAA.deposit import rtr as deposit_r
from source.LPAA.info import rtr as info_r
from source.LPAA.announce import rtr as announce_r
from source.LPAA.whitelist import rtr as whitelist_r
from source.LPAA.auction import rtr as auction_r


col_init(autoreset=True)
just_fix_windows_console()
load_dotenv()

storage = MemoryStorage()
disp = Dispatcher(storage=storage)
disp.include_routers(
    abstract_r,
    register_r,
    deposit_r,
    info_r,
    announce_r,
    whitelist_r,
    auction_r
)
bot = Bot(getenv("LYPAY_ADMINS_TOKEN"), default=DefaultBotProperties(parse_mode=ParseMode.HTML))


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


async def download_photo_(file_id: str, path: str):
    try:
        await bot.download(file_id, path)
    except Exception as e:
        print(e)
        tracker.error(
            e=e,
            userID=0
        )


async def edit_text_(chat_id: int, message_id: int, text: str):
    try:
        await bot.edit_message_text(text, chat_id=chat_id, message_id=message_id)
    except Exception as e:
        tracker.error(
            e=e,
            userID=0
        )


@disp.startup()
async def ccc_on_startup():
    for key, value in (await f_read_sublist("ccc/lpaa")).items():
        exelink.ccc_remove_keyboard(
            bot='lpaa',
            chat_id=key,
            message_id=value,
            text="Сервер был перезапущен /> сообщение с клавиатурой удалено автоматически",
            userID=int(key)
        )
        await sleep(0.005)
        exelink.sublist(
            mode='remove',
            name='ccc/lpaa',
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
            for name in cfg.NAMES.LPAA:
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
            await bot.set_my_commands([BotCommand(command=cmd[0], description=cmd[1]) for cmd in cfg.COMMANDS.LPAA])
            set_cmd = F.LIGHTBLACK_EX + S.BRIGHT + "- set commands... " + S.RESET_ALL + F.LIGHTGREEN_EX + "[OK]"
        except:
            set_cmd = F.LIGHTBLACK_EX + S.BRIGHT + "- set commands... " + S.RESET_ALL + F.RED + "[FAILED]"

        started = "\nSTARTED!"

        tracker.startup("lpaa", del_web, *set_name, set_cmd, started)

        await disp.start_polling(bot)
    else:
        print("Bad start; you have to use official Launcher!")


if __name__ == "__main__":
    run(main())
