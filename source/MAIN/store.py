from aiogram import Router
from aiogram.types import Message, FSInputFile, CallbackQuery, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.fsm.context import FSMContext
from aiogram import F as mF

from aiofiles import open as a_open
from asyncio import sleep
from datetime import datetime
from os import listdir
from os.path import exists
from colorama import Fore as F, Style as S

from scripts import j2, i, f, firewall3, tracker, exelink, lpsql
from scripts.unix import unix
from data import config as cfg, txt

import source.MAIN._keyboards as main_keyboard
from source.MAIN._states import *


rtr = Router()
config = [j2.fromfile(cfg.PATHS.LAUNCH_SETTINGS)["config_v"]]
firewall3 = firewall3.FireWall('MAIN')
db = lpsql.DataBase("lypay_database.db", lpsql.Tables.MAIN)
print("MAIN/store router")


@rtr.message(mF.text == "🛍 Покупка")
async def store(message: Message, state: FSMContext):
    try:
        f.update_config(config, [txt, cfg, main_keyboard])
        if (await j2.fromfile_async(cfg.PATHS.LAUNCH_SETTINGS))["main_can_deposit"]:
            if message.from_user.id in db.searchall("users", "ID"):
                firewall_status = firewall3.check(message.from_user.id)
                if firewall_status == firewall3.WHITE_ANCHOR:
                    tracker.log(
                        command=("STORE", F.MAGENTA),
                        status=("OK", F.GREEN),
                        from_user=f.collect_FU(message)
                    )
                    await message.answer(txt.MAIN.STORE.ID_CHOOSE,
                                         reply_markup=main_keyboard.update_keyboard(message.from_user.id, True))
                    await state.set_state(StoreFSM.ID)
                elif firewall_status == firewall3.BLACK_ANCHOR:
                    tracker.black(f.collect_FU(message))
                    await message.answer(txt.MAIN.CMD.IN_BLACKLIST)
                else:
                    tracker.gray(f.collect_FU(message))
                    await message.answer(txt.MAIN.CMD.NOT_IN_WHITELIST)
            else:
                tracker.log(
                    command=("STORE", F.MAGENTA),
                    status=("NOT_REGISTERED", F.RED),
                    from_user=f.collect_FU(message)
                )
                await message.answer(txt.MAIN.REGISTRATION.NOT_REGISTERED)
        else:
            tracker.log(
                command=("STORE", F.MAGENTA),
                status=("SETTINGS_ACTION_FORBIDDEN", F.RED),
                from_user=f.collect_FU(message)
            )
            await message.answer(txt.MAIN.STORE.FORBIDDEN_BY_SETTINGS)
    except Exception as e:
        tracker.error(
            e=e,
            userID=message.from_user.id
        )


@rtr.message(StoreFSM.ID, mF.text)
async def choose_store(message: Message, state: FSMContext):
    try:
        f.update_config(config, [txt, cfg, main_keyboard])
        censor = tracker.censor(
            from_user=f.collect_FU(message),
            text=message.text
        )
        if not censor:
            await message.answer(txt.MAIN.CMD.CENSOR_BLACK)
            return
        text = message.text.lower().replace('а', 'a').replace('с', 'c').replace('е', 'e')

        current = db.search("stores", "ID", text)

        if current is None:
            await message.answer(txt.MAIN.STORE.ID_WRONG)
            tracker.log(
                command=("STORE", F.MAGENTA),
                status=("FAIL", F.RED + S.NORMAL),
                from_user=f.collect_FU(message)
            )
        else:
            if not current["logo"]:
                await message.answer(txt.MAIN.STORE.ID_OK.format(
                    name=current["name"],
                    description=current["description"]
                ))
            else:
                logo = db.search("logotypes", "storeID", text)
                if logo is None or logo["fileID_main"] is None:
                    fileid = (await message.answer_photo(FSInputFile(cfg.PATHS.STORES_LOGOS + f"{text}.jpg"),
                                                         caption=txt.MAIN.STORE.ID_OK.format(
                                                             name=current["name"],
                                                             description=current["description"]
                                                         ))).photo[-1].file_id
                    try:
                        db.update("logotypes", "storeID", text, "fileID_main", fileid)
                    except lpsql.errors.EntryNotFound:
                        db.insert("logotypes",
                                  [
                                         text,      # storeID
                                         fileid,    # fileID_main
                                         None       # fileID_lpsb
                                     ])
                else:
                    await message.answer_photo(logo["fileID_main"],
                                               caption=txt.MAIN.STORE.ID_OK.format(
                                                   name=current["name"],
                                                   description=current["description"]
                                               ))
            await state.update_data(ID=text)
            await state.update_data(ITEM=list())
            await state.update_data(MULTIPLIER=list())
            await state.set_state(StoreFSM.ITEM)
            keyboard, real_items, count = await proceed_store_keyboard(text)
            await state.update_data(REAL=real_items)
            m_id = (await message.answer(
                txt.MAIN.STORE.ITEMS.format(
                    items_empty='' if count > 0 else 'в данный момент здесь ничего нет',
                    flag='' if len(db.search("changing", "storeID", text, True)) == 0 else txt.MAIN.STORE.WARNING_ON_CHANGE
                ),
                reply_markup=keyboard.as_markup()
            )).message_id
            if count > 0:
                exelink.sublist(
                    mode='add',
                    name='ccc/main',
                    key=message.chat.id,
                    data=m_id,
                    userID=message.from_user.id
                )
            tracker.log(
                command=("STORE", F.MAGENTA),
                status=("CONFIRMED", F.GREEN + S.NORMAL),
                from_user=f.collect_FU(message)
            )
    except Exception as e:
        tracker.error(
            e=e,
            userID=message.from_user.id
        )


