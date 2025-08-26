from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery, InputMediaVideo, InputMediaPhoto
from aiogram.fsm.context import FSMContext
from aiogram import F as mF

from colorama import Fore as F, Style as S
from random import randint

from scripts import f, tracker, exelink, lpsql, firewall3
from scripts.j2 import fromfile_async as j_fromfile_async, fromfile as j_fromfile
from data import config as cfg, txt

from source.LPSB._states import *
import source.LPSB._keyboards as main_keyboard


rtr = Router()
config = [j_fromfile(cfg.PATHS.LAUNCH_SETTINGS)["config_v"]]
firewall3 = firewall3.FireWall("LPSB")
db = lpsql.DataBase("lypay_database.db", lpsql.Tables.MAIN)
print("LPSB/ad router")


@rtr.message(Command("ad"))
async def ad(message: Message, state: FSMContext):
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
                store_id = db.search("shopkeepers", "userID", message.from_user.id)["storeID"]
                if not (await j_fromfile_async(cfg.PATHS.LAUNCH_SETTINGS))["lpsb_can_send_ad"]:
                    await message.answer(txt.LPSB.AD.FORBIDDEN_BY_SETTINGS)
                    tracker.log(
                        command=("AD", F.MAGENTA + S.BRIGHT),
                        status=("FORBIDDEN_BY_SETTINGS", F.RED + S.DIM),
                        from_user=f.collect_FU(message)
                    )
                elif store_id in (await f.read_sublist("ads")).keys():
                    await message.answer(txt.LPSB.AD.ALREADY_APPROVED)
                    tracker.log(
                        command=("AD", F.MAGENTA + S.BRIGHT),
                        status=("ALREADY_APPROVED", F.YELLOW + S.DIM),
                        from_user=f.collect_FU(message)
                    )
                else:
                    m_id = (await message.answer(txt.LPSB.AD.START, reply_markup=main_keyboard.adCMD["phase1"])).message_id
                    exelink.sublist(
                        name='ccc/lpsb',
                        key=message.chat.id,
                        data=m_id,
                        userID=message.from_user.id
                    )
                    await state.set_state(AdFSM.WAITING)
                    await state.update_data(AD_TEXT=None)
                    await state.update_data(AD_PHOTO=list())
                    await state.update_data(AD_VIDEO=None)
                    tracker.log(
                        command=("AD", F.MAGENTA + S.BRIGHT),
                        from_user=f.collect_FU(message)
                    )
            elif current not in RegistrationFSM.__states__:
                await message.delete()
            else:
                await message.answer(txt.LPSB.REGISTRATION.FORCE_REGISTRATION)
                tracker.log(
                    command=("MENU", F.BLUE + S.BRIGHT),
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
                                             randint(0, len(cfg.MEDIA.NOT_IN_LPSB_WHITELIST_FROGS)-1)
                                         ])
    except Exception as e:
        tracker.error(
            e=e,
            userID=message.from_user.id
        )


@rtr.message(AdFSM.WAITING, mF.text)
async def proceed_text(message: Message, state: FSMContext):
    try:
        f.update_config(config, [txt, cfg, main_keyboard])
        censor = tracker.censor(
            from_user=f.collect_FU(message),
            text=message.text,
            text_length_flag=False
        )
        if not censor:
            await message.answer(txt.MAIN.CMD.CENSOR_BLACK)
            return
        if len(message.text) <= 250:
            await message.answer(txt.LPSB.AD.TEXT_APPROVED)
            if (await state.get_data())["AD_TEXT"] is not None:
                await message.answer(txt.LPSB.AD.TEXT_REWRITE_WARNING)
            await state.update_data(AD_TEXT=message.text)
        else:
            await message.answer(txt.LPSB.AD.TEXT_LENGTH_LIMIT.format(text_length=len(message.text)))
        tracker.log(
            command=("AD", F.MAGENTA + S.BRIGHT),
            status=("TEXT_PROCEED", F.YELLOW + S.DIM),
            from_user=f.collect_FU(message)
        )
    except Exception as e:
        tracker.error(
            e=e,
            userID=message.from_user.id
        )


