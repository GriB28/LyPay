from aiogram import Router
from aiogram.types import Message, CallbackQuery
from aiogram.filters.command import Command
from aiogram.fsm.context import FSMContext
from aiogram import F as mF

from colorama import Fore as F, Style as S
from os import mkdir, listdir, remove
from os.path import exists
from shutil import rmtree

from scripts import j2, i, f, tracker, lpsql, exelink
from data import config as cfg, txt


from source.LPSB._states import *
import source.LPSB._keyboards as main_keyboard


rtr = Router()
config = [j2.fromfile(cfg.PATHS.LAUNCH_SETTINGS)["config_v"]]
db = lpsql.DataBase("lypay_database.db", lpsql.Tables.MAIN)
print("LPSB/menu/items subrouter")


@rtr.callback_query(MenuFSM.MENU, mF.data == "items_cb")
async def items(callback: CallbackQuery):
    try:
        f.update_config(config, [txt, cfg, main_keyboard])
        await callback.message.edit_text(
            "Главное меню\n> 'Ассортимент 📋'",
            reply_markup=main_keyboard.menuCMD["items"]
        )
        await callback.answer()
        tracker.log(
            command=("MENU", F.BLUE + S.BRIGHT),
            status=("ITEMS_ROUTE", F.YELLOW + S.DIM),
            from_user=f.collect_FU(callback)
        )
    except Exception as e:
        tracker.error(
            e=e,
            userID=callback.from_user.id
        )


@rtr.callback_query(mF.data == "items_now_cb")
async def display_current_items(callback: CallbackQuery, state: FSMContext):
    try:
        f.update_config(config, [txt, cfg, main_keyboard])
        await callback.message.edit_text(f"{callback.message.text}\n> 'Текущий ассортимент'")
        await callback.answer()
        try:
            id_ = db.search("shopkeepers", "userID", callback.from_user.id)["storeID"]
            path_ = cfg.PATHS.STORES_KEYBOARDS + id_
            if exists(path_):
                listdir_ = listdir(path_)
                if len(listdir_) > 0:
                    for k in listdir_:
                        js = await j2.fromfile_async(path_ + '\\' + k)
                        await callback.message.answer(f'<code>{f.de_anchor(js["text"])} / {js["price"]}</code>')
                else:
                    await callback.message.answer(txt.LPSB.ITEMS.NOT_EXIST)
            else:
                await callback.message.answer(txt.LPSB.ITEMS.NOT_EXIST)
            tracker.log(
                command=("MENU", F.BLUE + S.BRIGHT),
                status=("CURRENT_ITEMS", F.GREEN + S.DIM),
                from_user=f.collect_FU(callback)
            )
        except:
            await callback.message.answer(txt.LPSB.ITEMS.SOMETHING_WENT_WRONG)
            tracker.log(
                command=("MENU", F.BLUE + S.BRIGHT),
                status=("CURRENT_ITEMS_FAIL", F.RED + S.DIM),
                from_user=f.collect_FU(callback)
            )
        await state.clear()
        exelink.sublist(
            mode='remove',
            name='ccc/lpsb',
            key=callback.message.chat.id,
            userID=callback.from_user.id
        )
    except Exception as e:
        tracker.error(
            e=e,
            userID=callback.from_user.id
        )