async def proceed_store_keyboard(store_id: str) -> tuple[InlineKeyboardBuilder, list[dict[str, ...]], int]:
    """
    :param store_id: ID магазина
    :return: tuple(клавиатура с товарами, список распакованных товров, количество товаров в клавиатуре)
    """
    keyboard = InlineKeyboardBuilder()
    data = list()
    c = 0
    if exists(cfg.PATHS.STORES_KEYBOARDS + store_id):
        for file in listdir(cfg.PATHS.STORES_KEYBOARDS + store_id):
            js = await j2.fromfile_async(cfg.PATHS.STORES_KEYBOARDS + store_id + '\\' + file)
            keyboard.add(InlineKeyboardButton(
                text=f"{f.de_anchor(js["text"])}  |  {js["price"]} {cfg.VALUTA.SHORT}",
                callback_data=js["call"])
            )
            js.pop("call")
            data.append(js)
            c += 1
        keyboard.adjust(1)
    return keyboard, data, c


@rtr.callback_query(StoreFSM.ITEM, mF.data.find("store_") != -1)
async def store_callback(callback: CallbackQuery, state: FSMContext):
    try:
        f.update_config(config, [txt, cfg, main_keyboard])
        data = await state.get_data()
        item_ = data["REAL"][i.to_int(callback.data.split('_')[2]) - 1]
        await state.set_state(StoreFSM.MULTIPLIER)
        state_saved = data["ITEM"]
        state_saved.append(item_)
        await state.update_data(ITEM=state_saved)
        await callback.message.edit_text(txt.MAIN.STORE.MULTIPLIER.MAIN.format(
            item=f.de_anchor(item_["text"]),
            amount=item_["price"]
        ))
        await callback.answer()
        tracker.log(
            command=("STORE", F.MAGENTA),
            status=("ITEM_CHOOSED", F.GREEN + S.NORMAL),
            from_user=f.collect_FU(callback)
        )
    except Exception as e:
        tracker.error(
            e=e,
            userID=callback.from_user.id
        )