@rtr.message(AdFSM.WAITING, mF.media_group_id)
async def skip_media_group(message: Message):
    try:
        f.update_config(config, [txt, cfg, main_keyboard])
        await message.answer(txt.LPSB.AD.CANT_HANDLE_MEDIA_GROUP)
        tracker.log(
            command=("AD", F.MAGENTA + S.BRIGHT),
            status=("MEDIA_GROUP", F.RED + S.DIM),
            from_user=f.collect_FU(message)
        )
    except Exception as e:
        tracker.error(
            e=e,
            userID=message.from_user.id
        )


@rtr.message(AdFSM.WAITING, mF.photo)
async def proceed_photo(message: Message, state: FSMContext):
    try:
        f.update_config(config, [txt, cfg, main_keyboard])
        photos = (await state.get_data())["AD_PHOTO"]
        if len(photos) < 4:
            await message.answer(txt.LPSB.AD.PHOTO_APPROVED.format(num=len(photos) + 1))
            await state.update_data(AD_PHOTO=photos + [message.photo[-1].file_id])
            tracker.log(
                command=("AD", F.MAGENTA + S.BRIGHT),
                status=("PHOTO_PROCEED", F.YELLOW + S.DIM),
                from_user=f.collect_FU(message)
            )
        else:
            await message.answer(txt.LPSB.AD.TOO_MANY)
            tracker.log(
                command=("AD", F.MAGENTA + S.BRIGHT),
                status=("PHOTO_PROCEED_FAIL", F.RED + S.DIM),
                from_user=f.collect_FU(message)
            )
    except Exception as e:
        tracker.error(
            e=e,
            userID=message.from_user.id
        )


@rtr.message(AdFSM.WAITING, mF.video)
async def proceed_video(message: Message, state: FSMContext):
    try:
        f.update_config(config, [txt, cfg, main_keyboard])
        if (await state.get_data())["AD_VIDEO"] is None:
            if message.video.duration > 60:
                await message.answer(txt.LPSB.AD.VIDEO_LENGTH_LIMIT)
                tracker.log(
                    command=("AD", F.MAGENTA + S.BRIGHT),
                    status=("VIDEO_PROCEED_FAIL", F.RED + S.DIM),
                    from_user=f.collect_FU(message)
                )
            else:
                await message.answer(txt.LPSB.AD.VIDEO_APPROVED)
                await state.update_data(AD_VIDEO=message.video.file_id)
                tracker.log(
                    command=("AD", F.MAGENTA + S.BRIGHT),
                    status=("VIDEO_PROCEED", F.YELLOW + S.DIM),
                    from_user=f.collect_FU(message)
                )
        else:
            await message.answer(txt.LPSB.AD.TOO_MANY)
            tracker.log(
                command=("AD", F.MAGENTA + S.BRIGHT),
                status=("VIDEO_PROCEED_FAIL", F.RED + S.DIM),
                from_user=f.collect_FU(message)
            )
    except Exception as e:
        tracker.error(
            e=e,
            userID=message.from_user.id
        )


@rtr.callback_query(AdFSM.WAITING, mF.data == "ad_continue_cb")
async def to_preview(callback: CallbackQuery, state: FSMContext):
    try:
        f.update_config(config, [txt, cfg, main_keyboard])
        data = await state.get_data()
        try:
            text = data["AD_TEXT"]
        except KeyError:
            text = None
        try:
            video = data["AD_VIDEO"]
        except KeyError:
            video = None
        try:
            photo = data["AD_PHOTO"]
        except KeyError:
            photo = list()
        await callback.answer()

        if text is None and video is None and len(photo) == 0:
            await callback.message.answer(txt.LPSB.AD.NULL_DATA)
            tracker.log(
                command=("AD", F.MAGENTA + S.BRIGHT),
                status=("CONTINUE_NO_TEXT", F.RED + S.DIM),
                from_user=f.collect_FU(callback)
            )
        else:
            text = txt.LPSB.AD.AD_PREFIX + (text if text is not None else '')
            await callback.message.edit_text(callback.message.text + "\n> 'Просмотр 👁'")
            exelink.sublist(
                mode='remove',
                name='ccc/lpsb',
                key=callback.message.chat.id,
                userID=callback.from_user.id
            )
            await state.set_state(AdFSM.CONFIRM)
            m_id = (await callback.message.answer(txt.LPSB.AD.PREVIEW_AND_CHECK, reply_markup=main_keyboard.adCMD["phase2"])).message_id
            exelink.sublist(
                name='ccc/lpsb',
                key=callback.message.chat.id,
                data=m_id,
                userID=callback.from_user.id
            )
            media_group = []
            if video is not None:
                media_group.append(InputMediaVideo(media=video))
            media_group += [InputMediaPhoto(media=ph) for ph in photo]

            if len(media_group) > 0:
                media_group[0].caption = text
                await callback.message.answer_media_group(media_group)
                final_ids = (["video:" + video] if video is not None else []) + ["photo:" + ph for ph in photo]
                final_ids[0] += f":{text}"
                await state.update_data(AD_CACHED='\u00a0'.join(final_ids))
            else:
                await callback.message.answer(text)
                await state.update_data(AD_CACHED=f"::{text}")
            store_id = db.search("shopkeepers", "userID", callback.from_user.id)["storeID"]
            await state.update_data(AD_TECH_DATA=txt.LPSB.AD.TECH_DATA.format(
                tag=('@'+callback.from_user.username) if callback.from_user.username is not None else '–',
                user_id=callback.from_user.id,
                store_id=store_id,
                host=db.search("stores", "ID", store_id)["hostEmail"],
                chat_id=callback.message.chat.id,
                message_id=callback.message.message_id
            ))

            tracker.log(
                command=("AD", F.MAGENTA + S.BRIGHT),
                status=("CONTINUE", F.BLUE + S.DIM),
                from_user=f.collect_FU(callback)
            )
    except Exception as e:
        tracker.error(
            e=e,
            userID=callback.from_user.id
        )