@rtr.callback_query(mF.data == "items_new_cb")
async def create_new_item(callback: CallbackQuery, state: FSMContext):
    try:
        f.update_config(config, [txt, cfg, main_keyboard])
        await callback.message.edit_text(f"{callback.message.text}\n> 'Добавить новые товары'")
        await callback.answer()
        try:
            id_ = db.search("shopkeepers", "userID", callback.from_user.id)["storeID"]
            path_ = cfg.PATHS.STORES_KEYBOARDS + id_
            db.insert("changing", [callback.from_user.id, id_])

            if not exists(path_):
                mkdir(path_)
                last_ = 0
            elif len(listdir(path_)) == 0:
                last_ = 0
            else:
                last_ = i.to_int(listdir(path_)[-1][:-5])

            await state.set_state(MenuFSM.ITEMS_NEW)
            await state.update_data(ITEMS_NEW=[last_, list()])

            await callback.message.answer(txt.LPSB.ITEMS.START)
            await callback.message.answer(txt.LPSB.ITEMS.EG_1)
            await callback.message.answer(txt.LPSB.ITEMS.EG_2)

            tracker.log(
                command=("MENU", F.BLUE + S.BRIGHT),
                status=("ADD_NEW", F.GREEN + S.DIM),
                from_user=f.collect_FU(callback)
            )
        except:
            await callback.message.answer(txt.LPSB.ITEMS.SOMETHING_WENT_WRONG)
            await state.clear()
            tracker.log(
                command=("MENU", F.BLUE + S.BRIGHT),
                status=("ADD_NEW_FAIL", F.RED + S.DIM),
                from_user=f.collect_FU(callback)
            )
        exelink.sublist(
            mode='remove',
            name='ccc/lpsb',
            key=callback.message.chat.id,
            userID=callback.from_user.id
        )
    except Exception as e:
        tracker.error(
            e=e,
            userID=callback.from_user.id
        )


@rtr.message(Command("stop"), MenuFSM.ITEMS_NEW)
async def stop_filling(message: Message, state: FSMContext):
    try:
        f.update_config(config, [txt, cfg, main_keyboard])
        data = (await state.get_data())["ITEMS_NEW"]
        try:
            id_ = db.search("shopkeepers", "userID", message.from_user.id)["storeID"]
            path = cfg.PATHS.STORES_KEYBOARDS + id_
            try:
                while True:
                    db.delete("changing", message.from_user.id, id_)
            except lpsql.errors.EntryNotFound:
                pass

            for k in range(len(data[1])):
                with open(path + f'\\{i.to_id(k + 1 + data[0])}.json', 'w', encoding='utf8') as file:
                    file.write(j2.to_({
                        "text": data[1][k][0],
                        "price": int(data[1][k][1]),
                        "call": f"store_{id_}_{i.to_id(k + 1 + data[0])}_cb"
                    }))

            tracker.log(
                command=("MENU", F.BLUE + S.BRIGHT),
                status=("CONFIRM_ITEMS", F.MAGENTA + S.DIM),
                from_user=f.collect_FU(message)
            )
            await message.answer(txt.LPSB.ITEMS.END)
        except:
            await message.answer(txt.LPSB.ITEMS.SOMETHING_WENT_WRONG)
            tracker.log(
                command=("MENU", F.BLUE + S.BRIGHT),
                status=("CONFIRM_ITEMS_FAIL", F.RED + S.DIM),
                from_user=f.collect_FU(message)
            )
        await state.clear()
    except Exception as e:
        tracker.error(
            e=e,
            userID=message.from_user.id
        )


