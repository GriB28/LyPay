from aiogram import Router
from aiogram.types import Message
from aiogram.filters.command import Command
from aiogram.fsm.context import FSMContext

from colorama import Fore as F, Style as S
from random import randint

from scripts import f, j2, tracker, firewall3, lpsql, exelink
from data import config as cfg, txt

from source.LPSB._states import *


rtr = Router()
config = [j2.fromfile(cfg.PATHS.LAUNCH_SETTINGS)["config_v"]]
firewall3 = firewall3.FireWall("LPSB", silent=False)
print("LPSB/abstract router")


@rtr.message(Command("start"))
async def start(message: Message, state: FSMContext):
    try:
        f.update_config(config, [txt, cfg])
        await message.answer(txt.LPSB.CMD.START)
        if message.from_user.id not in lpsql.searchall("shopkeepers", "userID"):
            if (await j2.fromfile_async(cfg.PATHS.LAUNCH_SETTINGS))["lpsb_can_register"]:
                await message.answer(txt.LPSB.REGISTRATION.CHECK_CODE)
                await state.set_state(RegistrationFSM.CHECK_CODE)
            else:
                await message.answer(txt.LPSB.REGISTRATION.FORBIDDEN_BY_SETTINGS)
        else:
            await message.answer(txt.LPSB.REGISTRATION.REGISTERED)
        tracker.log(
            command=("START", F.GREEN + S.BRIGHT),
            from_user=f.collect_FU(message)
        )
    except Exception as e:
        tracker.error(
            e=e,
            userID=message.from_user.id
        )


@rtr.message(Command("cancel"))
async def cancel(message: Message, state: FSMContext):
    try:
        f.update_config(config, [txt, cfg])
        firewall_status = firewall3.check(message.from_user.id)
        if firewall_status == firewall3.WHITE_ANCHOR:
            now = await state.get_state()
            if now in RegistrationFSM.__states__:
                await message.answer(txt.LPSB.REGISTRATION.FORCE_REGISTRATION)
                tracker.log(
                    command=("CANCEL", F.RED + S.NORMAL),
                    status=("FORCE_REGISTRATION", F.MAGENTA + S.BRIGHT),
                    from_user=f.collect_FU(message)
                )
            else:
                tracker.log(
                    command=("CANCELLED", F.RED + S.BRIGHT),
                    from_user=f.collect_FU(message)
                )
                c = 0
                for key, value in (await f.read_sublist('ccc/lpsb')).items():
                    if key == str(message.chat.id):
                        c += 1
                        exelink.ccc_remove_keyboard(
                            bot='lpsb',
                            chat_id=key,
                            message_id=value,
                            text="[CCC] Действие отменено.",
                            userID=message.from_user.id
                        )
                        exelink.sublist(
                            mode='remove',
                            name='ccc/lpsb',
                            key=key,
                            data=value,
                            userID=message.from_user.id
                        )
                if c == 0:
                    await message.answer(txt.LPSB.CMD.CANCELLED)
                await state.clear()

                try:
                    storeID = lpsql.search("shopkeepers", "userID", message.from_user.id)
                    if storeID is None:
                        return
                    storeID = storeID["storeID"]
                    while True:
                        lpsql.delete("changing", message.from_user.id, storeID)
                except lpsql.errors.EntryNotFound:
                    pass
        elif firewall_status == firewall3.BLACK_ANCHOR:
            tracker.black(f.collect_FU(message))
            await message.answer(txt.LPSB.CMD.IN_BLACKLIST)
        else:
            tracker.gray(f.collect_FU(message))
            await message.answer(txt.LPSB.CMD.NOT_IN_WHITELIST)
            await message.answer_sticker(cfg.MEDIA.NOT_IN_LPSB_WHITELIST_FROGS[
                                             randint(0, len(cfg.MEDIA.NOT_IN_LPSB_WHITELIST_FROGS)-1)
                                         ])
            # print(F.LIGHTBLACK_EX + S.DIM + str(message.from_user.id))
    except Exception as e:
        tracker.error(
            e=e,
            userID=message.from_user.id
        )
