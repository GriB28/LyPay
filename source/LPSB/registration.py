from aiogram import Router
from aiogram.types import Message, CallbackQuery, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.fsm.context import FSMContext
from aiogram import F as mF

from colorama import Fore as F, Style as S
from random import randint

from scripts import f, tracker, firewall3, exelink, lpsql
from scripts.j2 import fromfile as j_fromfile
from data import config as cfg, txt

from source.LPSB._states import *
import source.LPSB._keyboards as main_keyboard


rtr = Router()
config = [j_fromfile(cfg.PATHS.LAUNCH_SETTINGS)["config_v"]]
firewall3 = firewall3.FireWall("LPSB")
db = lpsql.DataBase("lypay_database.db", lpsql.Tables.MAIN)
print("LPSB/registration router")


@rtr.message(mF.text, RegistrationFSM.CHECK_CODE)
async def check_code(message: Message, state: FSMContext):
    try:
        f.update_config(config, [txt, cfg, main_keyboard])
        base = await f.read_sublist('store_form_link')
        if message.text not in base.keys():
            rng = randint(0, 49)
            for key, value in cfg.MEDIA.BAD_LPSB_REGISTRATION_CODE.items():
                if rng in value:
                    await message.answer_sticker(key)
                    break
            tracker.log(
                command=("REGISTRATION", F.YELLOW + S.BRIGHT),
                status=("INCORRECT_CODE", F.RED + S.DIM),
                from_user=f.collect_FU(message)
            )
            exelink.warn(
                text=txt.EXE.EVENTS.NEW_WRONG_LPSB_ACCESS_CODE.format(
                    rng=rng,
                    id=message.from_user.id,
                    tag=f"{'@' if message.from_user.username else ''}{message.from_user.username}"
                ),
                userID=message.from_user.id
            )
        else:
            email = base[message.text]
            await message.answer(txt.LPSB.REGISTRATION.TABLET.format(email=email))
            await message.answer(txt.LPSB.REGISTRATION.NAME)
            await state.set_state(RegistrationFSM.NAME)
            await state.update_data(EMAIL=email)
            await state.update_data(CODE=message.text)
            tracker.log(
                command=("REGISTRATION", F.YELLOW + S.BRIGHT),
                status=("CODE_CONFIRMED", F.GREEN + S.DIM),
                from_user=f.collect_FU(message)
            )
    except Exception as e:
        tracker.error(
            e=e,
            userID=message.from_user.id
        )


@rtr.message(mF.text, RegistrationFSM.NAME)
async def save_name(message: Message, state: FSMContext):
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
                    command=("REGISTRATION", F.YELLOW + S.BRIGHT),
                    status=("NAME_TOO_LONG", F.RED + S.DIM),
                    from_user=f.collect_FU(message)
                )
            else:
                await state.update_data(NAME=message.text)
                await message.answer(txt.LPSB.REGISTRATION.DESCRIPTION)
                await state.set_state(RegistrationFSM.DESCRIPTION)
                tracker.log(
                    command=("REGISTRATION", F.YELLOW + S.BRIGHT),
                    status=("NAME_OK", F.YELLOW + S.DIM),
                    from_user=f.collect_FU(message)
                )
        else:
            await message.answer(txt.LPSB.REGISTRATION.BAD_FORMAT)
            tracker.log(
                command=("REGISTRATION", F.YELLOW + S.BRIGHT),
                status=("NAME_BAD", F.RED + S.DIM),
                from_user=f.collect_FU(message)
            )
    except Exception as e:
        tracker.error(
            e=e,
            userID=message.from_user.id
        )


@rtr.message(mF.text, RegistrationFSM.DESCRIPTION)
async def save_description(message: Message, state: FSMContext):
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
                command=("REGISTRATION", F.YELLOW + S.BRIGHT),
                status=("DESCRIPTION_TOO_LONG", F.RED + S.DIM),
                from_user=f.collect_FU(message)
            )
        else:
            await state.update_data(DESCRIPTION=message.text)
            m_id = (await message.answer(txt.LPSB.REGISTRATION.LOGO.SENT, reply_markup=main_keyboard.skipLogoCMD)).message_id
            exelink.sublist(
                mode='add',
                name='ccc/lpsb',
                key=message.chat.id,
                data=m_id,
                userID=message.from_user.id
            )
            await state.set_state(RegistrationFSM.LOGO)
            tracker.log(
                command=("REGISTRATION", F.YELLOW + S.BRIGHT),
                status=("DESCRIPTION_OK", F.YELLOW + S.DIM),
                from_user=f.collect_FU(message)
            )
    except Exception as e:
        tracker.error(
            e=e,
            userID=message.from_user.id
        )


@rtr.message(mF.photo, RegistrationFSM.LOGO)
async def save_logo(message: Message, state: FSMContext):
    try:
        f.update_config(config, [txt, cfg, main_keyboard])
        await state.update_data(LOGO=message.photo[-1].file_id)
        await message.answer(txt.LPSB.REGISTRATION.LOGO.OK)
        await state.set_state(RegistrationFSM.END)
        tracker.log(
            command=("REGISTRATION", F.YELLOW + S.BRIGHT),
            status=("LOGO_OK", F.YELLOW + S.DIM),
            from_user=f.collect_FU(message)
        )
        await get_id(message, state)
    except Exception as e:
        tracker.error(
            e=e,
            userID=message.from_user.id
        )


