from aiogram import Router
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram import F as mF

from aiofiles import open as a_open
from colorama import Fore as F, Style as S
from os import remove
from os.path import exists

from scripts import f, tracker, exelink, lpsql
from scripts.unix import unix
from scripts.j2 import fromfile as j_fromfile
from data import config as cfg, txt

from source.LPSB._states import *
import source.LPSB._keyboards as main_keyboard


rtr = Router()
config = [j_fromfile(cfg.PATHS.LAUNCH_SETTINGS)["config_v"]]
db = lpsql.DataBase("lypay_database.db", lpsql.Tables.MAIN)
print("LPSB/menu/settings subrouter")


@rtr.callback_query(MenuFSM.MENU, mF.data == "settings_cb")
async def settings(callback: CallbackQuery):
    try:
        f.update_config(config, [txt, cfg, main_keyboard])
        await callback.message.edit_text(
            "Главное меню\n> 'Настройки ⚙️'\nВыберите, что хотите изменить: ",
            reply_markup=main_keyboard.menuCMD["settings"]
        )
        await callback.answer()
        tracker.log(
            command=("MENU", F.BLUE + S.BRIGHT),
            status=("SETTINGS_ROUTE", F.YELLOW + S.DIM),
            from_user=f.collect_FU(callback)
        )
    except Exception as e:
        tracker.error(
            e=e,
            userID=callback.from_user.id
        )


@rtr.callback_query(mF.data == "settings_name_cb")
async def settings_name(callback: CallbackQuery, state: FSMContext):
    try:
        f.update_config(config, [txt, cfg, main_keyboard])
        await callback.message.edit_text(f"{callback.message.text}\n> 'Название'")
        await callback.answer()
        await callback.message.answer(txt.LPSB.SETTINGS.NAME)
        await state.set_state(MenuFSM.SETTINGS_NAME)
        exelink.sublist(
            mode='remove',
            name='ccc/lpsb',
            key=callback.message.chat.id,
            userID=callback.from_user.id
        )
        tracker.log(
            command=("MENU", F.BLUE + S.BRIGHT),
            status=("NAME_UPDATE_REQUEST", F.GREEN + S.NORMAL),
            from_user=f.collect_FU(callback)
        )
    except Exception as e:
        tracker.error(
            e=e,
            userID=callback.from_user.id
        )


@rtr.message(MenuFSM.SETTINGS_NAME, mF.text)
async def settings_set_name(message: Message, state: FSMContext):
    try:
        f.update_config(config, [txt, cfg, main_keyboard])
        censor = tracker.censor(
            from_user=f.collect_FU(message),
            text=message.text
        )
        if not censor:
            await message.answer(txt.MAIN.CMD.CENSOR_BLACK)
            return
        if message.text.find('\n') == -1:
            if len(message.text) > 100:
                await message.answer(txt.LPSB.SETTINGS.NAME_TOO_LONG)
                tracker.log(
                    command=("MENU", F.BLUE + S.BRIGHT),
                    status=("NAME_TOO_LONG", F.RED + S.DIM),
                    from_user=f.collect_FU(message)
                )
            else:
                try:
                    id_ = db.search("shopkeepers", "userID", message.from_user.id)["storeID"]
                    db.update("stores", "ID", id_, "name", message.text.strip())
                    store_host = db.search("stores", "ID", id_)["hostID"]
                    if message.from_user.id != store_host:
                        await message.bot.send_message(
                            text=txt.LPSB.SETTINGS.HOST_WARNING.NAME.format(id=message.from_user.id),
                            chat_id=store_host
                        )
                        ''' до v2.2:
                        exelink.message(
                            text=txt.LPSB.SETTINGS.HOST_WARNING.NAME.format(id=message.from_user.id),
                            bot='LPSB',
                            participantID=store_host,
                            userID=message.from_user.id
                        )
                        '''

                    await message.answer(txt.LPSB.SETTINGS.UPDATED)
                    tracker.log(
                        command=("MENU", F.BLUE + S.BRIGHT),
                        status=("NAME_UPDATED", F.GREEN + S.BRIGHT),
                        from_user=f.collect_FU(message)
                    )
                except:
                    await message.answer(txt.LPSB.ITEMS.SOMETHING_WENT_WRONG)
                    tracker.log(
                        command=("MENU", F.BLUE + S.BRIGHT),
                        status=("NAME_UPDATE_FAIL", F.RED + S.NORMAL),
                        from_user=f.collect_FU(message)
                    )
                await state.set_state(MenuFSM.MENU)
                m_id = (await message.answer(
                    "Главное меню\n> 'Настройки ⚙️'\nВыберите, что хотите изменить: ",
                    reply_markup=main_keyboard.menuCMD["settings"]
                )).message_id
                exelink.sublist(
                    mode='add',
                    name='ccc/lpsb',
                    key=message.chat.id,
                    data=m_id,
                    userID=message.from_user.id
                )
        else:
            await message.answer(txt.LPSB.SETTINGS.BAD_FORMAT)
            tracker.log(
                command=("MENU", F.BLUE + S.BRIGHT),
                status=("NAME_UPDATE_FAIL", F.RED + S.NORMAL),
                from_user=f.collect_FU(message)
            )
    except Exception as e:
        tracker.error(
            e=e,
            userID=message.from_user.id
        )


