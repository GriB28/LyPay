from aiogram import Router
from aiogram.types import Message, CallbackQuery, FSInputFile
from aiogram.filters.command import Command
from aiogram.fsm.context import FSMContext
from aiogram import F as mF

from asyncio import sleep
from colorama import Fore as F, Style as S
from random import randint
from os.path import exists

from scripts import f, tracker, firewall3, exelink, lpsql
from scripts.j2 import fromfile as j_fromfile
from data import config as cfg, txt

from source.LPSB._states import *
import source.LPSB._keyboards as main_keyboard

rtr = Router()
config = [j_fromfile(cfg.PATHS.LAUNCH_SETTINGS)["config_v"]]
firewall3 = firewall3.FireWall("LPSB")
db = lpsql.DataBase("lypay_database.db", lpsql.Tables.MAIN)
print("LPSB/access router")


@rtr.message(Command("access"))
async def access(message: Message, state: FSMContext):
    try:
        f.update_config(config, [txt, cfg, main_keyboard])
        firewall_status = firewall3.check(message.from_user.id)
        if firewall_status == firewall3.WHITE_ANCHOR:
            current = await state.get_state()
            if current not in RegistrationFSM.__states__ and \
                    current not in MenuFSM.__states__ and \
                    current not in AccessFSM.__states__ and \
                    current not in AdFSM.__states__ and \
                    message.from_user.id in db.searchall("shopkeepers", "userID"):
                store = db.search("stores", "ID", db.search("shopkeepers", "userID", message.from_user.id)["storeID"])
                if store["hostID"] == message.from_user.id:
                    await state.set_state(AccessFSM.MENU)
                    m_id = (await message.answer(
                        txt.LPSB.ACCESS.MENU,
                        reply_markup=main_keyboard.accessCMD
                    )).message_id
                    exelink.sublist(
                        mode='add',
                        name='ccc/lpsb',
                        key=message.chat.id,
                        data=m_id,
                        userID=message.from_user.id
                    )
                    tracker.log(
                        command=("ACCESS", F.LIGHTCYAN_EX + S.BRIGHT),
                        status=("MENU", F.YELLOW + S.NORMAL),
                        from_user=f.collect_FU(message)
                    )
                else:
                    await message.answer(txt.LPSB.ACCESS.NOT_HOST)
                    tracker.log(
                        command=("ACCESS", F.LIGHTCYAN_EX + S.BRIGHT),
                        status=("NOT_HOST", F.RED + S.NORMAL),
                        from_user=f.collect_FU(message)
                    )
            elif current not in RegistrationFSM.__states__:
                await message.delete()
            else:
                await message.answer(txt.LPSB.REGISTRATION.FORCE_REGISTRATION)
                tracker.log(
                    command=("ACCESS", F.LIGHTCYAN_EX + S.BRIGHT),
                    status=("FORCED_REGISTRATION", F.LIGHTMAGENTA_EX + S.BRIGHT),
                    from_user=f.collect_FU(message)
                )
        elif firewall_status == firewall3.BLACK_ANCHOR:
            tracker.black(f.collect_FU(message))
            await message.answer(txt.LPSB.CMD.IN_BLACKLIST)
        else:
            tracker.gray(f.collect_FU(message))
            await message.answer(txt.LPSB.CMD.NOT_IN_WHITELIST)
            await message.answer_sticker(cfg.MEDIA.NOT_IN_LPSB_WHITELIST_FROGS[
                                             randint(0, len(cfg.MEDIA.NOT_IN_LPSB_WHITELIST_FROGS) - 1)
                                         ])
            # print(F.LIGHTBLACK_EX + S.DIM + str(message.from_user.id))
    except Exception as e:
        tracker.error(
            e=e,
            userID=message.from_user.id
        )


