from aiogram import Router
from aiogram import F as mF
from aiogram.filters.command import Command
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from asyncio import sleep
from colorama import Fore as F, Style as S
from os import listdir
from psutil import cpu_percent as CPU, virtual_memory as RAM, process_iter
from datetime import datetime

from scripts import j2, f, firewall3, tracker, exelink, lpsql
from data import config as cfg, txt

from source.LPAA._states import *
import source.LPAA._keyboards as main_keyboard


rtr = Router()
config = [j2.fromfile(cfg.PATHS.LAUNCH_SETTINGS)["config_v"]]
firewall3 = firewall3.FireWall("LPAA")
print("LPAA/info router")


@rtr.message(Command("info"), mF.chat.id == cfg.HIGH_GROUP)
async def information(message: Message, state: FSMContext):
    try:
        f.update_config(config, [txt, cfg, main_keyboard])
        firewall_status = firewall3.check(message.from_user.id)
        if firewall_status == firewall3.WHITE_ANCHOR:
            msg = list()
            m3 = await message.answer(txt.LPAA.INFO.START_CHEQUE, reply_markup=main_keyboard.infoCMD_cheque)
            m2 = await message.answer(txt.LPAA.INFO.START_STORE, reply_markup=main_keyboard.infoCMD_store)
            m1 = await message.answer(txt.LPAA.INFO.START_USER, reply_markup=main_keyboard.infoCMD_user)
            msg.append(m1)
            msg.append(m2)
            msg.append(m3)
            await state.update_data(MSG=msg)
            await state.set_state(InfoFSM.INFO)
            tracker.log(
                command=("INFO", F.YELLOW + S.NORMAL),
                status=("MENU", F.YELLOW + S.NORMAL),
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


# USER ID
@rtr.callback_query(InfoFSM.INFO, mF.data == 'user_ID_', mF.message.chat.id == cfg.HIGH_GROUP)
async def info_user_id(callback: CallbackQuery, state: FSMContext):
    try:
        f.update_config(config, [txt, cfg, main_keyboard])
        await callback.message.edit_text("Выбран поиск пользователя по ID")
        await callback.answer()
        msg = (await state.get_data())["MSG"]
        await msg[1].delete()
        await msg[2].delete()
        await state.set_state(InfoFSM.USER_ID)
        await callback.message.answer(txt.LPAA.INFO.USER.ID)
        tracker.log(
            command=("INFO", F.YELLOW + S.NORMAL),
            status=("USER_ID", F.GREEN + S.DIM),
            from_user=f.collect_FU(callback)
        )
    except Exception as e:
        tracker.error(
            e=e,
            userID=callback.from_user.id
        )


@rtr.message(InfoFSM.USER_ID, mF.text, mF.chat.id == cfg.HIGH_GROUP)
async def user_by_id(message: Message, state: FSMContext):
    try:
        f.update_config(config, [txt, cfg, main_keyboard])
        try:
            input_ = int(message.text.strip())
            await message.answer("Запрос одобрен. Ожидайте ответа...")
            try:
                user = lpsql.search("users", "ID", input_)
                if user is None:
                    raise lpsql.errors.IDNotFound
                await message.answer(txt.LPAA.INFO.USER.TABLET.format(
                    id=input_,
                    name=user["name"],
                    group=user["class"],
                    email=user["email"],
                    tag='@'+user["tag"] if user["tag"] else '–',
                    balance=user["balance"]
                ))
            except lpsql.errors.IDNotFound:
                await message.answer("Ничего не найдено!")
                tracker.log(
                    command=("INFO", F.YELLOW + S.NORMAL),
                    status=("NULL_SEARCH", F.RED + S.DIM),
                    from_user=f.collect_FU(message)
                )
            await state.clear()
        except ValueError:
            await message.answer(txt.LPAA.BAD_ARG)
            tracker.log(
                command=("INFO", F.YELLOW + S.NORMAL),
                status=("BAD_ARG", F.RED + S.DIM),
                from_user=f.collect_FU(message)
            )
    except Exception as e:
        tracker.error(
            e=e,
            userID=message.from_user.id
        )


# USER NAME
@rtr.callback_query(InfoFSM.INFO, mF.data == 'user_NAME_', mF.message.chat.id == cfg.HIGH_GROUP)
async def info_user_name(callback: CallbackQuery, state: FSMContext):
    try:
        f.update_config(config, [txt, cfg, main_keyboard])
        await callback.message.edit_text("Выбран поиск пользователя по имени")
        await callback.answer()
        msg = (await state.get_data())["MSG"]
        await msg[1].delete()
        await msg[2].delete()
        await state.set_state(InfoFSM.USER_NAME)
        await callback.message.answer(txt.LPAA.INFO.USER.NAME)
        tracker.log(
            command=("INFO", F.YELLOW + S.NORMAL),
            status=("USER_NAME", F.GREEN + S.DIM),
            from_user=f.collect_FU(callback)
        )
    except Exception as e:
        tracker.error(
            e=e,
            userID=callback.from_user.id
        )


@rtr.message(InfoFSM.USER_NAME, mF.text, mF.chat.id == cfg.HIGH_GROUP)
async def user_by_name(message: Message, state: FSMContext):
    try:
        f.update_config(config, [txt, cfg, main_keyboard])
        try:
            input_ = message.text.strip().lower()
            await message.answer("Запрос одобрен. Ожидайте ответа...")
            tracker.log(
                command=("INFO", F.YELLOW + S.NORMAL),
                status=("SEARCHING", F.GREEN + S.DIM),
                from_user=f.collect_FU(message)
            )
            out = 0
            for user in lpsql.searchall("users", "ID"):
                read = lpsql.search("users", "ID", user)
                if input_ in read["name"].lower():
                    await message.answer(txt.LPAA.INFO.USER.TABLET.format(
                        id=user,
                        name=read["name"],
                        group=read["class"],
                        email=read["email"],
                        tag='@'+read["tag"] if read["tag"] else '–',
                        balance=read["balance"]
                    ))
                    await sleep(1/30)
                    out += 1
            if out == 0:
                await message.answer("Ничего не найдено!")
                tracker.log(
                    command=("INFO", F.YELLOW + S.NORMAL),
                    status=("NULL_SEARCH", F.RED + S.DIM),
                    from_user=f.collect_FU(message)
                )
            await state.clear()
        except ValueError:
            await message.answer(txt.LPAA.BAD_ARG)
            tracker.log(
                command=("INFO", F.YELLOW + S.NORMAL),
                status=("BAD_ARG", F.RED + S.DIM),
                from_user=f.collect_FU(message)
            )
    except Exception as e:
        tracker.error(
            e=e,
            userID=message.from_user.id
        )


# USER EMAIL
@rtr.callback_query(InfoFSM.INFO, mF.data == 'user_EMAIL_', mF.message.chat.id == cfg.HIGH_GROUP)
async def info_user_email(callback: CallbackQuery, state: FSMContext):
    try:
        f.update_config(config, [txt, cfg, main_keyboard])
        await callback.message.edit_text("Выбран поиск пользователя по почте")
        await callback.answer()
        msg = (await state.get_data())["MSG"]
        await msg[1].delete()
        await msg[2].delete()
        await state.set_state(InfoFSM.USER_EMAIL)
        await callback.message.answer(txt.LPAA.INFO.USER.EMAIL)
        tracker.log(
            command=("INFO", F.YELLOW + S.NORMAL),
            status=("USER_EMAIL", F.GREEN + S.DIM),
            from_user=f.collect_FU(callback)
        )
    except Exception as e:
        tracker.error(
            e=e,
            userID=callback.from_user.id
        )


@rtr.message(InfoFSM.USER_EMAIL, mF.text, mF.chat.id == cfg.HIGH_GROUP)
async def user_by_email(message: Message, state: FSMContext):
    try:
        f.update_config(config, [txt, cfg, main_keyboard])
        try:
            input_ = message.text.strip().lower()
            await message.answer("Запрос одобрен. Ожидайте ответа...")
            tracker.log(
                command=("INFO", F.YELLOW + S.NORMAL),
                status=("SEARCHING", F.GREEN + S.DIM),
                from_user=f.collect_FU(message)
            )
            out = 0
            for user in lpsql.searchall("users", "ID"):
                read = lpsql.search("users", "ID", user)
                if input_ in read["email"].lower():
                    await message.answer(txt.LPAA.INFO.USER.TABLET.format(
                        id=user,
                        name=read["name"],
                        group=read["class"],
                        email=read["email"],
                        tag='@'+read["tag"] if read["tag"] else '–',
                        balance=read["balance"]
                    ))
                    await sleep(1/30)
                    out += 1
            if out == 0:
                await message.answer("Ничего не найдено!")
                tracker.log(
                    command=("INFO", F.YELLOW + S.NORMAL),
                    status=("NULL_SEARCH", F.RED + S.DIM),
                    from_user=f.collect_FU(message)
                )
            await state.clear()
        except ValueError:
            await message.answer(txt.LPAA.BAD_ARG)
            tracker.log(
                command=("INFO", F.YELLOW + S.NORMAL),
                status=("BAD_ARG", F.RED + S.DIM),
                from_user=f.collect_FU(message)
            )
    except Exception as e:
        tracker.error(
            e=e,
            userID=message.from_user.id
        )


# USER TAG
@rtr.callback_query(InfoFSM.INFO, mF.data == 'user_TAG_', mF.message.chat.id == cfg.HIGH_GROUP)
async def info_user_tag(callback: CallbackQuery, state: FSMContext):
    try:
        f.update_config(config, [txt, cfg, main_keyboard])
        await callback.message.edit_text("Выбран поиск пользователя по тегу")
        await callback.answer()
        msg = (await state.get_data())["MSG"]
        await msg[1].delete()
        await msg[2].delete()
        await state.set_state(InfoFSM.USER_TAG)
        await callback.message.answer(txt.LPAA.INFO.USER.TAG)
        tracker.log(
            command=("INFO", F.YELLOW + S.NORMAL),
            status=("USER_TAG", F.GREEN + S.DIM),
            from_user=f.collect_FU(callback)
        )
    except Exception as e:
        tracker.error(
            e=e,
            userID=callback.from_user.id
        )


@rtr.message(InfoFSM.USER_TAG, mF.text, mF.chat.id == cfg.HIGH_GROUP)
async def user_by_tag(message: Message, state: FSMContext):
    try:
        f.update_config(config, [txt, cfg, main_keyboard])
        try:
            input_ = message.text.strip().lower().replace('@', '')
            await message.answer("Запрос одобрен. Ожидайте ответа...")
            tracker.log(
                command=("INFO", F.YELLOW + S.NORMAL),
                status=("SEARCHING", F.GREEN + S.DIM),
                from_user=f.collect_FU(message)
            )
            out = 0
            for user in lpsql.searchall("users", "ID"):
                read = lpsql.search("users", "ID", user)
                if read["tag"] and input_ in read["tag"].lower():
                    await message.answer(txt.LPAA.INFO.USER.TABLET.format(
                        id=user,
                        name=read["name"],
                        group=read["class"],
                        email=read["email"],
                        tag='@'+read["tag"] if read["tag"] else '–',
                        balance=read["balance"]
                    ))
                    await sleep(1/30)
                    out += 1
            if out == 0:
                await message.answer("Ничего не найдено!")
                tracker.log(
                    command=("INFO", F.YELLOW + S.NORMAL),
                    status=("NULL_SEARCH", F.RED + S.DIM),
                    from_user=f.collect_FU(message)
                )
            await state.clear()
        except ValueError:
            await message.answer(txt.LPAA.BAD_ARG)
            tracker.log(
                command=("INFO", F.YELLOW + S.NORMAL),
                status=("BAD_ARG", F.RED + S.DIM),
                from_user=f.collect_FU(message)
            )
    except Exception as e:
        tracker.error(
            e=e,
            userID=message.from_user.id
        )


# USER/STORE TRANSACTIONS
@rtr.callback_query(InfoFSM.INFO, mF.data.in_(('user_TRANSACTION_', 'store_TRANSACTION_')), mF.message.chat.id == cfg.HIGH_GROUP)
async def info_transaction(callback: CallbackQuery, state: FSMContext):
    try:
        f.update_config(config, [txt, cfg, main_keyboard])
        await callback.message.edit_text("Выбран просмотр переводов")
        await callback.answer()
        await state.set_state(InfoFSM.TRANSACTION)
        msg = (await state.get_data())["MSG"]
        await msg[2].delete()
        if callback.data == "user_TRANSACTION_":
            await msg[1].delete()
            await state.update_data(TRANSACTION='u')
            await callback.message.answer(txt.LPAA.INFO.USER.TRANSACTION.USER_START)
        else:
            await msg[0].delete()
            await state.update_data(TRANSACTION='s')
            await callback.message.answer(txt.LPAA.INFO.USER.TRANSACTION.STORE_START)
        tracker.log(
            command=("INFO", F.YELLOW + S.NORMAL),
            status=("USER_TRANSACTIONS", F.GREEN + S.DIM),
            from_user=f.collect_FU(callback)
        )
    except Exception as e:
        tracker.error(
            e=e,
            userID=callback.from_user.id
        )


def format_transaction_report(text: str, id_: str, amount: int, time: str) -> str:
    return text.format(id=id_, amount=amount, time=time)


@rtr.message(InfoFSM.TRANSACTION, mF.text, mF.chat.id == cfg.HIGH_GROUP)
async def transactions(message: Message, state: FSMContext):
    try:
        f.update_config(config, [txt, cfg, main_keyboard])
        data = (await state.get_data())["TRANSACTION"]
        is_user = data == 'u'
        input_ = message.text.strip()
        ok = False
        try:
            if not ok and int(input_) in lpsql.searchall("users", "ID"):
                ok = True
        except ValueError:
            pass
        if not ok and input_ in lpsql.searchall("stores", "ID"):
            ok = True

        if not ok:
            await message.answer(txt.LPAA.BAD_ARG)
            tracker.log(
                command=("INFO", F.YELLOW + S.NORMAL),
                status=("BAD_ARG", F.RED + S.DIM),
                from_user=f.collect_FU(message)
            )

        else:
            input_ = data + input_
            await message.answer("Запрос одобрен. Ожидайте ответа...")
            try:
                tracker.log(
                    command=("INFO", F.YELLOW + S.NORMAL),
                    status=("SEARCHING", F.GREEN + S.DIM),
                    from_user=f.collect_FU(message)
                )
                c = 0
                for tr in lpsql.get_table("history"):
                    if input_ != tr["id_out"] and input_ != tr["id_in"]:
                        continue
                    t = datetime.fromtimestamp(tr["unix"]).strftime('%d.%m.%Y %X.') + str(int(tr["unix"] * 100) % 100)
                    key = tr["id_out"] if tr["id_out"] != input_ else tr["id_in"]
                    for value in lpsql.searchall("stores", "ID"):
                        if key == f"s{value}":
                            if is_user:
                                if tr["id_out"] == input_:
                                    await message.answer(format_transaction_report(
                                        txt.LPAA.INFO.USER.TRANSACTION.USER_to_STORE_TABLET,
                                        value, tr["value"], t
                                    ))
                                    await sleep(1/30)
                                elif tr["id_in"] == input_:
                                    await message.answer(format_transaction_report(
                                        txt.LPAA.INFO.USER.TRANSACTION.USER_from_STORE_TABLET,
                                        value, tr["value"], t
                                    ))
                                    await sleep(1/30)
                            else:
                                await message.answer(format_transaction_report(
                                    "не может такого быть. магазин перевёл магазину whaaat\n{id} {amount} {time}",
                                    value, tr["value"], t
                                ))
                                await sleep(1/30)
                            c += 1
                            break
                    for value in lpsql.searchall("users", "ID"):
                        if key == f"u{value}":
                            if is_user:
                                if tr["id_out"] == input_:
                                    await message.answer(format_transaction_report(
                                        txt.LPAA.INFO.USER.TRANSACTION.USER_to_USER_TABLET,
                                        value, tr["value"], t
                                    ))
                                    await sleep(1/30)
                                elif tr["id_in"] == input_:
                                    await message.answer(format_transaction_report(
                                        txt.LPAA.INFO.USER.TRANSACTION.USER_from_USER_TABLET,
                                        value, tr["value"], t
                                    ))
                                    await sleep(1/30)
                            else:
                                if tr["id_out"] == input_:
                                    await message.answer(format_transaction_report(
                                        txt.LPAA.INFO.USER.TRANSACTION.STORE_to_USER_TABLET,
                                        value, tr["value"], t
                                    ))
                                    await sleep(1/30)
                                elif tr["id_in"] == input_:
                                    await message.answer(format_transaction_report(
                                        txt.LPAA.INFO.USER.TRANSACTION.STORE_from_USER_TABLET,
                                        value, tr["value"], t
                                    ))
                                    await sleep(1/30)
                            c += 1
                            break
                    if key[0] == "d":
                        await message.answer(format_transaction_report(
                            txt.LPAA.INFO.USER.TRANSACTION.DEALER_to_ANYONE_TABLET,
                            key[1:], tr["value"], t
                        ))
                        await sleep(1/30)
                if c == 0:
                    await message.answer("Ничего не найдено!")
                    tracker.log(
                        command=("INFO", F.YELLOW + S.NORMAL),
                        status=("NULL_SEARCH", F.RED + S.DIM),
                        from_user=f.collect_FU(message)
                    )
            except lpsql.errors.IDNotFound:
                await message.answer("Ничего не найдено!")
                tracker.log(
                    command=("INFO", F.YELLOW + S.NORMAL),
                    status=("NULL_SEARCH", F.RED + S.DIM),
                    from_user=f.collect_FU(message)
                )
            await state.clear()
    except Exception as e:
        tracker.error(
            e=e,
            userID=message.from_user.id
        )


# STORE ID
@rtr.callback_query(InfoFSM.INFO, mF.data == 'store_ID_', mF.message.chat.id == cfg.HIGH_GROUP)
async def info_store_id(callback: CallbackQuery, state: FSMContext):
    try:
        f.update_config(config, [txt, cfg, main_keyboard])
        await callback.message.edit_text("Выбран поиск магазина по ID")
        await callback.answer()
        msg = (await state.get_data())["MSG"]
        await msg[0].delete()
        await msg[2].delete()
        await state.set_state(InfoFSM.STORE_ID)
        await callback.message.answer(txt.LPAA.INFO.STORE.ID)
        tracker.log(
            command=("INFO", F.YELLOW + S.NORMAL),
            status=("STORE_ID", F.GREEN + S.DIM),
            from_user=f.collect_FU(callback)
        )
    except Exception as e:
        tracker.error(
            e=e,
            userID=callback.from_user.id
        )


@rtr.message(InfoFSM.STORE_ID, mF.text, mF.chat.id == cfg.HIGH_GROUP)
async def store_by_id(message: Message, state: FSMContext):
    try:
        f.update_config(config, [txt, cfg, main_keyboard])
        try:
            input_ = message.text.strip().lower()
            await message.answer("Запрос одобрен. Ожидайте ответа...")
            try:
                tracker.log(
                    command=("INFO", F.YELLOW + S.NORMAL),
                    status=("SEARCHING", F.GREEN + S.DIM),
                    from_user=f.collect_FU(message)
                )
                read = lpsql.search("stores", "ID", input_)
                if read is None:
                    raise lpsql.errors.IDNotFound
                await message.answer(txt.LPAA.INFO.STORE.TABLET.format(
                    store=input_,
                    name=read["name"],
                    desc=read["description"],
                    auc=read["auctionID"],
                    host=read["hostID"],
                    balance=read["balance"]
                ))
            except lpsql.errors.IDNotFound:
                await message.answer("Ничего не найдено!")
                tracker.log(
                    command=("INFO", F.YELLOW + S.NORMAL),
                    status=("NULL_SEARCH", F.RED + S.DIM),
                    from_user=f.collect_FU(message)
                )
            await state.clear()
        except ValueError:
            await message.answer(txt.LPAA.BAD_ARG)
            tracker.log(
                command=("INFO", F.YELLOW + S.NORMAL),
                status=("BAD_ARG", F.RED + S.DIM),
                from_user=f.collect_FU(message)
            )
    except Exception as e:
        tracker.error(
            e=e,
            userID=message.from_user.id
        )


# STORE NAME
@rtr.callback_query(InfoFSM.INFO, mF.data == 'store_NAME_', mF.message.chat.id == cfg.HIGH_GROUP)
async def info_store_name(callback: CallbackQuery, state: FSMContext):
    try:
        f.update_config(config, [txt, cfg, main_keyboard])
        await callback.message.edit_text("Выбран поиск магазина по названию")
        await callback.answer()
        msg = (await state.get_data())["MSG"]
        await msg[0].delete()
        await msg[2].delete()
        await state.set_state(InfoFSM.STORE_NAME)
        await callback.message.answer(txt.LPAA.INFO.STORE.NAME)
        tracker.log(
            command=("INFO", F.YELLOW + S.NORMAL),
            status=("STORE_ID", F.GREEN + S.DIM),
            from_user=f.collect_FU(callback)
        )
    except Exception as e:
        tracker.error(
            e=e,
            userID=callback.from_user.id
        )


@rtr.message(InfoFSM.STORE_NAME, mF.text, mF.chat.id == cfg.HIGH_GROUP)
async def store_by_name(message: Message, state: FSMContext):
    try:
        f.update_config(config, [txt, cfg, main_keyboard])
        try:
            input_ = message.text.strip().lower()
            await message.answer("Запрос одобрен. Ожидайте ответа...")
            out = 0
            tracker.log(
                command=("INFO", F.YELLOW + S.NORMAL),
                status=("SEARCHING", F.GREEN + S.DIM),
                from_user=f.collect_FU(message)
            )
            for store in lpsql.searchall("stores", "ID"):
                js = lpsql.search("stores", "ID", store)
                if input_ in js["name"].lower():
                    await message.answer(txt.LPAA.INFO.STORE.TABLET.format(
                        store=store,
                        name=js["name"],
                        desc=js["description"],
                        auc=js["auctionID"],
                        host=js["hostID"],
                        balance=js["balance"]
                    ))
                    await sleep(1/30)
                    out += 1
            if out == 0:
                await message.answer("Ничего не найдено!")
                tracker.log(
                    command=("INFO", F.YELLOW + S.NORMAL),
                    status=("NULL_SEARCH", F.RED + S.DIM),
                    from_user=f.collect_FU(message)
                )
            await state.clear()
        except ValueError:
            await message.answer(txt.LPAA.BAD_ARG)
            tracker.log(
                command=("INFO", F.YELLOW + S.NORMAL),
                status=("BAD_ARG", F.RED + S.DIM),
                from_user=f.collect_FU(message)
            )
    except Exception as e:
        tracker.error(
            e=e,
            userID=message.from_user.id
        )


# STORE DESCRIPTION
@rtr.callback_query(InfoFSM.INFO, mF.data == 'store_DESC_', mF.message.chat.id == cfg.HIGH_GROUP)
async def info_store_desc(callback: CallbackQuery, state: FSMContext):
    try:
        f.update_config(config, [txt, cfg, main_keyboard])
        await callback.message.edit_text("Выбран поиск магазина по описанию")
        await callback.answer()
        msg = (await state.get_data())["MSG"]
        await msg[0].delete()
        await msg[2].delete()
        await state.set_state(InfoFSM.STORE_DESC)
        await callback.message.answer(txt.LPAA.INFO.STORE.DESC)
        tracker.log(
            command=("INFO", F.YELLOW + S.NORMAL),
            status=("STORE_DESC", F.GREEN + S.DIM),
            from_user=f.collect_FU(callback)
        )
    except Exception as e:
        tracker.error(
            e=e,
            userID=callback.from_user.id
        )


@rtr.message(InfoFSM.STORE_DESC, mF.text, mF.chat.id == cfg.HIGH_GROUP)
async def store_by_desc(message: Message, state: FSMContext):
    try:
        f.update_config(config, [txt, cfg, main_keyboard])
        try:
            input_ = message.text.strip().lower()
            await message.answer("Запрос одобрен. Ожидайте ответа...")
            out = 0
            tracker.log(
                command=("INFO", F.YELLOW + S.NORMAL),
                status=("SEARCHING", F.GREEN + S.DIM),
                from_user=f.collect_FU(message)
            )
            for store in lpsql.searchall("stores", "ID"):
                js = lpsql.search("stores", "ID", store)
                if input_ in js["description"].lower():
                    await message.answer(txt.LPAA.INFO.STORE.TABLET.format(
                        store=store,
                        name=js["name"],
                        desc=js["description"],
                        auc=js["auctionID"],
                        host=js["hostID"],
                        balance=js["balance"]
                    ))
                    await sleep(1/30)
                    out += 1
            if out == 0:
                await message.answer("Ничего не найдено!")
                tracker.log(
                    command=("INFO", F.YELLOW + S.NORMAL),
                    status=("NULL_SEARCH", F.RED + S.DIM),
                    from_user=f.collect_FU(message)
                )
            await state.clear()
        except ValueError:
            await message.answer(txt.LPAA.BAD_ARG)
            tracker.log(
                command=("INFO", F.YELLOW + S.NORMAL),
                status=("BAD_ARG", F.RED + S.DIM),
                from_user=f.collect_FU(message)
            )
    except Exception as e:
        tracker.error(
            e=e,
            userID=message.from_user.id
        )


# STORE HOST
@rtr.callback_query(InfoFSM.INFO, mF.data == 'store_HOST_', mF.message.chat.id == cfg.HIGH_GROUP)
async def info_store_host(callback: CallbackQuery, state: FSMContext):
    try:
        f.update_config(config, [txt, cfg, main_keyboard])
        await callback.message.edit_text("Выбран поиск магазина по владельцу")
        await callback.answer()
        msg = (await state.get_data())["MSG"]
        await msg[0].delete()
        await msg[2].delete()
        await state.set_state(InfoFSM.STORE_HOST)
        await callback.message.answer(txt.LPAA.INFO.STORE.HOST)
        tracker.log(
            command=("INFO", F.YELLOW + S.NORMAL),
            status=("STORE_HOST", F.GREEN + S.DIM),
            from_user=f.collect_FU(callback)
        )
    except Exception as e:
        tracker.error(
            e=e,
            userID=callback.from_user.id
        )


@rtr.message(InfoFSM.STORE_HOST, mF.text, mF.chat.id == cfg.HIGH_GROUP)
async def store_by_host(message: Message, state: FSMContext):
    try:
        f.update_config(config, [txt, cfg, main_keyboard])
        try:
            input_ = int(message.text.strip().lower())
            await message.answer("Запрос одобрен. Ожидайте ответа...")
            out = 0
            tracker.log(
                command=("INFO", F.YELLOW + S.NORMAL),
                status=("SEARCHING", F.GREEN + S.DIM),
                from_user=f.collect_FU(message)
            )
            for store in lpsql.searchall("stores", "ID"):
                js = lpsql.search("stores", "ID", store)
                if input_ == js["hostID"]:
                    await message.answer(txt.LPAA.INFO.STORE.TABLET.format(
                        store=store,
                        name=js["name"],
                        desc=js["description"],
                        auc=js["auctionID"],
                        host=js["hostID"],
                        balance=js["balance"]
                    ))
                    await sleep(1/30)
                    out += 1
            if out == 0:
                await message.answer("Ничего не найдено!")
                tracker.log(
                    command=("INFO", F.YELLOW + S.NORMAL),
                    status=("NULL_SEARCH", F.RED + S.DIM),
                    from_user=f.collect_FU(message)
                )
            await state.clear()
        except ValueError:
            await message.answer(txt.LPAA.BAD_ARG)
            tracker.log(
                command=("INFO", F.YELLOW + S.NORMAL),
                status=("BAD_ARG", F.RED + S.DIM),
                from_user=f.collect_FU(message)
            )
    except Exception as e:
        tracker.error(
            e=e,
            userID=message.from_user.id
        )


# CHEQUE ID
@rtr.callback_query(InfoFSM.INFO, mF.data == 'cheque_ID_', mF.message.chat.id == cfg.HIGH_GROUP)
async def info_cheque_id(callback: CallbackQuery, state: FSMContext):
    try:
        f.update_config(config, [txt, cfg, main_keyboard])
        await callback.message.edit_text("Выбран поиск чека по ID")
        await callback.answer()
        msg = (await state.get_data())["MSG"]
        await msg[0].delete()
        await msg[1].delete()
        await state.set_state(InfoFSM.CHEQUE_ID)
        await callback.message.answer(txt.LPAA.INFO.CHEQUE.ID)
        tracker.log(
            command=("INFO", F.YELLOW + S.NORMAL),
            status=("CHEQUE_ID", F.YELLOW + S.NORMAL),
            from_user=f.collect_FU(callback)
        )
    except Exception as e:
        tracker.error(
            e=e,
            userID=callback.from_user.id
        )


@rtr.message(InfoFSM.CHEQUE_ID, mF.text, mF.chat.id == cfg.HIGH_GROUP)
async def cheque_by_id(message: Message, state: FSMContext):
    try:
        f.update_config(config, [txt, cfg, main_keyboard])
        try:
            input_ = message.text.strip().lower().replace('#', '').replace('cheque', '')
            if input_[0] == '_':
                input_ = input_[1:]
            await message.answer("Запрос одобрен. Ожидайте ответа...")
            tracker.log(
                command=("INFO", F.YELLOW + S.NORMAL),
                status=("SEARCHING", F.GREEN + S.DIM),
                from_user=f.collect_FU(message)
            )
            for cheque in listdir(cfg.PATHS.STORES_CHEQUES):
                if input_ == cheque[:-5]:
                    js = await j2.fromfile_async(cfg.PATHS.STORES_CHEQUES + cheque)
                    user = lpsql.search("users", "ID", js["customer"])
                    items_ = js["items"]
                    multipliers_ = js["multipliers"]
                    await message.answer(txt.LPAA.INFO.CHEQUE.TABLET.format(
                        store=input_.split('_')[1],
                        cheque_id=input_,
                        name=user["name"],
                        group=user["class"],
                        tag='@'+user["tag"] if user["tag"] else '–',
                        items=txt.MAIN.STORE.CHEQUE_GENERATED_STRINGS_SEPARATOR.join(
                            [f"{f.de_anchor(items_[i]["text"])} × {multipliers_[i]} | {items_[i]["price"] * multipliers_[i]} {cfg.VALUTA.SHORT}" for i in range(len(items_))]
                        ),
                        total=js["price"],
                        status="активен" if js["status"] else "возвращён"
                    ))
                    await state.clear()
                    return
            await message.answer("Ничего не найдено!")
            tracker.log(
                command=("INFO", F.YELLOW + S.NORMAL),
                status=("NULL_SEARCH", F.RED + S.DIM),
                from_user=f.collect_FU(message)
            )
            await state.clear()
        except ValueError:
            await message.answer(txt.LPAA.BAD_ARG)
            tracker.log(
                command=("INFO", F.YELLOW + S.NORMAL),
                status=("BAD_ARG", F.RED + S.DIM),
                from_user=f.collect_FU(message)
            )
    except Exception as e:
        tracker.error(
            e=e,
            userID=message.from_user.id
        )


# CHEQUE STORE
@rtr.callback_query(InfoFSM.INFO, mF.data == 'cheque_STORE_', mF.message.chat.id == cfg.HIGH_GROUP)
async def info_cheque_store(callback: CallbackQuery, state: FSMContext):
    try:
        f.update_config(config, [txt, cfg, main_keyboard])
        await callback.message.edit_text("Выбран поиск чека по магазину")
        await callback.answer()
        msg = (await state.get_data())["MSG"]
        await msg[0].delete()
        await msg[1].delete()
        await state.set_state(InfoFSM.CHEQUE_STORE)
        await callback.message.answer(txt.LPAA.INFO.CHEQUE.STORE)
        tracker.log(
            command=("INFO", F.YELLOW + S.NORMAL),
            status=("CHEQUE_STORE", F.YELLOW + S.NORMAL),
            from_user=f.collect_FU(callback)
        )
    except Exception as e:
        tracker.error(
            e=e,
            userID=callback.from_user.id
        )


@rtr.message(InfoFSM.CHEQUE_STORE, mF.text, mF.chat.id == cfg.HIGH_GROUP)
async def cheque_by_store(message: Message, state: FSMContext):
    try:
        f.update_config(config, [txt, cfg, main_keyboard])
        try:
            input_ = message.text.strip().lower()
            await message.answer("Запрос одобрен. Ожидайте ответа...")
            out = 0
            tracker.log(
                command=("INFO", F.YELLOW + S.NORMAL),
                status=("SEARCHING", F.GREEN + S.DIM),
                from_user=f.collect_FU(message)
            )
            for cheque in listdir(cfg.PATHS.STORES_CHEQUES):
                if input_ == cheque.split('_')[1]:
                    js = await j2.fromfile_async(cfg.PATHS.STORES_CHEQUES + cheque)
                    user = lpsql.search("users", "ID", js["customer"])
                    items_ = js["items"]
                    multipliers_ = js["multipliers"]
                    await message.answer(txt.LPAA.INFO.CHEQUE.TABLET.format(
                        store=input_,
                        cheque_id=cheque[:-5],
                        name=user["name"],
                        group=user["class"],
                        tag='@'+user["tag"] if user["tag"] else '–',
                        items=txt.MAIN.STORE.CHEQUE_GENERATED_STRINGS_SEPARATOR.join(
                            [f"{f.de_anchor(items_[i]["text"])} × {multipliers_[i]} | {items_[i]["price"] * multipliers_[i]} {cfg.VALUTA.SHORT}" for i in range(len(items_))]
                        ),
                        total=js["price"],
                        status="активен" if js["status"] else "возвращён"
                    ))
                    await sleep(1/30)
                    out += 1
            if out == 0:
                await message.answer("Ничего не найдено!")
                tracker.log(
                    command=("INFO", F.YELLOW + S.NORMAL),
                    status=("NULL_SEARCH", F.RED + S.DIM),
                    from_user=f.collect_FU(message)
                )
            await state.clear()
        except ValueError:
            await message.answer(txt.LPAA.BAD_ARG)
            tracker.log(
                command=("INFO", F.YELLOW + S.NORMAL),
                status=("BAD_ARG", F.RED + S.DIM),
                from_user=f.collect_FU(message)
            )
    except Exception as e:
        tracker.error(
            e=e,
            userID=message.from_user.id
        )


# CHEQUE CUSTOMER
@rtr.callback_query(InfoFSM.INFO, mF.data == 'cheque_CUSTOMER_', mF.message.chat.id == cfg.HIGH_GROUP)
async def info_cheque_customer(callback: CallbackQuery, state: FSMContext):
    try:
        f.update_config(config, [txt, cfg, main_keyboard])
        await callback.message.edit_text("Выбран поиск чека по покупателю")
        await callback.answer()
        msg = (await state.get_data())["MSG"]
        await msg[0].delete()
        await msg[1].delete()
        await state.set_state(InfoFSM.CHEQUE_CUST)
        await callback.message.answer(txt.LPAA.INFO.CHEQUE.CUSTOMER)
        tracker.log(
            command=("INFO", F.YELLOW + S.NORMAL),
            status=("CHEQUE_CUSTOMER", F.YELLOW + S.NORMAL),
            from_user=f.collect_FU(callback)
        )
    except Exception as e:
        tracker.error(
            e=e,
            userID=callback.from_user.id
        )


@rtr.message(InfoFSM.CHEQUE_CUST, mF.text, mF.chat.id == cfg.HIGH_GROUP)
async def cheque_by_customer(message: Message, state: FSMContext):
    try:
        f.update_config(config, [txt, cfg, main_keyboard])
        try:
            input_ = message.text.strip()
            await message.answer("Запрос одобрен. Ожидайте ответа...")
            out = 0
            tracker.log(
                command=("INFO", F.YELLOW + S.NORMAL),
                status=("SEARCHING", F.GREEN + S.DIM),
                from_user=f.collect_FU(message)
            )
            for cheque in listdir(cfg.PATHS.STORES_CHEQUES):
                if input_ == cheque.split('_')[0]:
                    js = await j2.fromfile_async(cfg.PATHS.STORES_CHEQUES + cheque)
                    user = lpsql.search("users", "ID", js["customer"])
                    items_ = js["items"]
                    multipliers_ = js["multipliers"]
                    await message.answer(txt.LPAA.INFO.CHEQUE.TABLET.format(
                        store=cheque.split('_')[1],
                        cheque_id=cheque[:-5],
                        name=user["name"],
                        group=user["class"],
                        tag='@'+user["tag"] if user["tag"] else '–',
                        items=txt.MAIN.STORE.CHEQUE_GENERATED_STRINGS_SEPARATOR.join(
                            [f"{f.de_anchor(items_[i]["text"])} × {multipliers_[i]} | {items_[i]["price"] * multipliers_[i]} {cfg.VALUTA.SHORT}" for i in range(len(items_))]
                        ),
                        total=js["price"],
                        status="активен" if js["status"] else "возвращён"
                    ))
                    await sleep(1/30)
                    out += 1
            if out == 0:
                await message.answer("Ничего не найдено!")
                tracker.log(
                    command=("INFO", F.YELLOW + S.NORMAL),
                    status=("NULL_SEARCH", F.RED + S.DIM),
                    from_user=f.collect_FU(message)
                )
            await state.clear()
        except ValueError:
            await message.answer(txt.LPAA.BAD_ARG)
            tracker.log(
                command=("INFO", F.YELLOW + S.NORMAL),
                status=("BAD_ARG", F.RED + S.DIM),
                from_user=f.collect_FU(message)
            )
    except Exception as e:
        tracker.error(
            e=e,
            userID=message.from_user.id
        )


# MACHINE
@rtr.message(Command("machine"), mF.chat.id == cfg.HIGH_GROUP)
async def machine_info(message: Message):
    try:
        f.update_config(config, [txt, cfg, main_keyboard])
        firewall_status = firewall3.check(message.from_user.id)
        if firewall_status == firewall3.WHITE_ANCHOR:
            python_processes = list()
            for running_process in process_iter():
                if running_process.name() == "python.exe" and len(running_process.cmdline()) > 0 and running_process.cmdline()[-1] == f'lypay_{cfg.VERSION}_launch_stamp':
                    python_processes.append(running_process)
            if len(python_processes) == 0:
                exelink.warn(
                    text=txt.EXE.ALERTS.NO_PROCESS_PYTHON,
                    userID=message.from_user.id
                )

            r = RAM()

            await message.answer(txt.LPAA.INFO.MACHINE_INFO_TABLET.format(
                cpu=f"{CPU():.1f}",
                ram_p=f"{r.percent:.1f}",
                ram_v=f"{(r.total - r.available) / 1073741824:.3f}",
                cpu_build=f"{sum(list(map(lambda p: p.cpu_percent(), python_processes))) / len(python_processes):.2f}",
                ram_build_p=f"{sum(list(map(lambda p: p.memory_percent(), python_processes))) / len(python_processes):.2f}",
                ram_build_v=f"{sum(list(map(lambda p: p.memory_info().rss, python_processes))) / 1073741824 / len(python_processes):.3f}",
                cpu_cores='\n'.join([f" ❯ {n+1}: {p}%" for n, p in enumerate(CPU(percpu=True))])
            ))
            tracker.log(
                command=("MACHINE_INFO", F.LIGHTMAGENTA_EX),
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