@rtr.callback_query(mF.data == "settings_description_cb")
async def settings_description(callback: CallbackQuery, state: FSMContext):
    try:
        f.update_config(config, [txt, cfg, main_keyboard])
        await callback.message.edit_text(f"{callback.message.text}\n> 'Описание'")
        await callback.answer()
        await callback.message.answer(txt.LPSB.SETTINGS.DESCRIPTION)
        await state.set_state(MenuFSM.SETTINGS_DESCRIPTION)
        exelink.sublist(
            mode='remove',
            name='ccc/lpsb',
            key=callback.message.chat.id,
            userID=callback.from_user.id
        )
        tracker.log(
            command=("MENU", F.BLUE + S.BRIGHT),
            status=("DESCRIPTION_UPDATE_REQUEST", F.GREEN + S.NORMAL),
            from_user=f.collect_FU(callback)
        )
    except Exception as e:
        tracker.error(
            e=e,
            userID=callback.from_user.id
        )


@rtr.message(MenuFSM.SETTINGS_DESCRIPTION, mF.text)
async def settings_set_description(message: Message, state: FSMContext):
    try:
        f.update_config(config, [txt, cfg, main_keyboard])
        censor = tracker.censor(
            from_user=f.collect_FU(message),
            text=message.text
        )
        if not censor:
            await message.answer(txt.MAIN.CMD.CENSOR_BLACK)
            return
        if len(message.text) > 900:
            await message.answer(txt.LPSB.SETTINGS.DESCRIPTION_TOO_LONG)
            tracker.log(
                command=("MENU", F.BLUE + S.BRIGHT),
                status=("DESCRIPTION_TOO_LONG", F.RED + S.DIM),
                from_user=f.collect_FU(message)
            )
        else:
            try:
                id_ = db.search("shopkeepers", "userID", message.from_user.id)["storeID"]
                db.update("stores", "ID", id_, "description", message.text.strip())
                store_host = db.search("stores", "ID", id_)["hostID"]
                if message.from_user.id != store_host:
                    await message.bot.send_message(
                        text=txt.LPSB.SETTINGS.HOST_WARNING.DESCRIPTION.format(id=message.from_user.id),
                        chat_id=store_host
                    )
                    ''' до v2.2:
                    exelink.message(
                        text=txt.LPSB.SETTINGS.HOST_WARNING.DESCRIPTION.format(id=message.from_user.id),
                        bot='LPSB',
                        participantID=store_host,
                        userID=message.from_user.id
                    )
                    '''

                await message.answer(txt.LPSB.SETTINGS.UPDATED)
                tracker.log(
                    command=("MENU", F.BLUE + S.BRIGHT),
                    status=("DESCRIPTION_UPDATED", F.GREEN + S.BRIGHT),
                    from_user=f.collect_FU(message)
                )
            except:
                await message.answer(txt.LPSB.ITEMS.SOMETHING_WENT_WRONG)
                tracker.log(
                    command=("MENU", F.BLUE + S.BRIGHT),
                    status=("DESCRIPTION_UPDATE_FAIL", F.RED + S.DIM),
                    from_user=f.collect_FU(message)
                )
            await state.set_state(MenuFSM.MENU)
            m_id = (await message.answer(
                "Главное меню\n> 'Настройки ⚙️'\nВыберите, что хотите изменить: ",
                reply_markup=main_keyboard.menuCMD["settings"]
            )).message_id
            exelink.sublist(
                mode='add',
                name='ccc/lpsb',
                key=message.chat.id,
                data=m_id,
                userID=message.from_user.id
            )
    except Exception as e:
        tracker.error(
            e=e,
            userID=message.from_user.id
        )


