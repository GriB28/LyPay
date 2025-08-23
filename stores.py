from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import BotCommand, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from os import getenv
from dotenv import load_dotenv

from asyncio import run, sleep
from colorama import Fore as F, Style as S, init as col_init, just_fix_windows_console

from scripts import j2, tracker, lpsql, exelink
from scripts.f import read_sublist as f_read_sublist, de_anchor as f_de_anchor, send_message as f_send_message
from data import config as cfg, txt

from source.SRV.manual_media_id_2 import rtr as manual_media_id_r


col_init(autoreset=True)
just_fix_windows_console()
load_dotenv()

storage = MemoryStorage()
disp = Dispatcher(storage=storage)
auc = j2.fromfile(cfg.PATHS.LAUNCH_SETTINGS)["auction"]
if auc:
    from source.AUC.abstract import rtr as abstract_r
    from source.LPSB.access import rtr as access_r
    from source.AUC.transfer import rtr as transfer_r
    disp.include_routers(
        abstract_r,
        access_r,
        transfer_r,
        manual_media_id_r
    )
else:
    from source.LPSB.abstract import rtr as abstract_r
    from source.LPSB.access import rtr as access_r
    from source.LPSB.cheques import rtr as cheques_r
    from source.LPSB.registration import rtr as registration_r
    from source.LPSB.menu import rtr as menu_r
    from source.LPSB.ad import rtr as ad_r  # !
    from source.LPSB.ad_admins import rtr as ad_admins_r  # !
    disp.include_routers(
        ad_admins_r,  # !
        abstract_r,
        ad_r,
        access_r,
        cheques_r,
        registration_r,
        menu_r,
        manual_media_id_r
    )
bot = Bot(getenv("LYPAY_STORES_TOKEN"), default=DefaultBotProperties(parse_mode=ParseMode.HTML))


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


async def send_cheque_(to: str, cheque_id: str):
    try:
        if (await j2.fromfile_async(cfg.PATHS.LAUNCH_SETTINGS))["auction"]:
            keyboard_markup = None
        else:
            keyboard_ = InlineKeyboardBuilder()
            keyboard_.add(InlineKeyboardButton(text="Возврат денежных средств", callback_data=f"cheque_cancel_{cheque_id}_cb"))
            keyboard_markup = keyboard_.as_markup()

        cheque_ = await j2.fromfile_async(cfg.PATHS.STORES_CHEQUES + f"{cheque_id}.json")
        user_ = lpsql.search("users", "ID", cheque_["customer"])

        generated_strings = list()
        items_ = cheque_["items"]
        multipliers_ = cheque_["multipliers"]
        for _ in range(len(items_)):
            text = f_de_anchor(items_[_]["text"])
            multy = multipliers_[_]
            price = items_[_]["price"]
            generated_strings.append(f"{text} × {multy} | {price * multy} {cfg.VALUTA.SHORT}")

        for shopkeeper in map(lambda d: d["userID"], lpsql.search("shopkeepers", "storeID", to, True)):
            await bot.send_message(shopkeeper, txt.LPSB.CHEQUE.TABLET.format(
                cheque_id=cheque_id,
                name=user_["name"],
                group=user_["class"],
                tag='@'+user_["tag"] if user_["tag"] else '–',
                items=txt.MAIN.STORE.CHEQUE_GENERATED_STRINGS_SEPARATOR.join(generated_strings),
                total=cheque_["price"]
            ), reply_markup=keyboard_markup)
            await sleep(1/30)
    except Exception as e:
        tracker.error(
            e=e,
            userID=0
        )


async def download_photo_(file_id: str, path: str):
    try:
        await bot.download(file_id, path)
    except Exception as e:
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
    for key, value in (await f_read_sublist("ccc/lpsb")).items():
        exelink.ccc_remove_keyboard(
            bot='lpsb',
            chat_id=key,
            message_id=value,
            text="Сервер был перезапущен, сообщение с клавиатурой удалено автоматически. Последнее начатое действие было сброшено.",
            userID=int(key)
        )
        await sleep(0.015)
        exelink.sublist(
            mode='remove',
            name='ccc/lpsb',
            key=key,
            userID=int(key)
        )


# -=-=-=-

async def main():
    settings = j2.fromfile(cfg.PATHS.LAUNCH_SETTINGS)
    if settings["launch"]:
        try:
            await bot.delete_webhook(drop_pending_updates=True)
            del_web = F.LIGHTBLACK_EX + S.BRIGHT + "- skipping webhooks... " + S.RESET_ALL + F.LIGHTGREEN_EX + "[OK]"
        except:
            del_web = F.LIGHTBLACK_EX + S.BRIGHT + "- skipping webhooks... " + S.RESET_ALL + F.RED + "[FAILED]"

        set_name = [F.LIGHTBLACK_EX + S.BRIGHT + "- set name..."]
        if settings["update_names"]:
            for name in cfg.NAMES.AUC if auc else cfg.NAMES.LPSB:
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
            await bot.set_my_commands([
                BotCommand(command=cmd[0], description=cmd[1])
                for cmd in (cfg.COMMANDS.AUC if auc else cfg.COMMANDS.LPSB)
            ])
            set_cmd = F.LIGHTBLACK_EX + S.BRIGHT + "- set commands... " + S.RESET_ALL + F.LIGHTGREEN_EX + "[OK]"
        except:
            set_cmd = F.LIGHTBLACK_EX + S.BRIGHT + "- set commands... " + S.RESET_ALL + F.RED + "[FAILED]"

        started = "\nSTARTED!"

        tracker.startup("auc" if auc else "lpsb", del_web, *set_name, set_cmd, started)

        await disp.start_polling(bot)
    else:
        print("Bad start; you have to use official Launcher!")


if __name__ == "__main__":
    run(main())
