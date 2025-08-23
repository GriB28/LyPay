from aiogram import Router
from aiogram import F as mF
from aiogram.types import Message, FSInputFile, LinkPreviewOptions
from aiogram.filters.command import Command, CommandStart
from aiogram.fsm.context import FSMContext

from colorama import Fore as F, Style as S
from datetime import datetime

from scripts import f, firewall3, tracker, exelink, j2, lpsql
from data import config as cfg, txt

import source.MAIN._keyboards as main_keyboard
from source.MAIN._states import *


rtr = Router()
config = [j2.fromfile(cfg.PATHS.LAUNCH_SETTINGS)["config_v"]]
firewall3 = firewall3.FireWall('MAIN', silent=False)
print("MAIN/abstract router")


@rtr.message(CommandStart(deep_link=False))
async def launch(message: Message, state: FSMContext):
    try:
        f.update_config(config, [txt, cfg, main_keyboard])
        firewall_status = firewall3.check(message.from_user.id)
        if firewall_status == firewall3.WHITE_ANCHOR:
            tracker.log(
                command=("START", F.GREEN + S.BRIGHT),
                from_user=f.collect_FU(message)
            )
            await message.answer(txt.MAIN.CMD.START, reply_markup=main_keyboard.startCMD)

            if message.from_user.id not in lpsql.searchall("users", "ID"):
                m_id = (await message.answer(
                    txt.MAIN.REGISTRATION.NEW,
                    reply_markup=main_keyboard.registerCMD,
                    link_preview_options=LinkPreviewOptions(is_disabled=True)
                )).message_id
                exelink.sublist(
                    mode='add',
                    name='ccc/main',
                    key=message.chat.id,
                    data=m_id,
                    userID=message.from_user.id
                )
                exelink.sublist(
                    mode='add',
                    name='hi_frog',
                    key=message.from_user.id,
                    data=datetime.now().strftime('%Y'),
                    userID=message.from_user.id
                )
                await state.set_state(RegisterFSM.STATE0)
            else:
                read_sublist = await f.read_sublist("hi_frog")
                uid = str(message.from_user.id)
                date = datetime.now().strftime('%Y')
                if read_sublist is None or uid not in read_sublist.keys() or read_sublist[uid] != date:
                    await message.answer_sticker(cfg.MEDIA.FROG_HELLO)
                    await message.answer(txt.MAIN.REGISTRATION.HI_FROG.format(
                        name=' '.join(lpsql.search("users", "ID", message.from_user.id)["name"].split()[:-1])
                    ))
                    exelink.sublist(
                        mode='add',
                        name='hi_frog',
                        key=message.from_user.id,
                        data=date,
                        userID=message.from_user.id
                    )
                await message.answer(txt.MAIN.REGISTRATION.EXISTS,
                                     reply_markup=main_keyboard.update_keyboard(message.from_user.id))
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


@rtr.message(mF.text.in_(("↩️ Отмена", "/cancel")))
async def cancel(message: Message, state: FSMContext):
    try:
        f.update_config(config, [txt, cfg, main_keyboard])
        firewall_status = firewall3.check(message.from_user.id)
        if firewall_status == firewall3.WHITE_ANCHOR:
            current = await state.get_state()
            tracker.log(
                command=("CANCELLED", F.RED + S.BRIGHT),
                from_user=f.collect_FU(message)
            )
            c = None
            if current in RegisterFSM.__states__:
                await message.answer(txt.MAIN.REGISTRATION.CANCEL,
                                     reply_markup=main_keyboard.update_keyboard(message.from_user.id))
            elif current in TransferFSM.__states__:
                await message.answer(txt.MAIN.TRANSFER.CANCEL,
                                     reply_markup=main_keyboard.update_keyboard(message.from_user.id))
            else:
                c = 0
            for key, value in (await f.read_sublist("ccc/main")).items():
                if key == str(message.chat.id):
                    exelink.ccc_remove_keyboard(
                        bot='main',
                        chat_id=key,
                        message_id=value,
                        text="[CCC] Действие отменено.",
                        userID=message.from_user.id
                    )
                    exelink.sublist(
                        mode='remove',
                        name='ccc/main',
                        key=key,
                        data=value,
                        userID=message.from_user.id
                    )
                    if c is not None:
                        c += 1
            if c is not None and c == 0:
                await message.answer("Действие отменено.",
                                     reply_markup=main_keyboard.update_keyboard(message.from_user.id))
            await state.clear()
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