@rtr.callback_query(mF.data == "settings_logo_cb")
async def settings_logo(callback: CallbackQuery, state: FSMContext):
    try:
        f.update_config(config, [txt, cfg, main_keyboard])
        await callback.message.edit_text(f"{callback.message.text}\n> 'Логотип'")
        await callback.answer()
        m_id = (await callback.message.answer(txt.LPSB.SETTINGS.LOGO, reply_markup=main_keyboard.menuCMD["settings_logo"])).message_id
        exelink.sublist(
            mode='add',
            name='ccc/lpsb',
            key=callback.message.chat.id,
            data=m_id,
            userID=callback.from_user.id
        )
        await state.set_state(MenuFSM.SETTINGS_LOGO)
        tracker.log(
            command=("MENU", F.BLUE + S.BRIGHT),
            status=("LOGO_UPDATE_REQUEST", F.GREEN + S.NORMAL),
            from_user=f.collect_FU(callback)
        )
    except Exception as e:
        tracker.error(
            e=e,
            userID=callback.from_user.id
        )


@rtr.message(MenuFSM.SETTINGS_LOGO, mF.photo)
async def settings_set_logo(message: Message, state: FSMContext):
    try:
        f.update_config(config, [txt, cfg, main_keyboard])
        try:
            id_ = db.search("shopkeepers", "userID", message.from_user.id)["storeID"]
            store = db.search("stores", "ID", id_)
            if store["logo"] and exists(cfg.PATHS.STORES_LOGOS + f"{id_}.jpg"):
                async with a_open(cfg.PATHS.STORES_LOGOS + f"{id_}.jpg", 'rb') as logo:
                    async with a_open(cfg.PATHS.OLD_LOGOS + f"{id_}_{int(unix())}.jpg", 'wb') as rewrite:
                        await rewrite.write(await logo.read())
            else:
                db.update("stores", "ID", id_, "logo", 1)

            exelink.photo(
                bot='LPSB',
                fileID=message.photo[-1].file_id,
                path=cfg.PATHS.STORES_LOGOS + f"{id_}.jpg",
                userID=message.from_user.id
            )
            try:
                db.update("logotypes", "storeID", id_, "fileID_lpsb", message.photo[-1].file_id)
            except lpsql.errors.EntryNotFound:
                db.insert("logotypes",
                          [
                                 id_,                       # storeID
                                 None,                      # fileID_main
                                 message.photo[-1].file_id  # fileID_lpsb
                             ])

            store_host = db.search("stores", "ID", id_)["hostID"]
            if message.from_user.id != store_host:
                await message.bot.send_message(
                    text=txt.LPSB.SETTINGS.HOST_WARNING.LOGO.format(id=message.from_user.id),
                    chat_id=store_host
                )
                ''' до v2.2:
                exelink.message(
                    text=txt.LPSB.SETTINGS.HOST_WARNING.LOGO.format(id=message.from_user.id),
                    bot='LPSB',
                    participantID=store_host,
                    userID=message.from_user.id
                )
                '''

            await message.answer(txt.LPSB.SETTINGS.UPDATED)
            tracker.log(
                command=("MENU", F.BLUE + S.BRIGHT),
                status=("LOGO_UPDATED", F.GREEN + S.BRIGHT),
                from_user=f.collect_FU(message)
            )
        except:
            await message.answer(txt.LPSB.ITEMS.SOMETHING_WENT_WRONG)
            tracker.log(
                command=("MENU", F.BLUE + S.BRIGHT),
                status=("LOGO_UPDATE_FAIL", F.RED + S.DIM),
                from_user=f.collect_FU(message)
            )
        await state.set_state(MenuFSM.MENU)
        m_id = (await message.answer(
            "Главное меню\n> 'Настройки ⚙️'\nВыберите, что хотите изменить: ",
            reply_markup=main_keyboard.menuCMD["settings"]
        )).message_id
        exelink.sublist(
            mode='add',
            name='ccc/lpsb',
            key=message.chat.id,
            data=m_id,
            userID=message.from_user.id
        )
    except Exception as e:
        tracker.error(
            e=e,
            userID=message.from_user.id
        )