@rtr.message(~mF.photo, RegistrationFSM.LOGO)
async def wrong_logo(message: Message):
    try:
        f.update_config(config, [txt, cfg, main_keyboard])
        await message.answer(txt.LPSB.REGISTRATION.LOGO.FORMAT)
        tracker.log(
            command=("REGISTRATION", F.YELLOW + S.BRIGHT),
            status=("LOGO_BAD", F.RED + S.DIM),
            from_user=f.collect_FU(message)
        )
    except Exception as e:
        tracker.error(
            e=e,
            userID=message.from_user.id
        )


@rtr.callback_query(mF.data == "skip_cb", RegistrationFSM.LOGO)
async def skip_logo(callback: CallbackQuery, state: FSMContext):
    try:
        f.update_config(config, [txt, cfg, main_keyboard])
        await callback.answer()
        await state.update_data(LOGO=None)
        await callback.message.answer(txt.LPSB.REGISTRATION.LOGO.SKIP)
        await state.set_state(RegistrationFSM.END)
        tracker.log(
            command=("REGISTRATION", F.YELLOW + S.BRIGHT),
            status=("LOGO_SKIP", F.YELLOW + S.DIM),
            from_user=f.collect_FU(callback)
        )

        await get_id(callback.message, state)
    except Exception as e:
        tracker.error(
            e=e,
            userID=callback.from_user.id
        )


async def get_id(message: Message, state: FSMContext):
    letters = list('abcdef0123456789')
    builder = InlineKeyboardBuilder()
    ids = set()
    for __ in range(10):
        id_ = letters[randint(0, 15)] + letters[randint(0, 15)] + letters[randint(0, 15)]
        while id_ in ids or id_ in db.searchall("stores", "ID"):
            id_ = letters[randint(0, 15)] + letters[randint(0, 15)] + letters[randint(0, 15)]
        ids.add(id_)

        builder.add(InlineKeyboardButton(text=id_, callback_data=id_ + "_cb_id"))
    builder.adjust(5)

    await state.update_data(END=ids)
    m_id = (await message.answer(txt.LPSB.REGISTRATION.ID, reply_markup=builder.as_markup())).message_id
    exelink.sublist(
        mode='add',
        name='ccc/lpsb',
        key=message.chat.id,
        data=m_id,
        userID=message.from_user.id
    )
    await state.set_state(RegistrationFSM.END)


@rtr.callback_query(mF.data.find('_cb_id') != -1, RegistrationFSM.END)
async def end_reg(callback: CallbackQuery, state: FSMContext):
    try:
        f.update_config(config, [txt, cfg, main_keyboard])
        data = await state.get_data()
        chosen = callback.data.replace('_cb_id', '')

        db.insert(
            "stores",
            [
                chosen,                         # ID
                data["NAME"].strip(),           # name
                callback.from_user.id,          # hostID
                data["DESCRIPTION"].strip(),    # description
                bool(data["LOGO"]),             # logo
                0,                              # balance
                data["EMAIL"],                  # hostEmail
                None,                           # auctionID
                None,                           # placeID
            ]
        )
        db.insert(
            "shopkeepers",
            [
                callback.from_user.id,  # userID
                chosen                  # storeID
            ]
        )
        db.insert(
            "logotypes",
            [
                chosen,     # storeID
                None,       # fileID_main
                None        # fileID_lpsb
            ]
        )
        exelink.sublist(
            mode='remove',
            name='store_form_link',
            key=data["CODE"],
            userID=callback.from_user.id
        )
        firewall3.add_white(callback.from_user.id, "added via automatic register code")

        if data["LOGO"]:  # data["LOGO"] - fileID_lpsb
            exelink.photo(
                bot="LPSB",
                fileID=data["LOGO"],
                path=cfg.PATHS.STORES_LOGOS + f"{chosen}.jpg",
                userID=callback.from_user.id
            )
            db.update("logotypes", "storeID", chosen, "fileID_lpsb", data["LOGO"])

        await callback.message.edit_text(txt.LPSB.REGISTRATION.END.format(id=chosen))
        await callback.answer()
        exelink.sublist(
            mode='remove',
            name='ccc/lpsb',
            key=callback.message.chat.id,
            userID=callback.from_user.id
        )
        exelink.warn(
            text=txt.EXE.EVENTS.NEW_LPSB_REGISTRATION.format(
                id=chosen,
                host=data["EMAIL"],
                host_id=callback.from_user.id
            ),
            userID=callback.from_user.id
        )
        tracker.log(
            command=("REGISTRATION", F.YELLOW + S.BRIGHT),
            status=("ID_PROCEED", F.GREEN + S.DIM),
            from_user=f.collect_FU(callback)
        )
        await state.clear()
    except Exception as e:
        tracker.error(
            e=e,
            userID=callback.from_user.id
        )
