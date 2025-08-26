from aiogram import Router
from aiogram import F as mF
from aiogram.filters.command import Command
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from colorama import Fore as F, Style as S

from scripts import f, firewall3, tracker, lpsql, exelink
from scripts.j2 import fromfile as j_fromfile
from data import config as cfg, txt

from source.LPAA._states import *
import source.LPAA._keyboards as main_keyboard


rtr = Router()
config = [j_fromfile(cfg.PATHS.LAUNCH_SETTINGS)["config_v"]]
firewall3_main, firewall3_lpsb = firewall3.FireWall("MAIN"), firewall3.FireWall("LPSB")
db = lpsql.DataBase("lypay_database.db", lpsql.Tables.MAIN)
print("LPAA/whitelist router")


@rtr.message(Command("whitelist"), mF.chat.id == cfg.HIGH_GROUP)
async def whitelist(message: Message, state: FSMContext):
    try:
        f.update_config(config, [txt, cfg, main_keyboard])
        message_to_MSG = await message.answer(txt.LPAA.WHITELIST.START, reply_markup=main_keyboard.whitelistCMD)
        exelink.sublist(
            mode='add',
            name='ccc/lpaa',
            key=message.chat.id,
            data=message_to_MSG.message_id,
            userID=message.from_user.id
        )
        await state.update_data(MSG=message_to_MSG)
        tracker.log(
            command=("WHITELIST", F.LIGHTGREEN_EX + S.BRIGHT),
            from_user=f.collect_FU(message)
        )
        await state.set_state(WhitelistFSM.BOT)
    except Exception as e:
        tracker.error(
            e=e,
            userID=message.from_user.id
        )


@rtr.callback_query(WhitelistFSM.BOT, mF.data == 'main_cb', mF.message.chat.id == cfg.HIGH_GROUP)
async def whitelist_main(callback: CallbackQuery, state: FSMContext):
    try:
        f.update_config(config, [txt, cfg, main_keyboard])
        await callback.message.edit_text(txt.LPAA.WHITELIST.MAIN)
        await callback.answer()
        await callback.message.answer(txt.LPAA.WHITELIST.USER_MAIN)
        await state.clear()
        exelink.sublist(
            mode='remove',
            name='ccc/lpaa',
            key=callback.message.chat.id,
            userID=callback.from_user.id
        )
        tracker.log(
            command=("WHITELIST", F.LIGHTGREEN_EX + S.BRIGHT),
            status=("MAIN", F.GREEN + S.BRIGHT),
            from_user=f.collect_FU(callback)
        )
    except Exception as e:
        tracker.error(
            e=e,
            userID=callback.from_user.id
        )


@rtr.callback_query(WhitelistFSM.BOT, mF.data == 'lpsb_cb', mF.message.chat.id == cfg.HIGH_GROUP)
async def whitelist_lpsb(callback: CallbackQuery, state: FSMContext):
    try:
        f.update_config(config, [txt, cfg, main_keyboard])
        await callback.message.edit_text(txt.LPAA.WHITELIST.LPSB)
        await callback.answer()
        await callback.message.answer(txt.LPAA.WHITELIST.USER_LPSB)
        await state.update_data(BOT="LPSB")
        await state.update_data(MSG=None)
        exelink.sublist(
            mode='remove',
            name='ccc/lpaa',
            key=callback.message.chat.id,
            userID=callback.from_user.id
        )
        await state.set_state(WhitelistFSM.USER)
        tracker.log(
            command=("WHITELIST", F.LIGHTGREEN_EX + S.BRIGHT),
            status=("LPSB", F.GREEN + S.BRIGHT),
            from_user=f.collect_FU(callback)
        )
    except Exception as e:
        tracker.error(
            e=e,
            userID=callback.from_user.id
        )


