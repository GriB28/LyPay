from aiogram import Router
from aiogram import F as mF
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from colorama import Fore as F, Style as S
from random import randint

from scripts import f, firewall3, tracker, lpsql
from scripts.unix import raw as raw_unix
from data import txt


rtr = Router()
firewall3 = firewall3.FireWall('MAIN', silent=True)
db = lpsql.DataBase("lypay_database.db", lpsql.Tables.MAIN)
print("SRV/test4_1x5 router")


@rtr.message(mF.text == "[TЕCТ 4]")
async def test(message: Message, state: FSMContext):
    try:
        firewall_status = firewall3.check(message.from_user.id)
        if firewall_status == firewall3.WHITE_ANCHOR:
            tracker.log(
                command=("TEST_4", F.GREEN + S.BRIGHT),
                from_user=f.collect_FU(message)
            )

            try:
                await state.update_data(TEST4=(await state.get_data())["TEST4"] + 1)
            except KeyError:
                await state.update_data(TEST4=1)

            db.insert("arttest_test4", [str(randint(0, 1000000000)) + str(raw_unix()), message.from_user.id])
            db.insert("arttest_test4", [str(randint(0, 1000000000)) + str(raw_unix()), message.from_user.id])
            db.insert("arttest_test4", [str(randint(0, 1000000000)) + str(raw_unix()), message.from_user.id])
            db.insert("arttest_test4", [str(randint(0, 1000000000)) + str(raw_unix()), message.from_user.id])
            db.insert("arttest_test4", [str(randint(0, 1000000000)) + str(raw_unix()), message.from_user.id])

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


@rtr.message(mF.text == "[TЕCТ 4] [зaвepшить]")
async def test_end(message: Message, state: FSMContext):
    try:
        firewall_status = firewall3.check(message.from_user.id)
        if firewall_status == firewall3.WHITE_ANCHOR:
            data = await state.get_data()
            try:
                answer = data["TEST4"]
                tracker.log(
                    command=("TEST_4_END", F.CYAN + S.BRIGHT),
                    from_user=f.collect_FU(message)
                )

                await message.answer(str(answer * 5))
                await message.answer(str(db.searchall("arttest_test4", "ID").count(message.from_user.id)))
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
