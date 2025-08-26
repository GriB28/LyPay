from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from asyncio import sleep
from colorama import Fore as F, Style as S
from os.path import exists
from shutil import rmtree

from data.config import MEDIA, PATHS
from scripts import f, firewall3, tracker, exelink, lpsql
from data import txt


rtr = Router()
firewall3 = firewall3.FireWall('MAIN', silent=True)
db = lpsql.DataBase("lypay_database.db", lpsql.Tables.MAIN)
print("SRV/admin_handler router")


@rtr.message(Command("next_test"))
async def go_next(message: Message, state: FSMContext):
    try:
        firewall_status = firewall3.check(message.from_user.id)
        if firewall_status == firewall3.WHITE_ANCHOR:
            cmd = message.text.split()
            if len(cmd) > 1:
                try:
                    test_num = int(cmd[1])
                except ValueError:
                    test_num = None
            else:
                test_num = None

            tracker.log(
                command=("ARTTEST", F.LIGHTGREEN_EX + S.BRIGHT),
                status=("NEXT", F.LIGHTGREEN_EX),
                from_user=f.collect_FU(message)
            )

            if test_num is None:
                try:
                    test_num = (await state.get_data())["TEST_NUM"] + 1
                except KeyError:
                    test_num = 1
            await state.update_data(TEST_NUM=test_num)
            exelink.sublist(
                name='arttest',
                key='testnum',
                data=test_num,
                userID=message.from_user.id
            )
            exelink.sublist(
                name='arttest',
                key='teststate',
                data='testing',
                userID=message.from_user.id
            )
            await sleep(1)
            await update_keyboards("""
Новый этап!

Снизу у клавиатуры у Вас появилась (обновилась) кнопка с порядковым номером теста.
Следуйте инструкциям организатора.
""")
            await message.answer(f"Тест №{test_num} запущен.")

        elif firewall_status == firewall3.BLACK_ANCHOR:
            await message.answer(txt.LPAA.IN_BLACKLIST)
            tracker.black(f.collect_FU(message))
        else:
            await message.answer(txt.LPAA.NOT_IN_WHITELIST)
            tracker.gray(f.collect_FU(message))
            await sleep(2)
            await message.answer_animation(MEDIA.NOT_IN_LPAA_WHITELIST)
            print(F.LIGHTBLACK_EX + S.DIM + str(message.from_user.id))
    except Exception as e:
        tracker.error(
            e=e,
            userID=message.from_user.id
        )


@rtr.message(Command("end_test"))
async def end_test(message: Message, state: FSMContext):
    try:
        firewall_status = firewall3.check(message.from_user.id)
        if firewall_status == firewall3.WHITE_ANCHOR:
            try:
                test_num = (await state.get_data())["TEST_NUM"]
            except KeyError:
                test_num = 0
            if test_num > 0:
                tracker.log(
                    command=("ARTTEST", F.LIGHTGREEN_EX + S.BRIGHT),
                    status=("END_CURRENT", F.LIGHTYELLOW_EX),
                    from_user=f.collect_FU(message)
                )
                exelink.sublist(
                    name='arttest',
                    key='teststate',
                    data='ended',
                    userID=message.from_user.id
                )
                await sleep(1)
                await update_keyboards("""
Подсчёт результатов!

Снизу у клавиатуры у Вас обновилась кнопка.
Нажмите её для получения результатов стресс-теста.
""")
                await message.answer(f"Текущий тест (№{(await state.get_data())["TEST_NUM"]}) завершён. Доступна кнопка результатов.")
            else:
                await message.answer("Тест ещё не был начат.")

        elif firewall_status == firewall3.BLACK_ANCHOR:
            await message.answer(txt.LPAA.IN_BLACKLIST)
            tracker.black(f.collect_FU(message))
        else:
            await message.answer(txt.LPAA.NOT_IN_WHITELIST)
            tracker.gray(f.collect_FU(message))
            await sleep(2)
            await message.answer_animation(MEDIA.NOT_IN_LPAA_WHITELIST)
            print(F.LIGHTBLACK_EX + S.DIM + str(message.from_user.id))
    except Exception as e:
        tracker.error(
            e=e,
            userID=message.from_user.id
        )


@rtr.message(Command("reset_test"))
async def reset_test_num(message: Message, state: FSMContext):
    try:
        firewall_status = firewall3.check(message.from_user.id)
        if firewall_status == firewall3.WHITE_ANCHOR:
            tracker.log(
                command=("ARTTEST", F.LIGHTGREEN_EX + S.BRIGHT),
                status=("RESET_TEST_NUM", F.LIGHTRED_EX),
                from_user=f.collect_FU(message)
            )
            await state.update_data(TEST_NUM=0)
            exelink.sublist(
                name='arttest',
                key='testnum',
                data=0,
                userID=message.from_user.id
            )
            exelink.sublist(
                name='arttest',
                key='teststate',
                data='reset',
                userID=message.from_user.id
            )
            if exists(PATHS.LISTS + "arttest"):
                rmtree(PATHS.LISTS + "arttest")
            db.manual("delete from arttest_test1")
            db.manual("delete from arttest_test4")
            await sleep(.95)
            await update_keyboards("===")
            await message.answer(f"Текущий тест сброшен (удалены все материалы).")
        elif firewall_status == firewall3.BLACK_ANCHOR:
            await message.answer(txt.LPAA.IN_BLACKLIST)
            tracker.black(f.collect_FU(message))
        else:
            await message.answer(txt.LPAA.NOT_IN_WHITELIST)
            tracker.gray(f.collect_FU(message))
            await sleep(2)
            await message.answer_animation(MEDIA.NOT_IN_LPAA_WHITELIST)
            print(F.LIGHTBLACK_EX + S.DIM + str(message.from_user.id))
    except Exception as e:
        tracker.error(
            e=e,
            userID=message.from_user.id
        )


async def update_keyboards(text: str):
    for user in db.searchall("users", "ID"):
        exelink.message(
            text=text,
            bot='MAIN',
            participantID=user,
            reset=True,
            userID=0
        )
        await sleep(.08)