@rtr.message(WhitelistFSM.USER, mF.text, mF.chat.id == cfg.HIGH_GROUP)
async def whitelist_user(message: Message, state: FSMContext):
    try:
        f.update_config(config, [txt, cfg, main_keyboard])
        try:
            user = int(message.text)
            bot = (await state.get_data())["BOT"]
            white_list = firewall3_lpsb.list_white() if bot == "LPSB" else firewall3_main.list_white()
            if str(user) not in white_list:
                await state.update_data(USER=user)
                await state.set_state(WhitelistFSM.CONFIRM)
                js = db.search("users", "ID", user)
                if js is None:
                    js = {"name": "незарегистрированный пользователь", "class": "–", "tag": None}
                await message.answer(txt.LPAA.WHITELIST.CONFIRM.format(
                    name=js["name"],
                    group=js["class"],
                    tag='@'+js["tag"] if js["tag"] else '–'
                ))
                tracker.log(
                    command=("WHITELIST", F.LIGHTGREEN_EX + S.BRIGHT),
                    status=("USER", F.GREEN + S.BRIGHT),
                    from_user=f.collect_FU(message)
                )
            else:
                await message.answer(txt.LPAA.WHITELIST.ALREADY_IN)
                tracker.log(
                    command=("WHITELIST", F.LIGHTGREEN_EX + S.BRIGHT),
                    status=("USER_IN_LIST", F.GREEN + S.DIM),
                    from_user=f.collect_FU(message)
                )
                await state.clear()
        except:
            await message.answer(txt.LPAA.BAD_ARG)
            tracker.log(
                command=("WHITELIST", F.LIGHTGREEN_EX + S.BRIGHT),
                status=("BAD_ARG", F.RED + S.BRIGHT),
                from_user=f.collect_FU(message)
            )
    except Exception as e:
        tracker.error(
            e=e,
            userID=message.from_user.id
        )


@rtr.message(WhitelistFSM.CONFIRM, Command("confirm"), mF.chat.id == cfg.HIGH_GROUP)
async def whitelist_confirm(message: Message, state: FSMContext):
    try:
        f.update_config(config, [txt, cfg, main_keyboard])
        data = await state.get_data()
        bot = data["BOT"]
        fw = firewall3_lpsb if bot == "LPSB" else firewall3_main
        fw.add_white(data["USER"], f"manual request from LPAA by {message.from_user.id}")
        await message.answer(txt.LPAA.WHITELIST.END)
        await state.clear()
        tracker.log(
            command=("WHITELIST", F.LIGHTGREEN_EX + S.BRIGHT),
            status=("SUCCESS", F.LIGHTGREEN_EX + S.BRIGHT),
            from_user=f.collect_FU(message)
        )
    except Exception as e:
        tracker.error(
            e=e,
            userID=message.from_user.id
        )


# -=-=-=- BAN

@rtr.message(Command("ban"), mF.chat.id == cfg.HIGH_GROUP)
async def ban(message: Message, state: FSMContext):
    try:
        f.update_config(config, [txt, cfg, main_keyboard])
        await state.set_state(BanFSM.ID)
        await message.answer(txt.LPAA.BAN.START)
    except Exception as e:
        tracker.error(
            e=e,
            userID=message.from_user.id
        )


@rtr.message(BanFSM.ID, mF.text, mF.chat.id == cfg.HIGH_GROUP)
async def ban_choose(message: Message, state: FSMContext):
    try:
        f.update_config(config, [txt, cfg, main_keyboard])
        try:
            id_ = int(message.text)
            if id_ in db.searchall("users", "ID"):
                if firewall3_main.check(id_) == firewall3_main.BLACK_ANCHOR == firewall3_lpsb.check(id_):
                    await message.answer(txt.LPAA.BAN.ALREADY)
                    tracker.log(
                        command=("BAN", F.LIGHTRED_EX + S.BRIGHT),
                        status=("ALREADY", F.BLUE + S.BRIGHT),
                        from_user=f.collect_FU(message)
                    )
                else:
                    js_ = db.search("users", "ID", id_)
                    await message.answer(txt.LPAA.BAN.CONFIRM.format(
                        name=js_["name"],
                        group=js_["class"],
                        tag='@'+js_["tag"] if js_["tag"] else '–'
                    ))
                    await state.update_data(ID=id_)
                    await state.set_state(BanFSM.CONFIRM)
                    tracker.log(
                        command=("BAN", F.LIGHTRED_EX + S.BRIGHT),
                        status=("ID", F.GREEN + S.NORMAL),
                        from_user=f.collect_FU(message)
                    )
            else:
                await message.answer(txt.LPAA.WRONG)
                tracker.log(
                    command=("BAN", F.LIGHTCYAN_EX + S.BRIGHT),
                    status=("ID_NOT_IN_DATABASE", F.LIGHTRED_EX + S.NORMAL),
                    from_user=f.collect_FU(message)
                )
        except:
            tracker.log(
                command=("BAN", F.LIGHTRED_EX + S.BRIGHT),
                status=("BAD_ID", F.LIGHTRED_EX + S.NORMAL),
                from_user=f.collect_FU(message)
            )
            await message.answer(txt.LPAA.BAD_ARG)
    except Exception as e:
        tracker.error(
            e=e,
            userID=message.from_user.id
        )


