from aiogram import Router
from aiogram.types import Message, CallbackQuery
from aiogram.filters.command import Command
from aiogram.fsm.context import FSMContext
from aiogram import F as mF

from colorama import Fore as F, Style as S

from scripts import f, firewall3, tracker, exelink, lpsql
from scripts.j2 import fromfile as j_fromfile
from data import config as cfg, txt

import source.MAIN._keyboards as main_keyboard
from source.MAIN._states import *


rtr = Router()
config = [j_fromfile(cfg.PATHS.LAUNCH_SETTINGS)["config_v"]]
firewall3 = firewall3.FireWall('MAIN')
db = lpsql.DataBase("lypay_database.db", lpsql.Tables.MAIN)
print("MAIN/transfer router")


@rtr.message(mF.text == "📤 Перевод пользователю")
async def transfer(message: Message):
    try:
        f.update_config(config, [txt, cfg, main_keyboard])
        if message.from_user.id in db.searchall("users", "ID"):
            firewall_status = firewall3.check(message.from_user.id)
            if firewall_status == firewall3.WHITE_ANCHOR:
                await message.answer(txt.MAIN.TRANSFER.START_0,
                                     reply_markup=main_keyboard.update_keyboard(message.from_user.id, True))
                m_id = (await message.answer(txt.MAIN.TRANSFER.START.format(code=message.from_user.id),
                                             reply_markup=main_keyboard.transferCMD)).message_id
                exelink.sublist(
                    mode='add',
                    name='ccc/main',
                    key=message.chat.id,
                    data=m_id,
                    userID=message.from_user.id
                )
                tracker.log(
                    command=("TRANSFER", F.GREEN + S.NORMAL),
                    status=("START", F.GREEN + S.DIM),
                    from_user=f.collect_FU(message)
                )
            elif firewall_status == firewall3.BLACK_ANCHOR:
                tracker.black(f.collect_FU(message))
                await message.answer(txt.MAIN.CMD.IN_BLACKLIST)
            else:
                tracker.gray(f.collect_FU(message))
                await message.answer(txt.MAIN.CMD.NOT_IN_WHITELIST)
        else:
            tracker.log(
                command=("TRANSFER", F.GREEN + S.NORMAL),
                status=("NOT_REGISTERED", F.RED + S.DIM),
                from_user=f.collect_FU(message)
            )
            await message.answer(txt.MAIN.REGISTRATION.NOT_REGISTERED)
    except Exception as e:
        tracker.error(
            e=e,
            userID=message.from_user.id
        )


@rtr.callback_query(mF.data == "transfer_qr_cb")
async def transfer_proceed_qr(callback: CallbackQuery, state: FSMContext):
    try:
        f.update_config(config, [txt, cfg, main_keyboard])
        await callback.message.edit_text(txt.MAIN.TRANSFER.QR_ROUTE)
        await callback.answer()
        await state.update_data(MODE=0)
        await state.set_state(TransferFSM.USER)
        tracker.log(
            command=("TRANSFER", F.GREEN + S.NORMAL),
            status=("QR_ROUTE", F.YELLOW + S.DIM),
            from_user=f.collect_FU(callback)
        )
    except Exception as e:
        tracker.error(
            e=e,
            userID=callback.from_user.id
        )


@rtr.callback_query(mF.data == "transfer_tag_cb")
async def transfer_proceed_tag(callback: CallbackQuery, state: FSMContext):
    try:
        f.update_config(config, [txt, cfg, main_keyboard])
        await callback.message.edit_text(txt.MAIN.TRANSFER.TAG_ROUTE.format(tag=callback.from_user.username))
        await callback.answer()
        await state.update_data(MODE=1)
        await state.set_state(TransferFSM.USER)
        tracker.log(
            command=("TRANSFER", F.GREEN + S.NORMAL),
            status=("TAG_ROUTE", F.YELLOW + S.DIM),
            from_user=f.collect_FU(callback)
        )
    except Exception as e:
        tracker.error(
            e=e,
            userID=callback.from_user.id
        )


@rtr.callback_query(mF.data == "transfer_name_cb")
async def transfer_proceed_name(callback: CallbackQuery, state: FSMContext):
    try:
        f.update_config(config, [txt, cfg, main_keyboard])
        await callback.message.edit_text(txt.MAIN.TRANSFER.NAME_ROUTE)
        await callback.answer()
        await state.update_data(MODE=2)
        await state.set_state(TransferFSM.USER)
        tracker.log(
            command=("TRANSFER", F.GREEN + S.NORMAL),
            status=("NAME_ROUTE", F.YELLOW + S.DIM),
            from_user=f.collect_FU(callback)
        )
    except Exception as e:
        tracker.error(
            e=e,
            userID=callback.from_user.id
        )


