from aiogram import Router
from aiogram import F as mF
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from colorama import Fore as F, Style as S
from random import randint

from scripts import f, firewall3, tracker, exelink
from scripts.unix import raw as raw_unix
from data import txt


rtr = Router()
firewall3 = firewall3.FireWall('MAIN', silent=True)
print("SRV/test2 router")


@rtr.message(mF.text == "[TЕCТ 2]")
async def test(message: Message, state: FSMContext):
    try:
        firewall_status = firewall3.check(message.from_user.id)
        if firewall_status == firewall3.WHITE_ANCHOR:
            tracker.log(
                command=("TEST_2", F.GREEN + S.BRIGHT),
                from_user=f.collect_FU(message)
            )

            try:
                await state.update_data(TEST2=(await state.get_data())["TEST2"] + 1)
            except KeyError:
                await state.update_data(TEST2=1)

            exelink.sublist(
                name="arttest/test2",
                key=str(randint(0, 1000000000))+str(raw_unix()),
                data=message.from_user.id,
                userID=message.from_user.id
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


@rtr.message(mF.text == "[TЕCТ 2] [зaвepшить]")
async def test_end(message: Message, state: FSMContext):
    try:
        firewall_status = firewall3.check(message.from_user.id)
        if firewall_status == firewall3.WHITE_ANCHOR:
            data = await state.get_data()
            try:
                answer = data["TEST2"]
                tracker.log(
                    command=("TEST_2_END", F.CYAN + S.BRIGHT),
                    from_user=f.collect_FU(message)
                )

                await message.answer(str(answer))
                await message.answer(str(list((await f.read_sublist("arttest/test2")).values()).count(str(message.from_user.id))))
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