@rtr.message(BanFSM.CONFIRM, Command("confirm"), mF.chat.id == cfg.HIGH_GROUP)
async def ban_end(message: Message, state: FSMContext):
    try:
        f.update_config(config, [txt, cfg, main_keyboard])
        await message.answer(txt.LPAA.BAN.END)
        data = (await state.get_data())["ID"]
        firewall3_main.add_black(data)
        firewall3_lpsb.add_black(data)
        await state.clear()
        tracker.log(
            command=("BAN", F.LIGHTRED_EX + S.BRIGHT),
            status=("BAN!", F.LIGHTRED_EX + S.NORMAL),
            from_user=f.collect_FU(message)
        )
    except Exception as e:
        tracker.error(
            e=e,
            userID=message.from_user.id
        )


# -=-=-=- PARDON

@rtr.message(Command("pardon"), mF.chat.id == cfg.HIGH_GROUP)
async def pardon(message: Message, state: FSMContext):
    try:
        f.update_config(config, [txt, cfg, main_keyboard])
        tracker.log(
            command=("PARDON", F.LIGHTCYAN_EX + S.BRIGHT),
            status=("PREPARING", F.LIGHTBLUE_EX + S.NORMAL),
            from_user=f.collect_FU(message)
        )
        await state.set_state(PardonFSM.ID)
        await message.answer(txt.LPAA.PARDON.START)
    except Exception as e:
        tracker.error(
            e=e,
            userID=message.from_user.id
        )


@rtr.message(PardonFSM.ID, mF.text, mF.chat.id == cfg.HIGH_GROUP)
async def pardon_choose(message: Message, state: FSMContext):
    try:
        f.update_config(config, [txt, cfg, main_keyboard])
        try:
            id_ = int(message.text)
            if id_ in db.searchall("users", "ID"):
                if firewall3_main.check(id_) == firewall3_main.WHITE_ANCHOR == firewall3_lpsb.check(id_):
                    await message.answer(txt.LPAA.PARDON.ALREADY)
                    tracker.log(
                        command=("PARDON", F.LIGHTCYAN_EX + S.BRIGHT),
                        status=("ALREADY", F.BLUE + S.BRIGHT),
                        from_user=f.collect_FU(message)
                    )
                else:
                    js_ = db.search("users", "ID", id_)
                    await message.answer(txt.LPAA.PARDON.CONFIRM.format(
                        name=js_["name"],
                        group=js_["class"],
                        tag='@'+js_["tag"] if js_["tag"] else '–'
                    ))
                    await state.update_data(ID=id_)
                    await state.set_state(PardonFSM.CONFIRM)
                    tracker.log(
                        command=("PARDON", F.LIGHTCYAN_EX + S.BRIGHT),
                        status=("ID", F.GREEN + S.NORMAL),
                        from_user=f.collect_FU(message)
                    )
            else:
                await message.answer(txt.LPAA.WRONG)
                tracker.log(
                    command=("PARDON", F.LIGHTCYAN_EX + S.BRIGHT),
                    status=("ID_NOT_IN_DATABASE", F.LIGHTRED_EX + S.NORMAL),
                    from_user=f.collect_FU(message)
                )
        except:
            tracker.log(
                command=("PARDON", F.LIGHTCYAN_EX + S.BRIGHT),
                status=("BAD_ID", F.LIGHTRED_EX + S.NORMAL),
                from_user=f.collect_FU(message)
            )
            await message.answer(txt.LPAA.BAD_ARG)
    except Exception as e:
        tracker.error(
            e=e,
            userID=message.from_user.id
        )


@rtr.message(PardonFSM.CONFIRM, Command("confirm"), mF.chat.id == cfg.HIGH_GROUP)
async def pardon_end(message: Message, state: FSMContext):
    try:
        f.update_config(config, [txt, cfg, main_keyboard])
        await message.answer(txt.LPAA.PARDON.END)
        data = (await state.get_data())["ID"]
        firewall3_main.remove_black(data)
        firewall3_lpsb.remove_black(data)
        await state.clear()
        tracker.log(
            command=("PARDON", F.LIGHTCYAN_EX + S.BRIGHT),
            status=("UNBAN!", F.LIGHTCYAN_EX + S.NORMAL),
            from_user=f.collect_FU(message)
        )
    except Exception as e:
        tracker.error(
            e=e,
            userID=message.from_user.id
        )
