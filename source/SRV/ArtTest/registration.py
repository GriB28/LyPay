from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from colorama import Fore as F, Style as S
from random import randint

from scripts import f, firewall3, tracker, lpsql
from data import txt


rtr = Router()
firewall3 = firewall3.FireWall('MAIN', silent=False)
print("SRV/registration router")


@rtr.message(Command("start"))
async def test(message: Message):
    try:
        firewall_status = firewall3.check(message.from_user.id)
        if firewall_status == firewall3.WHITE_ANCHOR:
            tracker.log(
                command=("REGISTRATION", F.YELLOW + S.BRIGHT),
                from_user=f.collect_FU(message)
            )

            if message.from_user.id not in lpsql.searchall("users", "ID"):
                lpsql.insert("users",
                             [
                                 message.from_user.id,          # ID
                                 "запись создана на арттесте",  # name
                                 "тестировщик",                 # class
                                 None,                          # email
                                 message.from_user.username,    # tag
                                 None,                          # balance
                                 None                           # owner
                             ])
            stickers = (
                "CAACAgIAAxkBAAISF2fxiF__FgOaG61nJeReRu1-VI1KAAJqAAO_Zp0Ymm8_-zxRVY42BA",
                "CAACAgIAAxkBAAISGWfxiI78cSp0Ec9hVkMGm57QnLdcAAJFAAO_Zp0Y85q75bmzpws2BA",
                "CAACAgIAAxkBAAISG2fxiJmmusE3CyPtNHGjIzPrlCt2AAI1AAO_Zp0YnjBB8YeDtUU2BA",
                "CAACAgIAAxkBAAISHWfxiKFuEu377HrfHPcXPLsxTC-3AAI-AAO_Zp0YnZiFVia4YRs2BA",
                "CAACAgIAAxkBAAISH2fxiLLJ0QEsPkvDM-HQUoDu4GMLAAJqDgACtqlwSIhrY4JurVjXNgQ"
            )
            await message.answer_sticker(
                stickers[randint(0, len(stickers)-1)]
                if message.from_user.id not in (562532936, 350531376) else
                "CAACAgUAAxkBAAISNWfxiurkbnoYQRYnK6u0HsJZXrvxAAIyFgACVWGoVIXx95gsMVlWNgQ"
            )

        elif firewall_status == firewall3.BLACK_ANCHOR:
            tracker.black(f.collect_FU(message))
            await message.answer(txt.MAIN.CMD.IN_BLACKLIST)
        else:
            tracker.gray(f.collect_FU(message))
            await message.answer(txt.MAIN.CMD.NOT_IN_WHITELIST)
    except Exception as e:
        tracker.error(
            e=e,
            userID=message.from_user.id
        )