@rtr.callback_query(AccessFSM.MENU, mF.data == "access_add_cb")
async def access_add(callback: CallbackQuery, state: FSMContext):
    try:
        f.update_config(config, [txt, cfg, main_keyboard])
        await callback.message.edit_text("Меню доступа\n> '➕ Добавить пользователя'")
        await callback.answer()
        await callback.message.answer(txt.LPSB.ACCESS.ADD.START)
        await state.set_state(AccessFSM.ADD_PICK)
        exelink.sublist(
            mode='remove',
            name='ccc/lpsb',
            key=callback.message.chat.id,
            userID=callback.from_user.id
        )
        tracker.log(
            command=("ACCESS", F.LIGHTCYAN_EX + S.BRIGHT),
            status=("ADD", F.GREEN + S.NORMAL),
            from_user=f.collect_FU(callback)
        )
    except Exception as e:
        tracker.error(
            e=e,
            userID=callback.from_user.id
        )


@rtr.message(AccessFSM.ADD_PICK, mF.text)
async def access_add_choose(message: Message, state: FSMContext):
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
            user = int(message.text.strip())
            store = db.search("shopkeepers", "userID", message.from_user.id)["storeID"]
            users_store = db.search("shopkeepers", "userID", user)
            if users_store:
                users_store = users_store
                if users_store != store:
                    await message.answer(txt.LPSB.ACCESS.ADD.USER_ALREADY_HAS_STORE)
                    tracker.log(
                        command=("ACCESS", F.LIGHTCYAN_EX + S.BRIGHT),
                        status=("USER_HAS_STORE", F.RED + S.NORMAL),
                        from_user=f.collect_FU(message)
                    )
                else:
                    await message.answer(txt.LPSB.ACCESS.ADD.USER_ALREADY_ADDED)
                    tracker.log(
                        command=("ACCESS", F.LIGHTCYAN_EX + S.BRIGHT),
                        status=("USER_ALREADY_ADDED", F.RED + S.DIM),
                        from_user=f.collect_FU(message)
                    )
            else:
                user = db.search("users", "ID", user)
                if user is None:
                    user = {"name": "незарегистрированный пользователь", "class": "–", "tag": None}
                await message.answer(txt.LPSB.ACCESS.CONFIRM.format(
                    name=user["name"],
                    group=user["class"],
                    tag='@' + user["tag"] if user["tag"] else '–'
                ))
                await state.update_data(PICK=message.text.strip())
                await state.set_state(AccessFSM.ADD_CONFIRM)
                tracker.log(
                    command=("ACCESS", F.LIGHTCYAN_EX + S.BRIGHT),
                    status=("CONFIRM_ADDING", F.GREEN + S.NORMAL),
                    from_user=f.collect_FU(message)
                )
        except ValueError:
            await message.answer(txt.LPSB.ACCESS.BAD_FORMAT)
            tracker.log(
                command=("ACCESS", F.LIGHTCYAN_EX + S.BRIGHT),
                status=("BAD_FORMAT", F.RED + S.NORMAL),
                from_user=f.collect_FU(message)
            )
    except Exception as e:
        tracker.error(
            e=e,
            userID=message.from_user.id
        )


@rtr.message(AccessFSM.ADD_CONFIRM, Command("confirm"))
async def access_add_confirm(message: Message, state: FSMContext):
    try:
        f.update_config(config, [txt, cfg, main_keyboard])
        user = (await state.get_data())["PICK"]
        store = db.search("shopkeepers", "userID", message.from_user.id)["storeID"]
        db.insert(
            "shopkeepers",
            [user, store]
        )
        firewall3.add_white(int(user), f"added by {message.from_user.id}")

        await message.answer(txt.LPSB.ACCESS.ADD.SUCCESS)
        await state.clear()
        tracker.log(
            command=("ACCESS", F.LIGHTCYAN_EX + S.BRIGHT),
            status=("NEW_SAVED", F.GREEN + S.NORMAL),
            from_user=f.collect_FU(message)
        )
    except Exception as e:
        tracker.error(
            e=e,
            userID=message.from_user.id
        )