@rtr.message(StoreFSM.MULTIPLIER, mF.text)
async def store_multiplier(message: Message, state: FSMContext):
    try:
        f.update_config(config, [txt, cfg, main_keyboard])
        censor = tracker.censor(
            from_user=f.collect_FU(message),
            text=message.text
        )
        if not censor:
            await message.answer(txt.MAIN.CMD.CENSOR_BLACK)
            return
        if message.text.isnumeric():
            multiplier = int(message.text)
            if multiplier == 0:
                await message.answer(txt.MAIN.STORE.MULTIPLIER.PURCHASED_0)
                tracker.log(
                    command=("STORE", F.MAGENTA),
                    status=("TRIED_0", F.LIGHTRED_EX + S.BRIGHT),
                    from_user=f.collect_FU(message)
                )
            else:
                state_saved = await state.get_data()
                state_saved["MULTIPLIER"].append(multiplier)

                if state_saved["ITEM"][-1] in state_saved["ITEM"][:-1]:
                    index = state_saved["ITEM"][:-1].index(state_saved["ITEM"][-1])
                    state_saved["MULTIPLIER"][index] += multiplier
                    state_saved["MULTIPLIER"] = state_saved["MULTIPLIER"][:-1]
                    state_saved["ITEM"] = state_saved["ITEM"][:-1]
                    await state.update_data(ITEM=state_saved["ITEM"])

                await state.update_data(MULTIPLIER=state_saved["MULTIPLIER"])
                items_ = state_saved["ITEM"]
                multipliers_ = state_saved["MULTIPLIER"]
                generated_strings = list()
                total_all = 0
                for i in range(len(items_)):
                    total_i = items_[i]["price"] * multipliers_[i]
                    total_all += total_i
                    generated_strings.append(f"{f.de_anchor(items_[i]["text"])} × {multipliers_[i]} | {total_i} {cfg.VALUTA.SHORT}")
                m_id = (await message.answer(
                    txt.MAIN.STORE.CONFIRM.format(
                        items='\n'.join(generated_strings),
                        total=total_all
                    ),
                    reply_markup=main_keyboard.storeCMD
                )).message_id
                exelink.sublist(
                    mode='add',
                    name='ccc/main',
                    key=message.chat.id,
                    data=m_id,
                    userID=message.from_user.id
                )
                await state.set_state(StoreFSM.CONFIRM)
                tracker.log(
                    command=("STORE", F.MAGENTA),
                    status=("TO_CONFIRM", F.LIGHTBLUE_EX + S.BRIGHT),
                    from_user=f.collect_FU(message)
                )
        else:
            await message.answer(txt.MAIN.STORE.MULTIPLIER.BAD_VALUE)
            tracker.log(
                command=("STORE", F.MAGENTA),
                status=("BAD_VALUE", F.LIGHTRED_EX + S.BRIGHT),
                from_user=f.collect_FU(message)
            )
    except Exception as e:
        tracker.error(
            e=e,
            userID=message.from_user.id
        )


@rtr.callback_query(StoreFSM.CONFIRM, mF.data == "store_cancel_cb")
async def store_cancel(callback: CallbackQuery, state: FSMContext):
    try:
        f.update_config(config, [txt, cfg, main_keyboard])
        await callback.message.edit_text(callback.message.text + "\n> 'Отменить покупку'")
        await callback.message.answer(txt.MAIN.STORE.PROCESS_CANCELED,
                                      reply_markup=main_keyboard.update_keyboard(callback.from_user.id))
        await callback.answer()
        exelink.sublist(
            mode='remove',
            name='ccc/main',
            key=callback.message.chat.id,
            userID=callback.from_user.id
        )
        await state.clear()
        tracker.log(
            command=("STORE", F.MAGENTA),
            status=("CANCELLED", F.RED),
            from_user=f.collect_FU(callback)
        )
    except Exception as e:
        tracker.error(
            e=e,
            userID=callback.from_user.id
        )


@rtr.callback_query(StoreFSM.CONFIRM, mF.data == "store_continue_cb")
async def store_continue(callback: CallbackQuery, state: FSMContext):
    try:
        f.update_config(config, [txt, cfg, main_keyboard])
        last_text = callback.message.text
        await callback.message.edit_text(last_text[:last_text.rfind('\n')] + "\nВыбрано 'Продолжить покупку'")
        await callback.answer()
        await state.set_state(StoreFSM.ITEM)
        keyboard, real_items, count = await proceed_store_keyboard((await state.get_data())["ID"])
        await state.update_data(REAL=real_items)
        m_id = (await callback.message.answer(
            txt.MAIN.STORE.ITEMS.format(
                items_empty='' if count > 0 else 'в данный момент здесь ничего нет',
                flag='' if len(db.search("changing", "storeID", (await state.get_data())["ID"],
                                         True)) == 0 else txt.MAIN.STORE.WARNING_ON_CHANGE
            ),
            reply_markup=keyboard.as_markup()
        )).message_id
        exelink.sublist(
            mode='add',
            name='ccc/main',
            key=callback.message.chat.id,
            data=m_id,
            userID=callback.from_user.id
        )
        if count == 0:
            await callback.message.answer(txt.MAIN.STORE.NO_ITEMS_FATAL,
                                          reply_markup=main_keyboard.update_keyboard(callback.from_user.id))
            await state.clear()
            tracker.log(
                command=("STORE", F.MAGENTA),
                status=("NO_ITEMS_FATAL", F.RED + S.BRIGHT),
                from_user=f.collect_FU(callback)
            )
        else:
            tracker.log(
                command=("STORE", F.MAGENTA),
                status=("CONTINUE", F.CYAN),
                from_user=f.collect_FU(callback)
            )
    except Exception as e:
        tracker.error(
            e=e,
            userID=callback.from_user.id
        )