@rtr.message(mF.text, MenuFSM.ITEMS_NEW)
async def fill_item(message: Message, state: FSMContext):
    try:
        f.update_config(config, [txt, cfg, main_keyboard])
        censor = tracker.censor(
            from_user=f.collect_FU(message),
            text=message.text
        )
        if not censor:
            await message.answer(txt.MAIN.CMD.CENSOR_BLACK)
            return
        split_ = message.text.split('/')
        parse = [(split_[k].strip() if k > len(split_) - 3 else split_[k]) for k in range(len(split_))]

        if len(parse) >= 2 and parse[-1].isnumeric():
            try:
                p = int(parse[-1])  # если не число - бахает
                if p <= 0:
                    await message.answer(txt.LPSB.ITEMS.TRIED_0)
                    tracker.log(
                        command=("MENU", F.BLUE + S.BRIGHT),
                        status=("NEW_ITEM_TRIED_0", F.RED + S.DIM),
                        from_user=f.collect_FU(message)
                    )
                else:
                    parsed_name = f.anchor('/'.join(parse[:-1]))
                    items_ = (await state.get_data())["ITEMS_NEW"]
                    items_[1].append([parsed_name, p])
                    await state.update_data(ITEMS_NEW=items_)

                    await message.answer(txt.LPSB.ITEMS.OK)
                    tracker.log(
                        command=("MENU", F.BLUE + S.BRIGHT),
                        status=("NEW_ITEM", F.MAGENTA + S.DIM),
                        from_user=f.collect_FU(message)
                    )
            except:
                await message.answer(txt.LPSB.ITEMS.BAD)
                tracker.log(
                    command=("MENU", F.BLUE + S.BRIGHT),
                    status=("NEW_ITEM_NOT_NUM", F.RED + S.DIM),
                    from_user=f.collect_FU(message)
                )
        else:
            await message.answer(txt.LPSB.ITEMS.BAD)
            tracker.log(
                command=("MENU", F.BLUE + S.BRIGHT),
                status=("NEW_ITEM_WRONG", F.RED + S.DIM),
                from_user=f.collect_FU(message)
            )
    except Exception as e:
        tracker.error(
            e=e,
            userID=message.from_user.id
        )


@rtr.callback_query(mF.data == "items_delete_cb")
async def delete_items(callback: CallbackQuery, state: FSMContext):
    try:
        f.update_config(config, [txt, cfg, main_keyboard])
        await callback.message.edit_text(f"{callback.message.text}\n> 'Удалить всё'")
        await callback.answer()

        try:
            id_ = db.search("shopkeepers", "userID", callback.from_user.id)["storeID"]
            try:
                while True:
                    db.delete("changing", callback.from_user.id, id_)
            except lpsql.errors.EntryNotFound:
                pass

            await state.set_state(MenuFSM.ITEMS_DELETE)
            await callback.message.answer(txt.LPSB.ITEMS.DELETE)
            tracker.log(
                command=("MENU", F.BLUE + S.BRIGHT),
                status=("DELETE_REQUEST", F.RED + S.BRIGHT),
                from_user=f.collect_FU(callback)
            )
        except:
            await callback.message.answer(txt.LPSB.ITEMS.SOMETHING_WENT_WRONG)
            await state.clear()
            exelink.sublist(
                mode='remove',
                name='ccc/lpsb',
                key=callback.message.chat.id,
                userID=callback.from_user.id
            )
            tracker.log(
                command=("MENU", F.BLUE + S.BRIGHT),
                status=("DELETE_REQUEST_FAIL", F.RED + S.DIM),
                from_user=f.collect_FU(callback)
            )
        exelink.sublist(
            mode='remove',
            name='ccc/lpsb',
            key=callback.message.chat.id,
            userID=callback.from_user.id
        )
    except Exception as e:
        tracker.error(
            e=e,
            userID=callback.from_user.id
        )


@rtr.message(mF.text, MenuFSM.ITEMS_DELETE)
async def delete_items_confirmed(message: Message, state: FSMContext):
    try:
        f.update_config(config, [txt, cfg, main_keyboard])
        if message.text == "ПОДТВЕРЖДАЮ":
            try:
                id_ = db.search("shopkeepers", "userID", message.from_user.id)["storeID"]
                path_ = cfg.PATHS.STORES_KEYBOARDS + id_
                rmtree(path_)
                mkdir(path_)
                try:
                    while True:
                        db.delete("changing", message.from_user.id, id_)
                except lpsql.errors.EntryNotFound:
                    pass

                await message.answer(txt.LPSB.ITEMS.DELETE_OK)
                await state.clear()
                tracker.log(
                    command=("MENU", F.BLUE + S.BRIGHT),
                    status=("DELETE_ALL_CONFIRM", F.RED + S.BRIGHT),
                    from_user=f.collect_FU(message)
                )
            except:
                await message.answer(txt.LPSB.ITEMS.SOMETHING_WENT_WRONG)
                await state.clear()
                tracker.log(
                    command=("MENU", F.BLUE + S.BRIGHT),
                    status=("DELETE_ALL_FAIL", F.RED + S.DIM),
                    from_user=f.collect_FU(message)
                )
        else:
            await message.answer(txt.LPSB.ITEMS.DELETE_FAIL)
            tracker.log(
                command=("MENU", F.BLUE + S.BRIGHT),
                status=("DELETE_ALL_FAIL", F.RED + S.DIM),
                from_user=f.collect_FU(message)
            )
    except Exception as e:
        tracker.error(
            e=e,
            userID=message.from_user.id
        )


