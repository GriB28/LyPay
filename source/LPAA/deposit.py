from aiogram import Router
from aiogram import F as mF
from aiogram.filters.command import Command
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from asyncio import sleep
from colorama import Fore as F, Style as S
from random import randint

from scripts import f, firewall3, tracker, exelink, lpsql, j2
from data import config as cfg, txt

from source.LPAA._states import *


rtr = Router()
config = [j2.fromfile(cfg.PATHS.LAUNCH_SETTINGS)["config_v"]]
firewall3 = firewall3.FireWall('LPAA')
print("LPAA/deposit router")


@rtr.message(Command("deposit"), mF.chat.id.in_((cfg.HIGH_GROUP, cfg.WARNING_GROUP)))
async def deposit_help_admins(message: Message):
    try:
        f.update_config(config, [txt, cfg])
        await message.answer(txt.LPAA.DEPOSIT.ADMIN_HELP)
        tracker.log(
            command=("DEPOSIT", F.CYAN + S.BRIGHT),
            status=("ADMINS_HELP", F.GREEN + S.DIM),
            from_user=f.collect_FU(message)
        )
    except Exception as e:
        tracker.error(
            e=e,
            userID=message.from_user.id
        )


@rtr.message(Command("deposit"), mF.chat.id.not_in((cfg.HIGH_GROUP, cfg.WARNING_GROUP)))
async def deposit_help_agents(message: Message, state: FSMContext):
    try:
        f.update_config(config, [txt, cfg])
        firewall_status = firewall3.check(message.from_user.id)
        if firewall_status == firewall3.WHITE_ANCHOR:
            if (await j2.fromfile_async(cfg.PATHS.LAUNCH_SETTINGS))["auction"]:
                await message.answer(txt.LPAA.DEPOSIT.HELP_AUC)
            else:
                await message.answer(txt.LPAA.DEPOSIT.HELP)
            await state.set_state(DepositFSM.ZERO)
            tracker.log(
                command=("DEPOSIT", F.CYAN + S.BRIGHT),
                status=("AGENTS_HELP", F.GREEN + S.DIM),
                from_user=f.collect_FU(message)
            )
        elif firewall_status == firewall3.BLACK_ANCHOR:
            await message.answer(txt.LPAA.IN_BLACKLIST)
            tracker.black(f.collect_FU(message))
        else:
            tracker.gray(f.collect_FU(message))
            await message.answer(txt.LPAA.NOT_IN_WHITELIST)
            await sleep(2)
            await message.answer_animation(cfg.MEDIA.NOT_IN_LPAA_WHITELIST)
    except Exception as e:
        tracker.error(
            e=e,
            userID=message.from_user.id
        )


@rtr.message(DepositFSM.ZERO, mF.text.isnumeric())
async def deposit_id(message: Message, state: FSMContext):
    try:
        f.update_config(config, [txt, cfg])
        firewall_status = firewall3.check(message.from_user.id)
        if firewall_status == firewall3.WHITE_ANCHOR:
            try:
                if not (await j2.fromfile_async(cfg.PATHS.LAUNCH_SETTINGS))["auction"] or len(message.text) > 3:
                    if int(message.text) in lpsql.searchall("users", "ID"):
                        await state.update_data(DEPOSIT_QR=int(message.text))
                        await state.update_data(DEPOSIT_MODE="normal")
                        await message.answer(txt.LPAA.DEPOSIT.SET_AMOUNT)
                        await state.set_state(DepositFSM.DEPOSIT_AMOUNT)
                    else:
                        await message.answer(txt.LPAA.WRONG)
                else:
                    if int(message.text) in lpsql.searchall("stores", "auctionID"):
                        await state.update_data(DEPOSIT_QR=lpsql.search("stores", "auctionID", int(message.text))["ID"])
                        await state.update_data(DEPOSIT_MODE="auction")
                        await message.answer(txt.LPAA.DEPOSIT.SET_AMOUNT)
                        await state.set_state(DepositFSM.DEPOSIT_AMOUNT)
                    else:
                        await message.answer(txt.LPAA.WRONG)
            except ValueError:
                await message.answer(txt.LPAA.BAD_ARG)
            tracker.log(
                command=("DEPOSIT", F.CYAN + S.BRIGHT),
                status=("ID", F.LIGHTBLUE_EX + S.NORMAL),
                from_user=f.collect_FU(message)
            )

        elif firewall_status == firewall3.BLACK_ANCHOR:
            await message.answer(txt.LPAA.IN_BLACKLIST)
            tracker.black(f.collect_FU(message))
        else:
            tracker.gray(f.collect_FU(message))
            await message.answer(txt.LPAA.NOT_IN_WHITELIST)
            await sleep(2)
            await message.answer_animation(cfg.MEDIA.NOT_IN_LPAA_WHITELIST)
    except Exception as e:
        tracker.error(
            e=e,
            userID=message.from_user.id
        )