@rtr.callback_query(StoreFSM.CONFIRM, mF.data == "store_confirm_cb")
async def store_purchase(callback: CallbackQuery, state: FSMContext):
    try:
        f.update_config(config, [txt, cfg, main_keyboard])
        _data_ = await state.get_data()
        user_ = db.search("users", "ID", callback.from_user.id)
        id_ = _data_["ID"]
        items_ = _data_["ITEM"]
        multipliers_ = _data_["MULTIPLIER"]

        generated_strings = list()
        total_all = 0
        for k in range(len(items_)):
            total_k = items_[k]["price"] * multipliers_[k]
            total_all += total_k
            generated_strings.append(f"{f.de_anchor(items_[k]["text"])} × {multipliers_[k]} | {total_k} {cfg.VALUTA.SHORT}")

        try:
            db.transfer(callback.from_user.id, id_, total_all)
            tracker.log(
                command=("STORE", F.MAGENTA),
                status=("BUY", F.YELLOW),
                from_user=f.collect_FU(callback)
            )

            cheque_id = f"{callback.from_user.id}_{id_}_{datetime.now().strftime('%H%M%S')}"
            async with a_open(cfg.PATHS.STORES_CHEQUES + f"{cheque_id}.json", 'w', encoding='utf8') as cheque:
                await cheque.write(j2.to_({
                    "unix": unix(),
                    "customer": callback.from_user.id,
                    "price": total_all,
                    "items": items_,
                    "multipliers": multipliers_,
                    "status": True
                }))

            await sleep(.01)
            exelink.cheque(
                participantStoreID=id_,
                chequeID=cheque_id,
                userID=callback.from_user.id
            )

            await callback.message.edit_text(txt.MAIN.STORE.SUCCESSFUL_1)
            await callback.message.answer(
                txt.MAIN.STORE.SUCCESSFUL_2.format(
                    cheque_id=cheque_id,
                    total=total_all,
                    id=id_,
                    items=txt.MAIN.STORE.CHEQUE_GENERATED_STRINGS_SEPARATOR.join(generated_strings)
                ),
                reply_markup=main_keyboard.update_keyboard(callback.from_user.id)
            )
            await callback.answer()
            exelink.sublist(
                mode='remove',
                name='ccc/main',
                key=callback.message.chat.id,
                userID=callback.from_user.id
            )

            if total_all >= 5000:
                exelink.warn(
                    text=txt.MAIN.STORE.WARNING_5K.format(
                        store=id_,
                        name=user_["name"],
                        group=user_["class"],
                        tag='@'+user_["tag"] if user_["tag"] else '–',
                        total=total_all,
                        cheque=cheque_id
                    ),
                    userID=callback.from_user.id
                )
            await state.clear()
        except lpsql.errors.NotEnoughBalance:
            await callback.message.edit_text(txt.MAIN.STORE.NOT_ENOUGH)
            await callback.message.answer(txt.MAIN.STORE.ID_CHOOSE_PAST)
            await callback.answer()
            exelink.sublist(
                mode='remove',
                name='ccc/main',
                key=callback.message.chat.id,
                userID=callback.from_user.id
            )
            tracker.log(
                command=("STORE", F.MAGENTA),
                status=("NOT_ENOUGH_MONEY", F.RED),
                from_user=f.collect_FU(callback)
            )
            await state.clear()
            await state.set_state(StoreFSM.ID)
    except Exception as e:
        tracker.error(
            e=e,
            userID=callback.from_user.id
        )
