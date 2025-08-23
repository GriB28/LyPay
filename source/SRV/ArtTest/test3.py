from aiogram import Router
from aiogram import F as mF
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from colorama import Fore as F, Style as S
from os import listdir

from data.config import PATHS
from scripts import f, firewall3, tracker, exelink
from data import txt


rtr = Router()
firewall3 = firewall3.FireWall('MAIN', silent=True)
print("SRV/test3 router")


@rtr.message(mF.text == "[TЕCТ 3]")
async def test(message: Message, state: FSMContext):
    try:
        firewall_status = firewall3.check(message.from_user.id)
        if firewall_status == firewall3.WHITE_ANCHOR:
            tracker.log(
                command=("TEST_3", F.GREEN + S.BRIGHT),
                from_user=f.collect_FU(message)
            )

            try:
                await state.update_data(TEST3=(await state.get_data())["TEST3"] + 1)
            except KeyError:
                await state.update_data(TEST3=1)

            exelink.add(f"test3 {message.from_user.id}", message.from_user.id)

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


@rtr.message(mF.text == "[TЕCТ 3] [зaвepшить]")
async def test_end(message: Message, state: FSMContext):
    try:
        firewall_status = firewall3.check(message.from_user.id)
        if firewall_status == firewall3.WHITE_ANCHOR:
            data = await state.get_data()
            try:
                answer = data["TEST3"]
                tracker.log(
                    command=("TEST_3_END", F.CYAN + S.BRIGHT),
                    from_user=f.collect_FU(message)
                )

                await message.answer(str(answer * 20))
                await message.answer(str(len(listdir(PATHS.LISTS + f"arttest/test3/{message.from_user.id}"))))
                await state.clear()
            except KeyError:
                pass

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


''' EXE part
elif task[0] == "test3":
    userID = int(task[1])
    for i in range(20):
        exelink.sublist(
            name=f"arttest/test3/{userID}/{str(randint(0, 1000000000))+str(raw_unix())}",
            key=str(raw_unix()),
            data=userID,
            userID=userID
        )
'''