@rtr.message(mF.text == "💳 Пополнить баланс")
async def deposit(message: Message):
    try:
        f.update_config(config, [txt, cfg, main_keyboard])
        if (await j2.fromfile_async(cfg.PATHS.LAUNCH_SETTINGS))["main_can_deposit"]:
            if message.from_user.id in lpsql.searchall("users", "ID"):
                firewall_status = firewall3.check(message.from_user.id)
                if firewall_status == firewall3.WHITE_ANCHOR:
                    tracker.log(
                        command=("DEPOSIT", F.CYAN + S.BRIGHT),
                        status=("SUCCESS", F.GREEN + S.BRIGHT),
                        from_user=f.collect_FU(message)
                    )
                    qr = lpsql.search("qr", "userID", message.from_user.id)
                    if qr is None or qr["fileID_main"] is None:
                        fileid = (await message.answer_photo(FSInputFile(cfg.PATHS.QR + str(message.from_user.id) + '.png'),
                                                             txt.MAIN.DEPOSIT.MAIN, has_spoiler=True)).photo[-1].file_id
                        lpsql.update("qr", "userID", message.from_user.id, "fileID_main", fileid)
                    else:
                        await message.answer_photo(qr["fileID_main"], txt.MAIN.DEPOSIT.MAIN, has_spoiler=True)
                elif firewall_status == firewall3.BLACK_ANCHOR:
                    tracker.black(f.collect_FU(message))
                    await message.answer(txt.MAIN.CMD.IN_BLACKLIST)
                else:
                    tracker.gray(f.collect_FU(message))
                    await message.answer(txt.MAIN.CMD.NOT_IN_WHITELIST)
            else:
                tracker.log(
                    command=("DEPOSIT", F.CYAN + S.BRIGHT),
                    status=("NOT_REGISTERED", F.RED),
                    from_user=f.collect_FU(message)
                )
                await message.answer(txt.MAIN.REGISTRATION.NOT_REGISTERED)
        else:
            tracker.log(
                command=("DEPOSIT", F.CYAN + S.BRIGHT),
                status=("SETTINGS_ACTION_FORBIDDEN", F.RED),
                from_user=f.collect_FU(message)
            )
            await message.answer(txt.MAIN.DEPOSIT.FORBIDDEN_BY_SETTINGS)
    except Exception as e:
        tracker.error(
            e=e,
            userID=message.from_user.id
        )


@rtr.message(mF.text.in_(("💰 Баланс", "😱 Баланс")))
async def balance(message: Message):
    try:
        f.update_config(config, [txt, cfg, main_keyboard])
        firewall_status = firewall3.check(message.from_user.id)
        if firewall_status == firewall3.WHITE_ANCHOR:
            try:
                balance_ = lpsql.balance_view(message.from_user.id)
                await message.answer(f"Ваш баланс: {balance_ if balance_ else 0} {cfg.VALUTA.SHORT}")
                tracker.log(
                    command=("BALANCE", F.MAGENTA + S.DIM),
                    from_user=f.collect_FU(message)
                )
            except lpsql.errors.IDNotFound:
                await message.answer(txt.MAIN.REGISTRATION.NOT_REGISTERED)
                tracker.log(
                    command=("BALANCE", F.MAGENTA + S.DIM),
                    status=("NOT_REGISTERED", F.RED + S.DIM),
                    from_user=f.collect_FU(message)
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


@rtr.message(mF.text == "⚙️ Авторы")
async def credits_(message: Message):
    try:
        f.update_config(config, [txt, cfg, main_keyboard])
        await message.answer_photo(cfg.MEDIA.CREDITS, caption=txt.MAIN.CREDITS.TEXT)
        tracker.log(
            command=("CREDITS", F.LIGHTMAGENTA_EX + S.DIM),
            from_user=f.collect_FU(message)
        )
    except Exception as e:
        tracker.error(
            e=e,
            userID=message.from_user.id
        )


@rtr.message(Command("get_qr"))
async def get_qr(message: Message):
    try:
        f.update_config(config, [txt, cfg, main_keyboard])
        firewall_status = firewall3.check(message.from_user.id)
        if firewall_status == firewall3.WHITE_ANCHOR:
            user = lpsql.search("users", "ID", message.from_user.id)
            if user is not None:
                await message.answer(txt.MAIN.CMD.QR_WARNING.format(
                    name=user["name"],
                    tag='@'+user["tag"] if user["tag"] else '–'
                ))
                qr = lpsql.search("qr", "userID", message.from_user.id)
                if qr is None or qr["fileID_main"] is None:
                    fileid = (await message.answer_photo(FSInputFile(cfg.PATHS.QR + str(message.from_user.id) + '.png'),
                                                         has_spoiler=True)).photo[-1].file_id
                    lpsql.update("qr", "userID", message.from_user.id, "fileID_main", fileid)
                else:
                    await message.answer_photo(qr["fileID_main"], has_spoiler=True)
                tracker.log(
                    command=("GET_QR", F.BLACK + S.BRIGHT),
                    from_user=f.collect_FU(message)
                )
            else:
                tracker.log(
                    command=("GET_QR", F.BLACK + S.BRIGHT),
                    status=("NOT_REGISTERED", F.RED),
                    from_user=f.collect_FU(message)
                )
                await message.answer(txt.MAIN.REGISTRATION.NOT_REGISTERED)
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


# @rtr.message(Command("delete"))
async def delete_acc(message: Message):
    try:
        try:
            lpsql.delete_user(message.from_user.id)
            await message.answer("Account deleted.")
        except lpsql.errors.IDNotFound:
            await message.answer("Account doesn't exist.")
    except Exception as e:
        tracker.error(
            e=e,
            userID=message.from_user.id
        )


@rtr.message(Command("help"))
async def help_(message: Message):
    try:
        f.update_config(config, [txt, cfg, main_keyboard])
        await message.answer_document(cfg.MEDIA.MANUAL.MAIN, caption=txt.MAIN.CMD.MANUAL)
        tracker.log(
            command=("HELP", F.LIGHTBLUE_EX),
            from_user=f.collect_FU(message)
        )
    except Exception as e:
        tracker.error(
            e=e,
            userID=message.from_user.id
        )