@rtr.message(DepositFSM.DEPOSIT_AMOUNT, mF.text)
async def set_amount(message: Message, state: FSMContext):
    try:
        f.update_config(config, [txt, cfg])
        try:
            amount = int(int(message.text) * cfg.VALUTA.COURSE)
            await state.update_data(DEPOSIT_AMOUNT=amount)
            mode = (await state.get_data())["DEPOSIT_MODE"]

            if mode == "normal":
                user = lpsql.search("users", "ID", (await state.get_data())["DEPOSIT_QR"])
                await message.answer(txt.LPAA.DEPOSIT.CONFIRM.format(
                    user=user["name"],
                    group=user["class"],
                    tag='@'+user["tag"] if user["tag"] else '–',
                    amount=amount)
                )
            else:
                store = lpsql.search("stores", "ID", (await state.get_data())["DEPOSIT_QR"])
                host = lpsql.search("users", "ID", store["hostID"])
                if host is None:
                    host = {
                        "name": "незарегистрированный пользователь",
                        "tag": None
                    }
                await message.answer(txt.LPAA.DEPOSIT.CONFIRM_AUC.format(
                    store=store["ID"],
                    aucID=store["auctionID"],
                    host=host["name"],
                    tag='@'+host["tag"] if host["tag"] else '–',
                    amount=amount)
                )
            await state.set_state(DepositFSM.CONFIRM)
        except ValueError:
            await message.answer(txt.LPAA.BAD_ARG)
        tracker.log(
            command=("DEPOSIT", F.CYAN + S.BRIGHT),
            status=("AMOUNT", F.LIGHTBLUE_EX + S.NORMAL),
            from_user=f.collect_FU(message)
        )
    except Exception as e:
        tracker.error(
            e=e,
            userID=message.from_user.id
        )


@rtr.message(DepositFSM.CONFIRM, Command("confirm"))
async def confirm(message: Message, state: FSMContext):
    try:
        f.update_config(config, [txt, cfg])
        data = await state.get_data()
        lpsql.deposit(data["DEPOSIT_QR"], data["DEPOSIT_AMOUNT"], message.from_user.id)

        if data["DEPOSIT_MODE"] == "normal":
            exelink.message(
                text=txt.MAIN.DEPOSIT.UPDATE.format(
                    value=('+' if data["DEPOSIT_AMOUNT"] >= 0 else '') + str(data["DEPOSIT_AMOUNT"])
                ),
                bot="MAIN",
                participantID=data["DEPOSIT_QR"],
                reset=True,
                userID=message.from_user.id
            )
        else:
            if data["DEPOSIT_AMOUNT"] > 0:
                message_text = cfg.VALUTA.MANUAL_REDACT_p.format(amount=data["DEPOSIT_AMOUNT"])
            else:
                message_text = cfg.VALUTA.MANUAL_REDACT_m.format(amount=-data["DEPOSIT_AMOUNT"])
            for userID in lpsql.search("shopkeepers", "storeID", data["DEPOSIT_QR"], True):
                exelink.message(
                    text=message_text,
                    bot="LPSB",
                    participantID=userID["userID"],
                    userID=message.from_user.id
                )
                await sleep(1/30)

        await state.clear()
        await state.set_state(DepositFSM.ZERO)
        await message.answer(txt.LPAA.DEPOSIT.OK)
        tracker.log(
            command=("CONFIRM", F.GREEN + S.BRIGHT),
            from_user=f.collect_FU(message)
        )
    except Exception as e:
        tracker.error(
            e=e,
            userID=message.from_user.id
        )


# -=-=-=-

@rtr.message(Command("high_deposit"), mF.chat.id == cfg.HIGH_GROUP)
async def high_deposit(message: Message, state: FSMContext):
    try:
        f.update_config(config, [txt, cfg])
        sid = lpsql.search("shopkeepers", "userID", message.from_user.id)
        all_stores = lpsql.searchall("stores", "ID")
        if len(all_stores) > 0:
            await message.answer(txt.LPAA.DEPOSIT.HIGH.START.format(
                uid=message.from_user.id,
                sid=sid["storeID"] if sid else all_stores[randint(0, len(all_stores)-1)]
            ))
        else:
            await message.answer(txt.LPAA.DEPOSIT.HIGH.START.format(
                uid=message.from_user.id,
                sid="abc"
            ))
        await state.set_state(HighDepositFSM.DEPOSIT_QR)
        tracker.log(
            command=("HIGH_DEPOSIT", F.LIGHTGREEN_EX),
            status=("INITIALISE", F.GREEN + S.BRIGHT),
            from_user=f.collect_FU(message)
        )
    except Exception as e:
        tracker.error(
            e=e,
            userID=message.from_user.id
        )


