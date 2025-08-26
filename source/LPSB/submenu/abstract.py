from aiogram import Router
from aiogram.types import CallbackQuery, FSInputFile, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram import F as mF
from aiogram.utils.keyboard import InlineKeyboardBuilder

from colorama import Fore as F, Style as S
from os import listdir
from os.path import exists

from scripts import j2, f, tracker, lpsql, exelink
from data import config as cfg, txt

from source.LPSB._states import *


rtr = Router()
config = [j2.fromfile(cfg.PATHS.LAUNCH_SETTINGS)["config_v"]]
db = lpsql.DataBase("lypay_database.db", lpsql.Tables.MAIN)
print("LPSB/menu/abstract subrouter")


@rtr.callback_query(MenuFSM.MENU, mF.data == "statistics_cb")
async def statistics(callback: CallbackQuery, state: FSMContext):
    try:
        f.update_config(config, [txt, cfg])
        await callback.message.edit_text("Главное меню\n> 'Статистика 📈'")
        await callback.answer()
        try:
            id_ = db.search("shopkeepers", "userID", callback.from_user.id)["storeID"]

            items_ = dict()
            balance_ = 0
            for cheque in listdir(cfg.PATHS.STORES_CHEQUES):
                store_ = cheque.split('_')[1]
                if store_ == id_:
                    js_ = j2.fromfile(cfg.PATHS.STORES_CHEQUES + cheque)
                    if js_["status"]:
                        for k in range(len(js_["items"])):
                            item_ = js_["items"][k]["text"]
                            multy_ = js_["multipliers"][k]
                            price_ = js_["items"][k]["price"]

                            if item_ not in items_.keys():
                                items_[item_] = 0
                            items_[item_] += multy_
                            balance_ += multy_ * price_

            await callback.message.answer(txt.LPSB.CMD.STATISTICS.format(
                store=id_,
                balance=balance_,
                items='   '+'\n   '.join([f"{f.de_anchor(item_key)}: {item_value}" for item_key, item_value in items_.items()])
            ))
            tracker.log(
                command=("MENU", F.BLUE + S.BRIGHT),
                status=("STATISTICS", F.YELLOW + S.DIM),
                from_user=f.collect_FU(callback)
            )
        except:
            await callback.message.answer(txt.LPSB.ITEMS.SOMETHING_WENT_WRONG)
            tracker.log(
                command=("MENU", F.BLUE + S.BRIGHT),
                status=("STATISTICS_FAIL", F.RED + S.DIM),
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
                callback_data="none")
            )
            js.pop("call")
            data.append(js)
            c += 1
        keyboard.adjust(1)
    return keyboard, data, c


@rtr.callback_query(mF.data == "none")
async def drop_callback(callback: CallbackQuery):
    await callback.answer()


@rtr.callback_query(MenuFSM.MENU, mF.data == "preview_cb")
async def preview(callback: CallbackQuery, state: FSMContext):
    try:
        f.update_config(config, [txt, cfg])
        await callback.message.edit_text("Главное меню\n> 'Предпросмотр 📲'")
        await callback.answer()
        try:
            id_ = db.search("shopkeepers", "userID", callback.from_user.id)["storeID"]
            store = db.search("stores", "ID", id_)
            if store["logo"]:
                logo = db.search("logotypes", "storeID", id_)
                if logo is None or logo["fileID_lpsb"] is None:
                    fileid = (await callback.message.answer_photo(FSInputFile(cfg.PATHS.STORES_LOGOS + f"{id_}.jpg"),
                                                                  caption=txt.MAIN.STORE.ID_OK.format(
                                                                      name=store["name"],
                                                                      description=store["description"]
                                                                  ))).photo[-1].file_id
                    try:
                        db.update("logotypes", "storeID", id_, "fileID_lpsb", fileid)
                    except lpsql.errors.EntryNotFound:
                        db.insert("logotypes",
                                  [
                                         id_,       # storeID
                                         None,      # fileID_main
                                         fileid     # fileID_lpsb
                                     ])
                else:
                    await callback.message.answer_photo(logo["fileID_lpsb"],
                                                        caption=txt.MAIN.STORE.ID_OK.format(
                                                            name=store["name"],
                                                            description=store["description"]
                                                        ))
            else:
                await callback.message.answer(txt.MAIN.STORE.ID_OK.format(
                    name=store["name"],
                    description=store["description"]
                ))

            keyboard, real_items, count = await proceed_store_keyboard(id_)
            await callback.message.answer(
                txt.MAIN.STORE.ITEMS.format(
                    items_empty='' if count > 0 else 'в данный момент здесь ничего нет',
                    flag='' if len(db.search("changing", "storeID", id_, True)) == 0 else txt.MAIN.STORE.WARNING_ON_CHANGE
                ),
                reply_markup=keyboard.as_markup()
            )

            tracker.log(
                command=("MENU", F.BLUE + S.BRIGHT),
                status=("PREVIEW", F.YELLOW + S.DIM),
                from_user=f.collect_FU(callback)
            )
        except:
            await callback.message.answer(txt.LPSB.ITEMS.SOMETHING_WENT_WRONG)
            tracker.log(
                command=("MENU", F.BLUE + S.BRIGHT),
                status=("PREVIEW_FAIL", F.RED + S.DIM),
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


@rtr.callback_query(MenuFSM.MENU, mF.data == "info_cb")
async def info(callback: CallbackQuery, state: FSMContext):
    try:
        f.update_config(config, [txt, cfg])
        await callback.message.edit_text("Главное меню\n> 'Информация ℹ️'")
        await callback.answer()
        store = db.search("stores", "ID", db.search("shopkeepers", "userID", callback.from_user.id)["storeID"])
        await callback.message.answer_photo(cfg.MEDIA.LPSB_MAP)
        await callback.message.answer_document(
            cfg.MEDIA.MANUAL.LPSB,
            caption=txt.LPSB.CMD.MENU_INFO_TABLET.format(
                store_id=store["ID"],
                place_id=store["placeID"],
                auc_id=store["auctionID"] if store["auctionID"] else "ещё не определено",
                host=store["hostEmail"],
            )
        )
        tracker.log(
            command=("MENU", F.BLUE + S.BRIGHT),
            status=("INFO", F.YELLOW + S.DIM),
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