@rtr.callback_query(mF.data == "items_edit_cb")
async def edit_items(callback: CallbackQuery, state: FSMContext):
    try:
        f.update_config(config, [txt, cfg, main_keyboard])
        await callback.message.edit_text(f"{callback.message.text}\n> 'Изменить существующие'")
        await callback.answer()
        await state.set_state(MenuFSM.ITEMS_EDIT)

        try:
            id_ = db.search("shopkeepers", "userID", callback.from_user.id)["storeID"]
            try:
                while True:
                    db.delete("changing", callback.from_user.id, id_)
            except lpsql.errors.EntryNotFound:
                pass

            edit_item_message = await callback.message.answer("%")
            await edit_item(edit_item_message, callback, state, 1)
            exelink.sublist(
                mode='add',
                name='ccc/lpsb',
                key=callback.message.chat.id,
                data=edit_item_message.message_id,
                userID=callback.from_user.id
            )
            tracker.log(
                command=("MENU", F.BLUE + S.BRIGHT),
                status=("EDIT_ITEM", F.YELLOW + S.BRIGHT),
                from_user=f.collect_FU(callback)
            )
        except:
            await callback.message.answer(txt.LPSB.ITEMS.SOMETHING_WENT_WRONG)
            await state.clear()
            tracker.log(
                command=("MENU", F.BLUE + S.BRIGHT),
                status=("EDIT_ITEM_FAIL", F.RED + S.BRIGHT),
                from_user=f.collect_FU(callback)
            )
            exelink.sublist(
                mode='remove',
                name='ccc/lpsb',
                key=callback.message.chat.id,
                userID=callback.from_user.id
            )
    except Exception as e:
        tracker.error(
            e=e,
            userID=callback.from_user.id
        )


async def edit_item(message: Message, callback: CallbackQuery, state: FSMContext, n: int):
    try:
        id_ = db.search("shopkeepers", "userID", callback.from_user.id)["storeID"]
        path_ = cfg.PATHS.STORES_KEYBOARDS + id_
        if exists(path_) and len(listdir(path_)) > 0:
            if n > i.to_int(listdir(path_)[-1][:-5]):
                await message.edit_text(txt.LPSB.ITEMS.OVER)
                await state.clear()
                exelink.sublist(
                    mode='remove',
                    name='ccc/lpsb',
                    key=callback.message.chat.id,
                    userID=callback.from_user.id
                )
                try:
                    while True:
                        db.delete("changing", message.from_user.id, id_)
                except lpsql.errors.EntryNotFound:
                    pass
                return
            await state.update_data(ITEMS_EDIT=n)
            js = await j2.fromfile_async(path_ + f'\\{i.to_id(n)}.json')
            new_string = f'<code>{f.de_anchor(js["text"])} / {js["price"]}</code>'
            if new_string != message.text:
                await message.edit_text(new_string, reply_markup=main_keyboard.menuCMD["items_edit"])
            tracker.log(
                command=("MENU", F.BLUE + S.BRIGHT),
                status=("EDIT_ITEM_CHAIN", F.CYAN + S.DIM),
                from_user=f.collect_FU(callback)
            )
        else:
            try:
                while True:
                    db.delete("changing", message.from_user.id, id_)
            except lpsql.errors.EntryNotFound:
                pass

            await message.edit_text(txt.LPSB.ITEMS.NOT_EXIST)
            await state.clear()
            exelink.sublist(
                mode='remove',
                name='ccc/lpsb',
                key=callback.message.chat.id,
                userID=callback.from_user.id
            )
            tracker.log(
                command=("MENU", F.BLUE + S.BRIGHT),
                status=("NO_ITEMS", F.CYAN + S.DIM),
                from_user=f.collect_FU(callback)
            )
    except:
        try:
            id_ = db.search("shopkeepers", "userID", callback.from_user.id)["storeID"]
            try:
                while True:
                    db.delete("changing", message.from_user.id, id_)
            except lpsql.errors.EntryNotFound:
                pass
        except:
            pass
        await message.edit_text(txt.LPSB.ITEMS.SOMETHING_WENT_WRONG)
        await state.clear()
        exelink.sublist(
            mode='remove',
            name='ccc/lpsb',
            key=callback.message.chat.id,
            userID=callback.from_user.id
        )
        tracker.log(
            command=("MENU", F.BLUE + S.BRIGHT),
            status=("EDIT_ITEM_CHAIN_FAIL", F.RED + S.DIM),
            from_user=f.collect_FU(callback)
        )


