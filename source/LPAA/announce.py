from aiogram import Router
from aiogram import F as mF
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from asyncio import sleep
from colorama import Fore as F, Style as S

from scripts import f, firewall3, tracker, exelink, lpsql
from scripts.j2 import fromfile as j_fromfile
from scripts.unix import unix
from data import txt, config as cfg

from source.LPAA._states import *


rtr = Router()
config = [j_fromfile(cfg.PATHS.LAUNCH_SETTINGS)["config_v"]]
firewall3, firewall3_LPSB = firewall3.FireWall("LPAA"), firewall3.FireWall("LPSB")
db = lpsql.DataBase("lypay_database.db", lpsql.Tables.MAIN)
print("LPAA/announce router")


@rtr.message(mF.text[:10] == "/announce_", mF.chat.id == cfg.HIGH_GROUP)
async def announce(message: Message, state: FSMContext):
    try:
        f.update_config(config, [txt, cfg])
        firewall_status = firewall3.check(message.from_user.id)
        if firewall_status == firewall3.WHITE_ANCHOR:
            tracker.log(
                command=("ANNOUNCE", F.CYAN + S.BRIGHT),
                status=("PREPARING", F.LIGHTBLUE_EX + S.NORMAL),
                from_user=f.collect_FU(message)
            )
            await state.set_state(AnnounceFSM.PREPARING)
            await state.update_data(BOT=message.text[10:14])
            await message.answer(txt.LPAA.ANNOUNCE.ANNOUNCE)
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


@rtr.message(AnnounceFSM.PREPARING, mF.text, mF.chat.id == cfg.HIGH_GROUP)
async def enter_text(message: Message, state: FSMContext):
    try:
        f.update_config(config, [txt, cfg])
        await state.update_data(PREPARING=message.text)
        await state.set_state(AnnounceFSM.PICKING)
        await message.answer(txt.LPAA.ANNOUNCE.PICKING_USERS)
        tracker.log(
            command=("ANNOUNCE", F.CYAN + S.BRIGHT),
            status=("ENTERING_TEXT", F.LIGHTBLUE_EX + S.NORMAL),
            from_user=f.collect_FU(message)
        )
    except Exception as e:
        tracker.error(
            e=e,
            userID=message.from_user.id
        )


@rtr.message(AnnounceFSM.PREPARING, mF.photo, mF.chat.id == cfg.HIGH_GROUP)
async def enter_photo(message: Message, state: FSMContext):
    try:
        f.update_config(config, [txt, cfg])
        exelink.photo(
            bot="LPAA",
            fileID=message.photo[-1].file_id,
            path=cfg.PATHS.IMAGES + f"{'img' + str(unix()).replace('.', '') + ".jpg"}",
            userID=message.from_user.id
        )
        await state.update_data(PREPARING_PHOTO=cfg.PATHS.IMAGES + 'img' + str(unix()).replace('.', '') + ".jpg")
        await message.answer(txt.LPAA.ANNOUNCE.ANNOUNCE_WITH_PHOTO_req_TEXT)
        tracker.log(
            command=("ANNOUNCE", F.CYAN + S.BRIGHT),
            status=("ENTERING_PHOTO", F.LIGHTBLUE_EX + S.NORMAL),
            from_user=f.collect_FU(message)
        )
    except Exception as e:
        tracker.error(
            e=e,
            userID=message.from_user.id
        )


@rtr.message(AnnounceFSM.PICKING, mF.text, mF.chat.id == cfg.HIGH_GROUP)
async def sent(message: Message, state: FSMContext):
    try:
        f.update_config(config, [txt, cfg])
        data = await state.get_data()
        announcement = data["PREPARING"]
        try:
            photo = data["PREPARING_PHOTO"]
        except KeyError:
            photo = None
        counter = 0
        if message.text.strip() == '-':
            if data["BOT"] == "main":
                for user in db.searchall("users", "ID"):
                    counter += 1
                    exelink.message(
                        text=announcement,
                        file_path=photo,
                        file_mode='photo_upload',
                        bot='MAIN',
                        participantID=user,
                        reset=True,
                        userID=message.from_user.id
                    )
            elif data["BOT"] == "lpsb":
                for user in firewall3_LPSB.list_white():
                    counter += 1
                    exelink.message(
                        text=announcement,
                        file_path=photo,
                        file_mode='photo_upload',
                        bot='LPSB',
                        participantID=int(user),
                        reset=False,
                        userID=message.from_user.id
                    )
            else:
                raise ValueError
            await message.answer(txt.LPAA.ANNOUNCE.COMPLETE.format(num=counter))
            await state.clear()
            tracker.log(
                command=("ANNOUNCE", F.CYAN + S.BRIGHT),
                status=("COMPLETE", F.LIGHTBLUE_EX + S.NORMAL),
                from_user=f.collect_FU(message)
            )
        else:
            try:
                ids = list(map(int, message.text.strip().split()))
                for id_ in ids:
                    counter += 1
                    exelink.message(
                        text=announcement,
                        file_path=photo,
                        file_mode='photo_upload',
                        bot=data["BOT"],
                        participantID=id_,
                        reset=(data["BOT"] == "main"),
                        userID=message.from_user.id
                    )
                await message.answer(txt.LPAA.ANNOUNCE.COMPLETE.format(num=counter))
                await state.clear()
                tracker.log(
                    command=("ANNOUNCE", F.CYAN + S.BRIGHT),
                    status=("COMPLETE", F.LIGHTBLUE_EX + S.NORMAL),
                    from_user=f.collect_FU(message)
                )
            except ValueError:
                await message.answer(txt.LPAA.BAD_ARG)
                tracker.log(
                    command=("ANNOUNCE", F.CYAN + S.BRIGHT),
                    status=("FAILURE", F.LIGHTRED_EX + S.NORMAL),
                    from_user=f.collect_FU(message)
                )
    except Exception as e:
        tracker.error(
            e=e,
            userID=message.from_user.id
        )