@rtr.callback_query(mF.data == "ad_cancel_cb")
async def cancel_this(callback: CallbackQuery, state: FSMContext):
    try:
        f.update_config(config, [txt, cfg, main_keyboard])
        await callback.answer()
        tracker.log(
            command=("CANCELLED", F.RED + S.BRIGHT),
            from_user=f.collect_FU(callback)
        )
        c = 0
        for key, value in (await f.read_sublist('ccc/lpsb')).items():
            if key == str(callback.message.chat.id):
                c += 1
                exelink.ccc_remove_keyboard(
                    bot='lpsb',
                    chat_id=key,
                    message_id=value,
                    text="[CCC] Действие отменено.",
                    userID=callback.from_user.id
                )
                exelink.sublist(
                    mode='remove',
                    name='ccc/lpsb',
                    key=key,
                    data=value,
                    userID=callback.from_user.id
                )
        if c == 0:
            await callback.message.answer(txt.LPSB.CMD.CANCELLED)
        await state.clear()

        try:
            storeID = db.search("shopkeepers", "userID", callback.from_user.id)
            if storeID is None:
                return
            storeID = storeID["storeID"]
            while True:
                db.delete("changing", callback.from_user.id, storeID)
        except lpsql.errors.EntryNotFound:
            pass
    except Exception as e:
        tracker.error(
            e=e,
            userID=callback.from_user.id
        )


@rtr.callback_query(mF.data == "ad_send_to_moderators_cb")
async def send_ad(callback: CallbackQuery, state: FSMContext):
    try:
        f.update_config(config, [txt, cfg, main_keyboard])
        data = await state.get_data()
        await callback.message.edit_text(callback.message.text + "\n> 'Отправить на модерацию ✨'")
        exelink.sublist(
            mode='remove',
            name='ccc/lpsb',
            key=callback.message.chat.id,
            userID=callback.from_user.id
        )
        unpacked_data = list()
        for line in data["AD_CACHED"].split(''):
            unpacked_data.append(line.split(':', 2))
        await f.parse_media_cache_ad_packet(
            bot=callback.bot,
            tech_message=data["AD_TECH_DATA"],
            sender_id=callback.from_user.id,
            to=cfg.AD_GROUP,
            data=unpacked_data
        )
        # формат пакета - scripts/f.py
        ''' до v2.2:
        exelink.message(
            text=data["AD_TECH_DATA"] + f"\u00a0{callback.from_user.id}",
            file_path=data["AD_CACHED"],
            file_mode='media_cache_ad',
            bot='LPSB',
            participantID=cfg.AD_GROUP,
            userID=callback.from_user.id
        )
        '''
        await callback.message.answer(txt.LPSB.AD.OK)
        await callback.answer()
        await state.clear()
        tracker.log(
            command=("AD", F.MAGENTA + S.BRIGHT),
            status=("SENT", F.BLUE),
            from_user=f.collect_FU(callback)
        )
    except Exception as e:
        tracker.error(
            e=e,
            userID=callback.from_user.id
        )
