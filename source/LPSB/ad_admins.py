from aiogram import Router
from aiogram.types import Message, ReactionTypeEmoji
from aiogram.filters.command import Command
from aiogram.fsm.context import FSMContext
from aiogram import F as mF

from colorama import Fore as F, Style as S
from asyncio import sleep

from scripts import f, tracker, lpsql, exelink
from scripts.j2 import fromfile as j_fromfile
from data import config as cfg, txt

from source.LPSB._states import *


rtr = Router()
config = [j_fromfile(cfg.PATHS.LAUNCH_SETTINGS)["config_v"]]
db = lpsql.DataBase("lypay_database.db", lpsql.Tables.MAIN)
print("LPSB/ad_admins router")


@rtr.message(Command("cancel"), mF.chat.id == cfg.AD_GROUP)
async def cancel(message: Message, state: FSMContext):
    try:
        f.update_config(config, [txt, cfg])
        await message.answer(txt.LPSB.AD.ADMIN.CANCEL)
        await state.clear()
        tracker.log(
            command=("AD_ADMIN_CANCEL", F.RED + S.BRIGHT),
            from_user=f.collect_FU(message)
        )
    except Exception as e:
        tracker.error(
            e=e,
            userID=message.from_user.id
        )


# -=-=-=-

@rtr.message(Command("answer"), mF.chat.id == cfg.AD_GROUP)
async def answer(message: Message, state: FSMContext):
    try:
        f.update_config(config, [txt, cfg])
        await message.answer(txt.LPSB.AD.ADMIN.SEND.START)
        await state.set_state(AdAdminFSM.SEND_ID)
        tracker.log(
            command=("ADMIN_ANSWER", F.GREEN + S.DIM),
            status=("START", F.LIGHTBLUE_EX + S.DIM),
            from_user=f.collect_FU(message)
        )
    except Exception as e:
        tracker.error(
            e=e,
            userID=message.from_user.id
        )


@rtr.message(AdAdminFSM.SEND_ID, mF.text)
async def get_id(message: Message, state: FSMContext):
    try:
        f.update_config(config, [txt, cfg])
        try:
            id_ = int(message.text)
        except ValueError:
            await message.answer(txt.LPSB.AD.ADMIN.SEND.BAD_ARG)
            tracker.log(
                command=("ADMIN_ANSWER", F.GREEN + S.DIM),
                status=("BAD_ARG", F.RED + S.DIM),
                from_user=f.collect_FU(message)
            )
            return
        search = db.search("shopkeepers", "userID", id_)
        if search:
            await state.update_data(ID=int(message.text))
            tracker.log(
                command=("ADMIN_ANSWER", F.GREEN + S.DIM),
                status=("ID_PROCEED", F.GREEN + S.DIM),
                from_user=f.collect_FU(message)
            )
            await state.set_state(AdAdminFSM.TEXT)
            await message.answer(txt.LPSB.AD.ADMIN.SEND.GET_TEXT)
        else:
            await message.answer(txt.LPSB.AD.ADMIN.SEND.ID_NOT_FOUND)
            tracker.log(
                command=("ADMIN_ANSWER", F.GREEN + S.DIM),
                status=("ID_NOT_FOUND", F.YELLOW + S.DIM),
                from_user=f.collect_FU(message)
            )
    except Exception as e:
        tracker.error(
            e=e,
            userID=message.from_user.id
        )


@rtr.message(AdAdminFSM.TEXT, mF.text)
async def get_text(message: Message, state: FSMContext):
    try:
        f.update_config(config, [txt, cfg])
        await message.answer(txt.LPSB.AD.ADMIN.SEND.CONFIRM.format(id=(await state.get_data())["ID"]))
        await state.set_state(AdAdminFSM.SEND_CONFIRM)
        await state.update_data(TEXT=message.text)
        tracker.log(
            command=("ADMIN_ANSWER", F.GREEN + S.DIM),
            status=("WAIT_FOR_CONFIRM", F.YELLOW + S.DIM),
            from_user=f.collect_FU(message)
        )
    except Exception as e:
        tracker.error(
            e=e,
            userID=message.from_user.id
        )


@rtr.message(AdAdminFSM.SEND_CONFIRM, Command("confirm"))
async def send_confirm(message: Message, state: FSMContext):
    try:
        f.update_config(config, [txt, cfg])
        data = await state.get_data()
        await message.bot.send_message(
            text="‼️ Сообщение от модераторов рекламы!\n\n" + data["TEXT"],
            chat_id=data["ID"]
        )
        ''' до v2.2:
        exelink.message(
            bot='LPSB',
            text="‼️ Сообщение от модераторов рекламы!\n\n" + data["TEXT"],
            participantID=data["ID"],
            userID=message.from_user.id
        )
        '''
        await message.answer(txt.LPSB.AD.ADMIN.SEND.OK)
        tracker.log(
            command=("ADMIN_ANSWER", F.GREEN + S.DIM),
            status=("SENT", F.YELLOW + S.DIM),
            from_user=f.collect_FU(message)
        )
    except Exception as e:
        tracker.error(
            e=e,
            userID=message.from_user.id
        )