@rtr.message(TransferFSM.USER, mF.text)
async def transfer_get_user(message: Message, state: FSMContext):
    try:
        f.update_config(config, [txt, cfg, main_keyboard])
        text = message.text.replace(' ', '').replace('\n', '').replace('@', '')
        ok = False
        mode = (await state.get_data())["MODE"]
        if mode == 0:  # by id
            try:
                text = int(text)
                if text not in db.searchall("users", "ID"):
                    await message.answer(txt.MAIN.TRANSFER.USER_NOT_REGISTERED)
                else:
                    ok = True
                tracker.log(
                    command=("TRANSFER", F.GREEN + S.NORMAL),
                    status=("ID", F.GREEN + S.DIM),
                    from_user=f.collect_FU(message)
                )
            except ValueError:
                await message.answer(txt.MAIN.TRANSFER.BAD_FORMAT)
                tracker.log(
                    command=("TRANSFER", F.GREEN + S.NORMAL),
                    status=("ID", F.RED + S.DIM),
                    from_user=f.collect_FU(message)
                )
        elif mode == 1:  # by tag
            text = text.replace('@', '').replace('https://t.me/', '')
            for userID in db.searchall("users", "ID"):
                search_tag = db.search("users", "ID", userID)["tag"]
                if search_tag is not None and search_tag.lower() == text.lower():
                    ok = True
                    text = userID
                    tracker.log(
                        command=("TRANSFER", F.GREEN + S.NORMAL),
                        status=("TAG", F.GREEN + S.DIM),
                        from_user=f.collect_FU(message)
                    )
                    break
            if not ok:
                await message.answer(txt.MAIN.TRANSFER.USER_NOT_REGISTERED)
                tracker.log(
                    command=("TRANSFER", F.GREEN + S.NORMAL),
                    status=("TAG", F.RED + S.DIM),
                    from_user=f.collect_FU(message)
                )
        elif mode == 2:  # by name
            text = text.capitalize()
            found = list()
            for userID in db.searchall("users", "ID"):
                if db.search("users", "ID", userID)["name"].split()[-1] == text:
                    ok = True
                    found.append(userID)
            if ok:
                if len(found) == 1:
                    text = found[0]
                    tracker.log(
                        command=("TRANSFER", F.GREEN + S.NORMAL),
                        status=("NAME", F.GREEN + S.DIM),
                        from_user=f.collect_FU(message)
                    )
                else:
                    await message.answer(txt.MAIN.TRANSFER.NAMESAKE_WARNING)
                    await state.clear()
                    ok = False
                    tracker.log(
                        command=("TRANSFER", F.GREEN + S.NORMAL),
                        status=("EQUAL_NAME", F.RED + S.NORMAL),
                        from_user=f.collect_FU(message)
                    )
            else:
                await message.answer(txt.MAIN.TRANSFER.USER_NOT_REGISTERED)
                tracker.log(
                    command=("TRANSFER", F.GREEN + S.NORMAL),
                    status=("NAME", F.RED + S.DIM),
                    from_user=f.collect_FU(message)
                )
        else:
            mode = None
            await message.answer(txt.MAIN.TRANSFER.BAD_FORMAT)
            tracker.log(
                command=("TRANSFER", F.GREEN + S.NORMAL),
                status=("BAD_FORMAT", F.RED + S.DIM),
                from_user=f.collect_FU(message)
            )

        if ok:   # при успехе заменить text на найденный id
            if text == message.from_user.id:
                await message.answer(txt.MAIN.TRANSFER.SELF)
            else:
                await state.set_state(TransferFSM.CONFIRM1)
                user = db.search("users", "ID", text)
                if mode == 1:
                    await message.answer(txt.MAIN.TRANSFER.CONFIRM1.NAME_LESS.format(
                        tag=user["tag"]
                    ))
                elif mode == 2:
                    await message.answer(txt.MAIN.TRANSFER.CONFIRM1.TAG_LESS.format(
                        name=user["name"],
                        group=user["class"]
                    ))
                else:
                    await message.answer(txt.MAIN.TRANSFER.CONFIRM1.FULL.format(
                        name=user["name"],
                        group=user["class"],
                        tag=user["tag"]
                    ))
                await state.update_data(MODE=mode)
                await state.update_data(USER=text)
    except Exception as e:
        tracker.error(
            e=e,
            userID=message.from_user.id
        )


