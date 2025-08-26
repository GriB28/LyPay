from aiogram import Router
from aiogram import F as mF
from aiogram.types import Message
from aiogram.filters.command import Command
from aiogram.fsm.context import FSMContext

from colorama import Fore as F, Style as S
from random import randint

from scripts import f, firewall3, tracker, exelink, lpsql
from scripts.j2 import fromfile as j_fromfile
from data import txt, config as cfg

from source.LPAA._states import *


rtr = Router()
config = [j_fromfile(cfg.PATHS.LAUNCH_SETTINGS)["config_v"]]
firewall3 = firewall3.FireWall('LPAA')
db = lpsql.DataBase("lypay_database.db", lpsql.Tables.MAIN)
print("LPAA/registration router")


@rtr.message(Command("register_email"), mF.chat.id == cfg.HIGH_GROUP)
async def start_reg(message: Message, state: FSMContext):
    try:
        f.update_config(config, [txt, cfg])
        cmd = message.text.split()
        if len(cmd) > 1:
            await do_proceeding(cmd[1], message, state)
        else:
            await message.answer(txt.LPAA.STORE_REGISTER.START)
            await state.set_state(StoreRegisterFSM.EMAIL)
            tracker.log(
                command=("STORE_REGISTER", F.YELLOW),
                status=("START", F.YELLOW),
                from_user=f.collect_FU(message)
            )
    except Exception as e:
        tracker.error(
            e=e,
            userID=message.from_user.id
        )


async def do_proceeding(text: str, message: Message, state: FSMContext):
    if not (text.count('@') == 1 and text[text.find('@'):].count('.') > 0 and text.index('@') > 0):
        await message.answer(txt.LPAA.STORE_REGISTER.BAD_FORMAT)
        tracker.log(
            command=("STORE_REGISTER", F.YELLOW),
            status=("EMAIL_NOT_FOUND", F.RED),
            from_user=f.collect_FU(message)
        )
    elif text in (await f.read_sublist("store_form_link")).keys():
        await message.answer(txt.LPAA.STORE_REGISTER.RECORD_EXIST)
        tracker.log(
            command=("STORE_REGISTER", F.YELLOW),
            status=("EXISTING_RECORD", F.RED + S.DIM),
            from_user=f.collect_FU(message)
        )
    elif text in db.searchall("stores", "hostEmail"):
        await message.answer(txt.LPAA.STORE_REGISTER.STORE_EXIST.format(
            id=db.search("stores", "hostEmail", text)["ID"])
        )
        tracker.log(
            command=("STORE_REGISTER", F.YELLOW),
            status=("EXISTING_STORE", F.RED + S.DIM),
            from_user=f.collect_FU(message)
        )
    else:
        shuffle = list('0123456789abcdef')
        code = "".join([shuffle[randint(0, 15)] for _ in range(32)])

        exelink.email(
            path=cfg.PATHS.EMAIL + "store.html",
            participantEmail=text,
            theme="LyPay: приглашение на Благотворительную Ярмарку-2025",
            keys={
                "VERSION": cfg.VERSION,
                "BUILD": cfg.BUILD,
                "NAME": f' ({cfg.NAME})' if cfg.NAME != '' else '',
                "CODE": code
            },
            files=[cfg.PATHS.EMAIL + "LyPay Store's Manual.pdf"],
            userID=message.from_user.id
        )
        exelink.sublist(
            mode='add',
            name='store_form_link',
            key=code,
            data=text,
            userID=message.from_user.id
        )
        await message.answer(txt.LPAA.STORE_REGISTER.END.format(code=code))
        tracker.log(
            command=("STORE_REGISTER", F.YELLOW),
            status=("OK", F.GREEN),
            from_user=f.collect_FU(message)
        )
        await state.clear()


@rtr.message(mF.text, StoreRegisterFSM.EMAIL)
async def proceed_email(message: Message, state: FSMContext):
    try:
        f.update_config(config, [txt, cfg])
        text = message.text
        await do_proceeding(text, message, state)
    except Exception as e:
        tracker.error(
            e=e,
            userID=message.from_user.id
        )