# -=-=-=-

@rtr.message(Command("approve"), mF.chat.id == cfg.AD_GROUP)
async def approve(message: Message, state: FSMContext):
    try:
        f.update_config(config, [txt, cfg])
        await message.answer(txt.LPSB.AD.ADMIN.APPROVE.START)
        await state.set_state(AdAdminFSM.APPROVE_ID)
        tracker.log(
            command=("ADMIN_APPROVE", F.CYAN + S.DIM),
            status=("START", F.LIGHTBLUE_EX + S.DIM),
            from_user=f.collect_FU(message)
        )
    except Exception as e:
        tracker.error(
            e=e,
            userID=message.from_user.id
        )


@rtr.message(AdAdminFSM.APPROVE_ID, mF.text)
async def get_id_to_approve(message: Message, state: FSMContext):
    try:
        f.update_config(config, [txt, cfg])
        stores = db.searchall("stores", "ID")
        store_id = message.text.lower()
        if store_id not in stores:
            await message.answer(txt.LPSB.AD.ADMIN.APPROVE.BAD_ARG)
            tracker.log(
                command=("ADMIN_APPROVE", F.CYAN + S.DIM),
                status=("BAD_ARG", F.RED + S.DIM),
                from_user=f.collect_FU(message)
            )
        elif store_id in (await f.read_sublist("ads")).keys():
            await message.answer(txt.LPSB.AD.ADMIN.APPROVE.ALREADY_APPROVED)
            tracker.log(
                command=("ADMIN_APPROVE", F.CYAN + S.DIM),
                status=("ALREADY_APPROVED", F.YELLOW + S.DIM),
                from_user=f.collect_FU(message)
            )
        else:
            store = db.search("stores", "ID", store_id)
            await state.update_data(APPROVE_ID=store_id)
            await state.set_state(AdAdminFSM.APPROVE_CONFIRM)
            await message.answer(txt.LPSB.AD.ADMIN.APPROVE.CONFIRM.format(
                id=message.text.lower(),
                name=store["name"],
                host=store["hostEmail"]
            ))
            tracker.log(
                command=("ADMIN_APPROVE", F.CYAN + S.DIM),
                status=("ID_PROCEED", F.GREEN + S.DIM),
                from_user=f.collect_FU(message)
            )
    except Exception as e:
        tracker.error(
            e=e,
            userID=message.from_user.id
        )


@rtr.message(AdAdminFSM.APPROVE_CONFIRM, Command("confirm"))
async def approve_confirm(message: Message, state: FSMContext):
    try:
        f.update_config(config, [txt, cfg])
        store_id = (await state.get_data())["APPROVE_ID"]
        shopkeepers = [user["userID"] for user in db.search("shopkeepers", "storeID", store_id, True)]
        for user in shopkeepers:
            await message.bot.send_message(
                text=txt.LPSB.AD.ADMIN.APPROVE.APPROVED_MESSAGE,
                chat_id=user
            )
            await sleep(1/30)
            ''' до v2.2:
            exelink.message(
                bot='LPSB',
                text=txt.LPSB.AD.ADMIN.APPROVE.APPROVED_MESSAGE,
                participantID=user,
                userID=message.from_user.id
            )
            '''
        exelink.sublist(
            mode="add",
            name="ads",
            key=store_id,
            data="approved",
            userID=message.from_user.id
        )
        for key, value in (await f.read_sublist("ad_approving")).items():  # key = message_id, value = user_id
            if int(value) in shopkeepers:
                await message.bot.set_message_reaction(
                    chat_id=cfg.AD_GROUP,
                    message_id=int(key),
                    reaction=[ReactionTypeEmoji(emoji="🔥")]
                )
                ''' до v2.2:
                exelink.message(
                    bot='LPSB',
                    text="🔥",
                    file_path=str(key),
                    file_mode="set_reaction",
                    participantID=cfg.AD_GROUP,
                    userID=message.from_user.id
                )'''
                exelink.sublist(
                    mode='remove',
                    name='ad_approving',
                    key=key,
                    userID=message.from_user.id
                )
        await message.answer(txt.LPSB.AD.ADMIN.APPROVE.OK)
        tracker.log(
            command=("ADMIN_APPROVE", F.GREEN + S.DIM),
            status=("SENT", F.YELLOW + S.DIM),
            from_user=f.collect_FU(message)
        )
    except Exception as e:
        tracker.error(
            e=e,
            userID=message.from_user.id
        )


@rtr.message(mF.chat.id == cfg.AD_GROUP)
async def drop_updates_at_ad_group(*args, **kwargs):
    pass