@rtr.message(MenuFSM.SETTINGS_LOGO, ~mF.photo)
async def settings_set_logo_fail(message: Message):
    try:
        f.update_config(config, [txt, cfg, main_keyboard])
        await message.answer(txt.LPSB.SETTINGS.NOT_PHOTO)
        tracker.log(
            command=("MENU", F.BLUE + S.BRIGHT),
            status=("LOGO_UPDATE_FAIL", F.RED + S.NORMAL),
            from_user=f.collect_FU(message)
        )
    except Exception as e:
        tracker.error(
            e=e,
            userID=message.from_user.id
        )


@rtr.callback_query(MenuFSM.SETTINGS_LOGO, mF.data == "settings_null_logo_cb")
async def settings_set_null_logo(callback: CallbackQuery, state: FSMContext):
    try:
        f.update_config(config, [txt, cfg, main_keyboard])
        await callback.message.edit_text(callback.message.text + '\n> Обнулить логотип 🛑')
        await callback.answer()
        try:
            id_ = db.search("shopkeepers", "userID", callback.from_user.id)["storeID"]
            store = db.search("stores", "ID", id_)
            if store["logo"] and exists(cfg.PATHS.STORES_LOGOS + f"{id_}.jpg"):
                async with a_open(cfg.PATHS.STORES_LOGOS + f"{id_}.jpg", 'rb') as logo:
                    async with a_open(cfg.PATHS.OLD_LOGOS + f"{id_}_{int(unix())}.jpg", 'wb') as rewrite:
                        await rewrite.write(await logo.read())
            remove(cfg.PATHS.STORES_LOGOS + f"{id_}.jpg")
            db.update("stores", "ID", id_, "logo", 0)
            try:
                db.update("logotypes", "storeID", id_, "fileID_main", None)
                db.update("logotypes", "storeID", id_, "fileID_lpsb", None)
            except lpsql.errors.EntryNotFound:
                db.insert("logotypes",
                          [
                                 id_,   # storeID
                                 None,  # fileID_main
                                 None   # fileID_lpsb
                             ])

            store_host = db.search("stores", "ID", id_)["hostID"]
            if callback.from_user.id != store_host:
                await callback.bot.send_message(
                    text=txt.LPSB.SETTINGS.HOST_WARNING.LOGO.format(id=callback.from_user.id),
                    chat_id=store_host
                )
                ''' до v2.2:
                exelink.message(
                    text=txt.LPSB.SETTINGS.HOST_WARNING.LOGO.format(id=callback.from_user.id),
                    bot='LPSB',
                    participantID=store_host,
                    userID=callback.from_user.id
                )
                '''

            await callback.message.answer(txt.LPSB.SETTINGS.UPDATED)
            tracker.log(
                command=("MENU", F.BLUE + S.BRIGHT),
                status=("LOGO_DELETED", F.LIGHTRED_EX + S.BRIGHT),
                from_user=f.collect_FU(callback)
            )
        except:
            await callback.message.answer(txt.LPSB.ITEMS.SOMETHING_WENT_WRONG)
            tracker.log(
                command=("MENU", F.BLUE + S.BRIGHT),
                status=("LOGO_NULL_FAIL", F.RED + S.DIM),
                from_user=f.collect_FU(callback)
            )
        await state.set_state(MenuFSM.MENU)
        m_id = (await callback.message.answer(
            "Главное меню\n> 'Настройки ⚙️'\nВыберите, что хотите изменить: ",
            reply_markup=main_keyboard.menuCMD["settings"]
        )).message_id
        exelink.sublist(
            mode='add',
            name='ccc/lpsb',
            key=callback.message.chat.id,
            data=m_id,
            userID=callback.from_user.id
        )
    except Exception as e:
        tracker.error(
            e=e,
            userID=callback.from_user.id
        )


@rtr.callback_query(mF.data == "settings_back_cb")
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
            command=("MENU_FROM_SETTINGS", F.BLUE + S.BRIGHT),
            from_user=f.collect_FU(callback)
        )
    except Exception as e:
        tracker.error(
            e=e,
            userID=callback.from_user.id
        )