@rtr.callback_query(AccessFSM.MENU, mF.data == "access_remove_cb")
async def access_remove(callback: CallbackQuery, state: FSMContext):
    try:
        f.update_config(config, [txt, cfg, main_keyboard])
        await callback.message.edit_text("Меню доступа\n> '➖ Удалить пользователя'")
        await callback.answer()
        await callback.message.answer(txt.LPSB.ACCESS.REMOVE.START)
        await state.set_state(AccessFSM.REMOVE_PICK)
        exelink.sublist(
            mode='remove',
            name='ccc/lpsb',
            key=callback.message.chat.id,
            userID=callback.from_user.id
        )
        tracker.log(
            command=("ACCESS", F.LIGHTCYAN_EX + S.BRIGHT),
            status=("REMOVE", F.GREEN + S.NORMAL),
            from_user=f.collect_FU(callback)
        )
    except Exception as e:
        tracker.error(
            e=e,
            userID=main_keyboard.cancelChequeCMD.from_user.id
        )


@rtr.message(AccessFSM.REMOVE_PICK, mF.text)
async def access_remove_choose(message: Message, state: FSMContext):
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
            user = int(message.text.strip())
            store = db.search("shopkeepers", "userID", message.from_user.id)["storeID"]
            if user == message.from_user.id:
                await message.answer(txt.LPSB.ACCESS.SELF_REMOVE)
                tracker.log(
                    command=("ACCESS", F.LIGHTCYAN_EX + S.BRIGHT),
                    status=("SELF_REMOVE_TRY", F.RED + S.NORMAL),
                    from_user=f.collect_FU(message)
                )
            else:
                users_store = db.search("shopkeepers", "userID", user)
                if users_store is not None:
                    if users_store["storeID"] == store:
                        user = db.search("users", "ID", user)
                        if user is None:
                            user = {"name": "незарегистрированный пользователь", "class": "–", "tag": None}
                        await message.answer(txt.LPSB.ACCESS.CONFIRM.format(
                            name=user["name"],
                            group=user["class"],
                            tag='@' + user["tag"] if user["tag"] else '–'
                        ))
                        await state.update_data(PICK=message.text.strip())
                        await state.set_state(AccessFSM.REMOVE_CONFIRM)
                        tracker.log(
                            command=("ACCESS", F.LIGHTCYAN_EX + S.BRIGHT),
                            status=("CONFIRM_REMOVING", F.GREEN + S.NORMAL),
                            from_user=f.collect_FU(message)
                        )
                    else:
                        await message.answer(txt.LPSB.ACCESS.REMOVE.USER_HAS_NO_ACCESS)
                        tracker.log(
                            command=("ACCESS", F.LIGHTCYAN_EX + S.BRIGHT),
                            status=("USER_HAS_ANOTHER_STORE", F.RED + S.DIM),
                            from_user=f.collect_FU(message)
                        )
                else:
                    await message.answer(txt.LPSB.ACCESS.REMOVE.USER_HAS_NO_ACCESS)
                    tracker.log(
                        command=("ACCESS", F.LIGHTCYAN_EX + S.BRIGHT),
                        status=("USER_HAS_NOT_STORE", F.RED + S.NORMAL),
                        from_user=f.collect_FU(message)
                    )

        except ValueError:
            await message.answer(txt.LPSB.ACCESS.BAD_FORMAT)
            tracker.log(
                command=("ACCESS", F.LIGHTCYAN_EX + S.BRIGHT),
                status=("BAD_FORMAT", F.RED + S.NORMAL),
                from_user=f.collect_FU(message)
            )
    except Exception as e:
        tracker.error(
            e=e,
            userID=message.from_user.id
        )


@rtr.message(AccessFSM.REMOVE_CONFIRM, Command("confirm"))
async def access_remove_confirm(message: Message, state: FSMContext):
    try:
        f.update_config(config, [txt, cfg, main_keyboard])
        user = (await state.get_data())["PICK"]
        store_id = db.search("shopkeepers", "userID", message.from_user.id)["storeID"]

        db.delete("shopkeepers", user, store_id)
        try:
            db.delete("changing", user, store_id)
        except:
            pass
        firewall3.remove_white(user)

        await message.answer(txt.LPSB.ACCESS.REMOVE.SUCCESS)
        await state.clear()
        tracker.log(
            command=("ACCESS", F.LIGHTCYAN_EX + S.BRIGHT),
            status=("REMOVED", F.GREEN + S.NORMAL),
            from_user=f.collect_FU(message)
        )
    except Exception as e:
        tracker.error(
            e=e,
            userID=message.from_user.id
        )