@rtr.callback_query(mF.data == "current_item_edit_cb")
async def actual_edit_item(callback: CallbackQuery, state: FSMContext):
    try:
        f.update_config(config, [txt, cfg, main_keyboard])
        await callback.message.edit_text(txt.LPSB.ITEMS.EDIT_TEXT % callback.message.text)
        await callback.answer()
        await state.set_state(MenuFSM.ITEMS_WAIT_FOR_EDIT)
        await state.update_data(ITEMS_WAIT_FOR_EDIT=callback)
        tracker.log(
            command=("MENU", F.BLUE + S.BRIGHT),
            status=("EDITING_ITEM", F.YELLOW + S.DIM),
            from_user=f.collect_FU(callback)
        )
        exelink.sublist(
            mode='remove',
            name='ccc/lpsb',
            key=callback.message.chat.id,
            userID=callback.from_user.id
        )
    except Exception as e:
        tracker.error(
            e=e,
            userID=callback.from_user.id
        )


@rtr.message(mF.text, MenuFSM.ITEMS_WAIT_FOR_EDIT)
async def edit_item_data(message: Message, state: FSMContext):
    try:
        f.update_config(config, [txt, cfg, main_keyboard])
        censor = tracker.censor(
            from_user=f.collect_FU(message),
            text=message.text
        )
        if not censor:
            await message.answer(txt.MAIN.CMD.CENSOR_BLACK)
            return
        data = (await state.get_data())
        try:
            id_ = db.search("shopkeepers", "userID", message.from_user.id)["storeID"]
            try:
                n = data["ITEMS_EDIT"]
                split_ = message.text.split('/')
                parse = [split_[k].strip() for k in range(len(split_)) if len(split_[k].strip()) > 0]

                if len(parse) == 2 and parse[1].isnumeric():
                    path_ = cfg.PATHS.STORES_KEYBOARDS + id_

                    if exists(path_):
                        with open(path_ + f'\\{i.to_id(n)}.json', 'w', encoding='utf8') as file:
                            file.write(j2.to_({
                                "text": f.anchor(parse[0]),
                                "price": int(parse[1]),
                                "call": f"store_{id_}_{i.to_id(n)}_cb"
                            }))
                        await message.answer(txt.LPSB.ITEMS.EDIT_OK)
                        tracker.log(
                            command=("MENU", F.BLUE + S.BRIGHT),
                            status=("EDIT_ITEM", F.MAGENTA + S.DIM),
                            from_user=f.collect_FU(message)
                        )
                        edit_item_message = await data["ITEMS_WAIT_FOR_EDIT"].message.answer('%')
                        await edit_item(edit_item_message, data["ITEMS_WAIT_FOR_EDIT"], state, n)
                        exelink.sublist(
                            mode='add',
                            name='ccc/lpsb',
                            key=message.chat.id,
                            data=edit_item_message.message_id,
                            userID=message.from_user.id
                        )
                    else:
                        await message.answer(txt.LPSB.ITEMS.NOT_EXIST)
                        tracker.log(
                            command=("MENU", F.BLUE + S.BRIGHT),
                            status=("EDIT_ITEM_ERROR", F.RED + S.DIM),
                            from_user=f.collect_FU(message)
                        )
                        exelink.sublist(
                            mode='remove',
                            name='ccc/lpsb',
                            key=message.chat.id,
                            userID=message.from_user.id
                        )
                else:
                    await message.answer(txt.LPSB.ITEMS.BAD)
                    tracker.log(
                        command=("MENU", F.BLUE + S.BRIGHT),
                        status=("EDIT_ITEM_WRONG", F.RED + S.DIM),
                        from_user=f.collect_FU(message)
                    )
            except:
                await message.answer(txt.LPSB.ITEMS.SOMETHING_WENT_WRONG)
                await state.clear()
                exelink.sublist(
                    mode='remove',
                    name='ccc/lpsb',
                    key=message.chat.id,
                    userID=message.from_user.id
                )

                try:
                    while True:
                        db.delete("changing", message.from_user.id, id_)
                except lpsql.errors.EntryNotFound:
                    pass

                tracker.log(
                    command=("MENU", F.BLUE + S.BRIGHT),
                    status=("EDIT_ITEM_FAIL", F.RED + S.DIM),
                    from_user=f.collect_FU(message)
                )
        except:
            await message.answer(txt.LPSB.ITEMS.SOMETHING_WENT_WRONG)
            await state.clear()
            tracker.log(
                command=("MENU", F.BLUE + S.BRIGHT),
                status=("EDIT_ITEM_FAIL", F.RED + S.DIM),
                from_user=f.collect_FU(message)
            )
            exelink.sublist(
                mode='remove',
                name='ccc/lpsb',
                key=message.chat.id,
                userID=message.from_user.id
            )
    except Exception as e:
        tracker.error(
            e=e,
            userID=message.from_user.id
        )


