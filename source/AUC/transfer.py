from aiogram import Router
from aiogram import F as mF
from aiogram.types import Message
from aiogram.filters.command import Command
from aiogram.fsm.context import FSMContext

from colorama import Fore as F, Style as S
from random import randint

from scripts import f, firewall3, tracker, lpsql
from scripts.j2 import fromfile as j_fromfile
from data import txt, config as cfg

from source.AUC._states import *


rtr = Router()
firewall3 = firewall3.FireWall('LPSB')
config = [j_fromfile(cfg.PATHS.LAUNCH_SETTINGS)["config_v"]]
db = lpsql.DataBase("lypay_database.db", lpsql.Tables.MAIN)
print("AUC/transfer router")


@rtr.message(Command("transfer"))
async def transfer(message: Message, state: FSMContext):
    try:
        f.update_config(config, [txt, cfg])
        firewall_status = firewall3.check(message.from_user.id)
        if firewall_status == firewall3.WHITE_ANCHOR:
            await message.answer(txt.AUC.TRANSFER.START)
            await state.set_state(TransferFSM.STORE)
            tracker.log(
                command=("TRANSFER", F.GREEN + S.NORMAL),
                status=("START", F.GREEN + S.DIM),
                from_user=f.collect_FU(message)
            )
        elif firewall_status == firewall3.BLACK_ANCHOR:
            tracker.black(f.collect_FU(message))
            await message.answer(txt.AUC.CMD.IN_BLACKLIST)
        else:
            tracker.gray(f.collect_FU(message))
            await message.answer(txt.AUC.CMD.NOT_IN_WHITELIST)
            await message.answer_sticker(cfg.MEDIA.NOT_IN_LPSB_WHITELIST_FROGS[
                                             randint(0, len(cfg.MEDIA.NOT_IN_LPSB_WHITELIST_FROGS)-1)
                                         ])
    except Exception as e:
        tracker.error(
            e=e,
            userID=message.from_user.id
        )


@rtr.message(TransferFSM.STORE, mF.text)
async def transfer_get_store(message: Message, state: FSMContext):
    try:
        f.update_config(config, [txt, cfg])
        text = message.text.lower()
        try:
            store = db.search("shopkeepers", "userID", message.from_user.id)["storeID"]
            try:
                if text not in db.searchall("stores", "ID"):
                    await message.answer(txt.AUC.TRANSFER.NOT_FOUND)
                    tracker.log(
                        command=("TRANSFER", F.GREEN + S.NORMAL),
                        status=("NOT_FOUND", F.RED + S.DIM),
                        from_user=f.collect_FU(message)
                    )
                elif text == store:
                    await message.answer(txt.AUC.TRANSFER.SELF)
                    tracker.log(
                        command=("TRANSFER", F.GREEN + S.NORMAL),
                        status=("SELF", F.RED + S.DIM),
                        from_user=f.collect_FU(message)
                    )
                else:
                    host = db.search("users", "ID", db.search("stores", "ID", text)["hostID"])
                    if host is None:
                        host = {"name": "незарегистрированный пользователь", "class": "–", "tag": None}

                    await message.answer(txt.AUC.TRANSFER.CONFIRM1.format(
                        store=text,
                        name=host["name"],
                        group=host["class"],
                        tag='@'+host["tag"] if host["tag"] else ''
                    ))
                    await state.update_data(STORE=text)
                    await state.set_state(TransferFSM.CONFIRM1)
                    tracker.log(
                        command=("TRANSFER", F.GREEN + S.NORMAL),
                        status=("STORE", F.BLUE + S.DIM),
                        from_user=f.collect_FU(message)
                    )
            except Exception as e:
                print(e.args)
                await message.answer(txt.AUC.TRANSFER.BAD_FORMAT)
                tracker.log(
                    command=("TRANSFER", F.RED + S.NORMAL),
                    status=("FAIL", F.RED + S.NORMAL),
                    from_user=f.collect_FU(message)
                )
        except:
            await message.answer(txt.AUC.CMD.FAILED)
            tracker.log(
                command=("TRANSFER", F.RED + S.NORMAL),
                status=("FAIL", F.RED + S.NORMAL),
                from_user=f.collect_FU(message)
            )
    except Exception as e:
        tracker.error(
            e=e,
            userID=message.from_user.id
        )


