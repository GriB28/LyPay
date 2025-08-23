from aiogram import Router
from aiogram.types import Message
from aiogram.filters.command import Command

from colorama import Fore as F

from scripts import f, tracker, exelink
from data import config as cfg, txt


rtr = Router()
print("MAIN/hidden_staff router")


@rtr.message(Command("r34"))
async def r34(message: Message):
    await message.answer("Нет.")
    tracker.log(
        command=(F.LIGHTWHITE_EX, "R34"),
        from_user=f.collect_FU(message)
    )
    exelink.warn(
        text=txt.EXE.EVENTS.HIDDEN_STUFF_R34.format(id=message.from_user.id),
        userID=message.from_user.id
    )


@rtr.message(Command("xilonen"))
async def xilonen(message: Message):
    await message.answer_sticker(cfg.MEDIA.XILONEN)
    tracker.log(
        command=(F.LIGHTWHITE_EX, "XILONEN"),
        from_user=f.collect_FU(message)
    )
    exelink.warn(
        text=txt.EXE.EVENTS.HIDDEN_STUFF_XILONEN.format(id=message.from_user.id),
        userID=message.from_user.id
    )