@rtr.callback_query(mF.data == "current_item_delete_cb")
async def actual_delete_item(callback: CallbackQuery):
    try:
        f.update_config(config, [txt, cfg, main_keyboard])
        await callback.message.edit_text("Вы уверены?", reply_markup=main_keyboard.menuCMD["items_delete"])
        await callback.answer()
        tracker.log(
            command=("MENU", F.BLUE + S.BRIGHT),
            status=("DELETING_ITEM", F.RED + S.DIM),
            from_user=f.collect_FU(callback)
        )
    except Exception as e:
        tracker.error(
            e=e,
            userID=callback.from_user.id
        )


@rtr.callback_query(mF.data == "confirm_delete_item_cb")
async def delete_item_data(callback: CallbackQuery, state: FSMContext):
    try:
        f.update_config(config, [txt, cfg, main_keyboard])
        try:
            id_ = db.search("shopkeepers", "userID", callback.from_user.id)["storeID"]
            path_ = cfg.PATHS.STORES_KEYBOARDS + id_
            data = (await state.get_data())["ITEMS_EDIT"]
            for k in range(data, i.to_int(listdir(path_)[-1][:-5])):
                js_base = j2.fromfile(path_ + f"\\{i.to_id(k)}.json")
                js_copying = j2.fromfile(path_ + f"\\{i.to_id(k + 1)}.json")
                js_base["text"] = js_copying["text"]
                js_base["price"] = js_copying["price"]

                with open(path_ + f"\\{i.to_id(k)}.json", 'w', encoding='utf8') as file:
                    file.write(j2.to_(js_base))

            remove(path_ + '\\' + listdir(path_)[-1])
            await callback.message.edit_text("Товар удалён!")
            await callback.answer()
            edit_item_message = await callback.message.answer('%')
            await edit_item(edit_item_message, callback, state, data)
            exelink.sublist(
                mode='add',
                name='ccc/lpsb',
                key=callback.message.chat.id,
                data=edit_item_message.message_id,
                userID=callback.from_user.id
            )
            tracker.log(
                command=("MENU", F.BLUE + S.BRIGHT),
                status=("ITEM_DELETED", F.RED + S.DIM),
                from_user=f.collect_FU(callback)
            )
        except:
            await callback.answer()
            await callback.message.answer(txt.LPSB.ITEMS.SOMETHING_WENT_WRONG)
            await state.clear()
            exelink.sublist(
                mode='remove',
                name='ccc/lpsb',
                key=callback.message.chat.id,
                userID=callback.from_user.id
            )
            tracker.log(
                command=("MENU", F.BLUE + S.BRIGHT),
                status=("ITEM_DELETE_FAIL", F.RED + S.DIM),
                from_user=f.collect_FU(callback)
            )
    except Exception as e:
        tracker.error(
            e=e,
            userID=callback.from_user.id
        )