@rtr.message(TransferFSM.CONFIRM1, Command("confirm"))
async def transfer_confirm1(message: Message, state: FSMContext):
    try:
        f.update_config(config, [txt, cfg, main_keyboard])
        await state.set_state(TransferFSM.INPUT)
        await message.answer(txt.MAIN.TRANSFER.INPUT.format(
            balance=db.balance_view(message.from_user.id)
        ))
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
        f.update_config(config, [txt, cfg, main_keyboard])
        censor = tracker.censor(
            from_user=f.collect_FU(message),
            text=message.text
        )
        if not censor:
            await message.answer(txt.MAIN.CMD.CENSOR_BLACK)
            return
        try:
            amount = int(message.text)
            if amount > 0:
                amount_ = db.balance_view(message.from_user.id)
                to_ = db.search("users", "ID", (await state.get_data())["USER"])
                if amount <= amount_:
                    await state.update_data(INPUT=amount)
                    mode = (await state.get_data())["MODE"]
                    if mode == 1:
                        await message.answer(txt.MAIN.TRANSFER.CONFIRM2.NAME_LESS.format(
                            tag='@'+to_["tag"],
                            amount=f"{amount} {cfg.VALUTA.SHORT}"
                        ))
                    elif mode == 2:
                        await message.answer(txt.MAIN.TRANSFER.CONFIRM2.TAG_LESS.format(
                            name=to_["name"],
                            group=to_["class"],
                            amount=f"{amount} {cfg.VALUTA.SHORT}"
                        ))
                    else:
                        await message.answer(txt.MAIN.TRANSFER.CONFIRM2.FULL.format(
                            name=to_["name"],
                            group=to_["class"],
                            tag='@'+to_["tag"] if to_["tag"] else '–',
                            amount=f"{amount} {cfg.VALUTA.SHORT}"
                        ))
                    await state.set_state(TransferFSM.CONFIRM2)
                    tracker.log(
                        command=("TRANSFER", F.GREEN + S.NORMAL),
                        status=("AMOUNT", F.GREEN + S.DIM),
                        from_user=f.collect_FU(message)
                    )
                else:
                    await message.answer(txt.MAIN.TRANSFER.NOT_ENOUGH)
                    tracker.log(
                        command=("TRANSFER", F.GREEN + S.NORMAL),
                        status=("NOT_ENOUGH_MONEY", F.RED + S.DIM),
                        from_user=f.collect_FU(message)
                    )
            else:
                await message.answer(txt.MAIN.TRANSFER.SUBZERO_INPUT_VALUE)
                tracker.log(
                    command=("TRANSFER", F.GREEN + S.NORMAL),
                    status=("AMOUNT_SUBZERO", F.RED + S.DIM),
                    from_user=f.collect_FU(message)
                )
        except ValueError:
            await message.answer(txt.MAIN.TRANSFER.BAD_FORMAT)
    except Exception as e:
        tracker.error(
            e=e,
            userID=message.from_user.id
        )


@rtr.message(TransferFSM.CONFIRM2, Command("confirm"))
async def transfer_confirm2(message: Message, state: FSMContext):
    try:
        f.update_config(config, [txt, cfg, main_keyboard])
        data = await state.get_data()
        from_ = db.search("users", "ID", message.from_user.id)
        db.transfer(message.from_user.id, data["USER"], data["INPUT"])

        await message.bot.send_message(
            text=txt.MAIN.TRANSFER.UPDATE.format(
                name=from_["name"],
                group=from_["class"],
                tag='@' + from_["tag"] if from_["tag"] else '',
                amount=('+' if data["INPUT"] >= 0 else '') + str(data["INPUT"])
            ),
            chat_id=data["USER"]
        )
        ''' до v2.2:
        exelink.message(
            text=txt.MAIN.TRANSFER.UPDATE.format(
                name=from_["name"],
                group=from_["class"],
                tag='@'+from_["tag"] if from_["tag"] else '',
                amount=('+' if data["INPUT"] >= 0 else '') + str(data["INPUT"])
            ),
            bot='MAIN',
            participantID=data["USER"],
            userID=message.from_user.id
        )
        '''
        await message.answer(txt.MAIN.TRANSFER.OK % ('-' + str(data["INPUT"])),
                             reply_markup=main_keyboard.update_keyboard(message.from_user.id))

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