@rtr.message(HighDepositFSM.DEPOSIT_QR, mF.text)
async def high_deposit_choose_id(message: Message, state: FSMContext):
    try:
        f.update_config(config, [txt, cfg])
        pick = message.text
        if pick[0] == 'u':
            try:
                user = int(pick[1:])
            except:
                await message.answer(txt.LPAA.BAD_ARG)
                return
            if user not in lpsql.searchall("users", "ID"):
                await message.answer(txt.LPAA.WRONG)
                return
            await state.update_data(HIGH_DEPOSIT_ID=user)
            await state.set_state(HighDepositFSM.DEPOSIT_AMOUNT)
            await message.answer(txt.LPAA.DEPOSIT.HIGH.AMOUNT)
            tracker.log(
                command=("HIGH_DEPOSIT", F.LIGHTGREEN_EX),
                status=("UID", F.GREEN + S.BRIGHT),
                from_user=f.collect_FU(message)
            )
        elif pick[0] == 's':
            store = pick[1:]
            if store not in lpsql.searchall("stores", "ID"):
                await message.answer(txt.LPAA.WRONG)
                return
            await state.update_data(HIGH_DEPOSIT_ID=store)
            await state.set_state(HighDepositFSM.DEPOSIT_AMOUNT)
            await message.answer(txt.LPAA.DEPOSIT.HIGH.AMOUNT)
            tracker.log(
                command=("HIGH_DEPOSIT", F.LIGHTGREEN_EX),
                status=("SID", F.GREEN + S.BRIGHT),
                from_user=f.collect_FU(message)
            )
        else:
            await message.answer(txt.LPAA.BAD_ARG)
            tracker.log(
                command=("HIGH_DEPOSIT", F.LIGHTGREEN_EX),
                status=("BAD_ARG", F.RED),
                from_user=f.collect_FU(message)
            )
    except Exception as e:
        tracker.error(
            e=e,
            userID=message.from_user.id
        )


@rtr.message(HighDepositFSM.DEPOSIT_AMOUNT, mF.text)
async def high_deposit_amount_input(message: Message, state: FSMContext):
    try:
        f.update_config(config, [txt, cfg])
        try:
            value = int(message.text)
            data = (await state.get_data())["HIGH_DEPOSIT_ID"]
            await state.update_data(HIGH_DEPOSIT_AMOUNT=value)
            await state.set_state(HighDepositFSM.CONFIRM)
            await message.answer(txt.LPAA.DEPOSIT.HIGH.CONFIRM.format(
                id=data,
                prefix='u' if type(data) is int else 's',
                amount=value
            ))
            tracker.log(
                command=("HIGH_DEPOSIT", F.LIGHTGREEN_EX),
                status=("AMOUNT", F.GREEN + S.BRIGHT),
                from_user=f.collect_FU(message)
            )
        except ValueError:
            await message.asnwer(txt.LPAA.BAD_ARG)
            tracker.log(
                command=("HIGH_DEPOSIT", F.LIGHTGREEN_EX),
                status=("BAD_ARG", F.RED),
                from_user=f.collect_FU(message)
            )
    except Exception as e:
        tracker.error(
            e=e,
            userID=message.from_user.id
        )


@rtr.message(Command("confirm"), HighDepositFSM.CONFIRM)
async def high_deposit_confirm(message: Message, state: FSMContext):
    try:
        f.update_config(config, [txt, cfg])
        data = await state.get_data()
        lpsql.deposit(data["HIGH_DEPOSIT_ID"], data["HIGH_DEPOSIT_AMOUNT"], message.from_user.id)
        if data["HIGH_DEPOSIT_AMOUNT"] > 0:
            message_text = cfg.VALUTA.MANUAL_REDACT_p.format(amount=data["HIGH_DEPOSIT_AMOUNT"])
        else:
            message_text = cfg.VALUTA.MANUAL_REDACT_m.format(amount=-data["HIGH_DEPOSIT_AMOUNT"])

        if type(data["HIGH_DEPOSIT_ID"]) is int:
            exelink.message(
                text=message_text,
                bot="MAIN",
                participantID=data["HIGH_DEPOSIT_ID"],
                reset=True,
                userID=message.from_user.id
            )
        else:
            for userID in lpsql.search("shopkeepers", "storeID", data["HIGH_DEPOSIT_ID"], True):
                exelink.message(
                    text=message_text,
                    bot="LPSB",
                    participantID=userID["userID"],
                    userID=message.from_user.id
                )
                await sleep(1/30)
        await state.clear()
        await message.answer(txt.LPAA.DEPOSIT.HIGH.OK)
        tracker.log(
            command=("HIGH_DEPOSIT", F.LIGHTGREEN_EX),
            status=("CONFIRM", F.LIGHTGREEN_EX + S.BRIGHT),
            from_user=f.collect_FU(message)
        )
    except Exception as e:
        tracker.error(
            e=e,
            userID=message.from_user.id
        )