@rtr.message(TransferFSM.CONFIRM1, Command("confirm"))
async def transfer_confirm1(message: Message, state: FSMContext):
    try:
        f.update_config(config, [txt, cfg])
        await state.set_state(TransferFSM.INPUT)
        await message.answer(txt.AUC.TRANSFER.INPUT)
        tracker.log(
            command=("TRANSFER", F.GREEN + S.NORMAL),
            status=("CONFIRM_1", F.YELLOW + S.DIM),
            from_user=f.collect_FU(message)
        )
    except Exception as e:
        tracker.error(
            e=e,
            userID=message.from_user.id
        )


@rtr.message(TransferFSM.INPUT, mF.text)
async def transfer_get_amount(message: Message, state: FSMContext):
    try:
        f.update_config(config, [txt, cfg])
        try:
            amount = int(message.text)
            if amount > 0:
                data = await state.get_data()
                if amount <= db.balance_view(db.search("shopkeepers", "userID", message.from_user.id)["storeID"]):
                    await state.update_data(INPUT=amount)
                    await message.answer(txt.AUC.TRANSFER.CONFIRM2.format(
                        store=data["STORE"],
                        amount=amount
                    ))
                    await state.set_state(TransferFSM.CONFIRM2)
                    tracker.log(
                        command=("TRANSFER", F.GREEN + S.NORMAL),
                        status=("AMOUNT", F.GREEN + S.DIM),
                        from_user=f.collect_FU(message)
                    )
                else:
                    await message.answer(txt.AUC.TRANSFER.NOT_ENOUGH)
                    tracker.log(
                        command=("TRANSFER", F.GREEN + S.NORMAL),
                        status=("NOT_ENOUGH_MONEY", F.RED + S.DIM),
                        from_user=f.collect_FU(message)
                    )
            else:
                await message.answer(txt.AUC.TRANSFER.SUBZERO_INPUT_VALUE)
                tracker.log(
                    command=("TRANSFER", F.GREEN + S.NORMAL),
                    status=("AMOUNT_SUBZERO", F.RED + S.DIM),
                    from_user=f.collect_FU(message)
                )
        except ValueError:
            await message.answer(txt.AUC.TRANSFER.BAD_FORMAT)
            tracker.log(
                command=("TRANSFER", F.GREEN + S.NORMAL),
                status=("AMOUNT_BAD_FORMAT", F.RED + S.DIM),
                from_user=f.collect_FU(message)
            )
    except Exception as e:
        tracker.error(
            e=e,
            userID=message.from_user.id
        )


@rtr.message(TransferFSM.CONFIRM2, Command("confirm"))
async def transfer_confirm2(message: Message, state: FSMContext):
    try:
        f.update_config(config, [txt, cfg])
        data = await state.get_data()
        id_ = db.search("shopkeepers", "userID", message.from_user.id)["storeID"]

        db.transfer(id_, data["STORE"], data["INPUT"])

        for userID in db.searchall("shopkeepers", "userID"):
            if db.search("shopkeepers", "userID", userID)["storeID"] == data["STORE"]:
                await message.bot.send_message(
                    text=txt.AUC.TRANSFER.UPDATE.format(
                        store=id_,
                        amount=('+' if data["INPUT"] >= 0 else '') + str(data["INPUT"])
                    ),
                    chat_id=userID
                )
                ''' до v2.2:
                exelink.message(
                    text=txt.AUC.TRANSFER.UPDATE.format(
                        store=id_,
                        amount=('+' if data["INPUT"] >= 0 else '') + str(data["INPUT"])
                    ),
                    bot="LPSB",
                    participantID=userID,
                    userID=message.from_user.id
                )
                '''
        await message.answer(txt.AUC.TRANSFER.OK.format('-' + str(data["INPUT"])))

        await state.clear()
        tracker.log(
            command=("TRANSFER", F.GREEN + S.NORMAL),
            status=("SUCCESSFUL", F.YELLOW + S.DIM),
            from_user=f.collect_FU(message)
        )
    except Exception as e:
        tracker.error(
            e=e,
            userID=message.from_user.id
        )