@rtr.callback_query(AccessFSM.MENU, mF.data == "access_monitor_cb")
async def access_monitor(callback: CallbackQuery, state: FSMContext):
    try:
        f.update_config(config, [txt, cfg, main_keyboard])
        await callback.message.edit_text("Меню доступа\n> '👁️‍🗨️ Просмотр пользователей'")
        await callback.answer()
        exelink.sublist(
            mode='remove',
            name='ccc/lpsb',
            key=callback.message.chat.id,
            userID=callback.from_user.id
        )

        userIDs = list(map(
            lambda d: d["userID"],
            db.search(
                "shopkeepers",
                "storeID",
                db.search("shopkeepers", "userID", callback.from_user.id)["storeID"],
                True
            )
        ))

        generated_string = list()
        for id_ in userIDs:
            user_ = db.search("users", "ID", id_)
            if user_ is None:
                user_ = {"name": "незарегистрированный пользователь", "class": "–", "tag": None}
            generated_string.append(
                f"<code>{id_}</code> {'(владелец) ' if id_ == callback.from_user.id else ''}– {user_["name"]} ({user_["class"]}){' @' + user_["tag"] if user_["tag"] else ''}"
            )

        await callback.message.answer(txt.LPSB.ACCESS.MONITOR.format(
            users='\n'.join(generated_string)
        ))
        await state.clear()
        tracker.log(
            command=("ACCESS", F.LIGHTCYAN_EX + S.BRIGHT),
            status=("MONITOR", F.LIGHTBLUE_EX + S.NORMAL),
            from_user=f.collect_FU(callback)
        )
    except Exception as e:
        tracker.error(
            e=e,
            userID=callback.from_user.id
        )


@rtr.message(Command("get_access"))
async def access_request(message: Message, state: FSMContext):
    try:
        f.update_config(config, [txt, cfg, main_keyboard])
        if message.from_user.id not in db.searchall("shopkeepers", "userID"):
            await message.answer(txt.LPSB.ACCESS.ADD.REQUEST_START)
            await state.clear()
            tracker.log(
                command=("ACCESS", F.LIGHTCYAN_EX + S.BRIGHT),
                status=("REQUEST", F.BLUE + S.NORMAL),
                from_user=f.collect_FU(message)
            )

            qr = db.search("qr", "userID", message.from_user.id)
            if qr is None or qr["fileID_lpsb"] is None:
                path = cfg.PATHS.QR + f"{message.from_user.id}.png"
                if not exists(path):
                    exelink.add(f"qr {message.from_user.id}", message.from_user.id)
                    while not exists(path):
                        await sleep(.5)
                if qr is None:
                    db.insert("qr", [message.from_user.id, None, None, None])
                fileid = (await message.answer_photo(
                    FSInputFile(path),
                    caption=f"<code>{message.from_user.id}</code>",
                    has_spoiler=True
                )).photo[-1].file_id
                db.update("qr", "userID", message.from_user.id, "fileID_lpsb", fileid)
            else:
                await message.answer_photo(
                    qr["fileID_lpsb"],
                    caption=f"<code>{message.from_user.id}</code>",
                    has_spoiler=True
                )
        else:
            await message.delete()
            tracker.log(
                command=("ACCESS", F.LIGHTCYAN_EX + S.BRIGHT),
                status=("ALREADY_HAS", F.BLUE + S.NORMAL),
                from_user=f.collect_FU(message)
            )
    except Exception as e:
        tracker.error(
            e=e,
            userID=message.from_user.id
        )


# @rtr.message(Command("get_access"))
async def temp_access(message: Message):
    try:
        f.update_config(config, [txt, cfg, main_keyboard])
        await message.answer("Открытие доступа пока что отключено 🥺")
        tracker.log(
            command=("ACCESS", F.LIGHTCYAN_EX + S.BRIGHT),
            status=("REQUEST", F.BLUE + S.NORMAL),
            from_user=f.collect_FU(message)
        )
    except Exception as e:
        tracker.error(
            e=e,
            userID=message.from_user.id
        )