@rtr.callback_query(mF.data == "deny_delete_item_cb")
async def deny_deleting(callback: CallbackQuery, state: FSMContext):
    try:
        f.update_config(config, [txt, cfg, main_keyboard])
        await callback.message.edit_text("Удаление отменено!")
        await callback.answer()
        edit_item_message = await callback.message.answer('%')
        await edit_item(edit_item_message, callback, state, (await state.get_data())["ITEMS_EDIT"])
        exelink.sublist(
            mode='add',
            name='ccc/lpsb',
            key=callback.message.chat.id,
            data=edit_item_message.message_id,
            userID=callback.from_user.id
        )
        tracker.log(
            command=("MENU", F.BLUE + S.BRIGHT),
            status=("DELETING_DENIED", F.RED + S.DIM),
            from_user=f.collect_FU(callback)
        )
    except Exception as e:
        tracker.error(
            e=e,
            userID=callback.from_user.id
        )


@rtr.callback_query(mF.data == "current_item_skip_cb")
async def skip_item(callback: CallbackQuery, state: FSMContext):
    try:
        f.update_config(config, [txt, cfg, main_keyboard])
        await callback.answer()
        try:
            await edit_item(callback.message, callback, state, (await state.get_data())["ITEMS_EDIT"] + 1)
            tracker.log(
                command=("MENU", F.BLUE + S.BRIGHT),
                status=("SKIP_ITEM", F.GREEN + S.DIM),
                from_user=f.collect_FU(callback)
            )
        except KeyError:
            await callback.message.edit_text(txt.LPSB.ITEMS.SOMETHING_WENT_WRONG)
            tracker.log(
                command=("MENU", F.BLUE + S.BRIGHT),
                status=("SKIP_ITEM_FAIL", F.RED + S.DIM),
                from_user=f.collect_FU(callback)
            )
            exelink.sublist(
                mode='remove',
                name='ccc/lpsb',
                key=callback.message.chat.id,
                userID=callback.from_user.id
            )
    except Exception as e:
        tracker.error(
            e=e,
            userID=callback.from_user.id
        )


@rtr.callback_query(mF.data == "items_back_cb")
async def back(callback: CallbackQuery, state: FSMContext):
    try:
        f.update_config(config, [txt, cfg, main_keyboard])
        await state.clear()
        await state.set_state(MenuFSM.MENU)
        storeID = db.search("shopkeepers", "userID", callback.from_user.id)["storeID"]
        await callback.message.edit_text(
            txt.LPSB.CMD.MENU_TABLET.format(
                id=storeID,
                balance=db.balance_view(storeID)
            ),
            reply_markup=main_keyboard.menuCMD["main"]
        )
        await callback.answer()
        tracker.log(
            command=("MENU_FROM_ITEMS", F.BLUE + S.BRIGHT),
            from_user=f.collect_FU(callback)
        )
    except Exception as e:
        tracker.error(
            e=e,
            userID=callback.from_user.id
        )
