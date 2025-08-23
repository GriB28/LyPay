from aiogram import Router
from aiogram import F as mF
from aiogram.types import Message
from aiogram.filters.command import Command
from aiogram.fsm.context import FSMContext

from asyncio import sleep
from colorama import Fore as F, Style as S

from scripts import f, firewall3, tracker, exelink
from scripts.j2 import fromfile as j_fromfile
from data import txt, config as cfg

from source.LPAA._states import *


rtr = Router()
config = [j_fromfile(cfg.PATHS.LAUNCH_SETTINGS)["config_v"]]
firewall3 = firewall3.FireWall('LPAA', silent=False)
print("LPAA/abstract router")


@rtr.message(Command("start"))
async def start(message: Message):
    try:
        f.update_config(config, [txt, cfg])
        firewall_status = firewall3.check(message.from_user.id)
        if firewall_status == firewall3.WHITE_ANCHOR:
            await message.answer(txt.LPAA.START)
            await message.answer(txt.LPAA.INFO_TABLET)
            tracker.log(
                command=("START", F.GREEN + S.BRIGHT),
                from_user=f.collect_FU(message)
            )
        elif firewall_status == firewall3.BLACK_ANCHOR:
            await message.answer(txt.LPAA.IN_BLACKLIST)
            tracker.black(f.collect_FU(message))
        else:
            await message.answer(txt.LPAA.NOT_IN_WHITELIST)
            tracker.gray(f.collect_FU(message))
            await sleep(2)
            await message.answer_animation(cfg.MEDIA.NOT_IN_LPAA_WHITELIST)
            print(F.LIGHTBLACK_EX + S.DIM + str(message.from_user.id))
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
            if await state.get_state() in InfoFSM.__states__:
                msg = (await state.get_data())["MSG"]
                for i in range(len(msg)):
                    try:
                        await msg[i].delete()
                    except:
                        pass
            c = 0
            for key, value in (await f.read_sublist('ccc/lpaa')).items():
                if key == str(message.chat.id):
                    c += 1
                    exelink.ccc_remove_keyboard(
                        bot='lpaa',
                        chat_id=key,
                        message_id=value,
                        text="[CCC] Действие отменено.",
                        userID=message.from_user.id
                    )
                    exelink.sublist(
                        mode='remove',
                        name='ccc/lpaa',
                        key=key,
                        data=value,
                        userID=message.from_user.id
                    )

            await state.clear()
            if c == 0:
                await message.answer(txt.LPAA.CANCELLED)
            tracker.log(
                command=("CANCELLED", F.RED + S.BRIGHT),
                from_user=f.collect_FU(message)
            )
        elif firewall_status == firewall3.BLACK_ANCHOR:
            await message.answer(txt.LPAA.IN_BLACKLIST)
            tracker.black(f.collect_FU(message))
        else:
            await message.answer(txt.LPAA.NOT_IN_WHITELIST)
            tracker.gray(f.collect_FU(message))
            await sleep(2)
            await message.answer_animation(cfg.MEDIA.NOT_IN_LPAA_WHITELIST)
    except Exception as e:
        tracker.error(
            e=e,
            userID=message.from_user.id
        )


@rtr.message(Command("q"), mF.chat.id.not_in((cfg.HIGH_GROUP, cfg.WARNING_GROUP)))
async def q(message: Message):
    try:
        f.update_config(config, [txt, cfg])
        await message.answer("Q!")
        tracker.log(
            command=("Q!", F.GREEN + S.BRIGHT),
            from_user=f.collect_FU(message)
        )
        print(F.LIGHTBLACK_EX + S.DIM + str(message.from_user.id))
    except Exception as e:
        tracker.error(
            e=e,
            userID=message.from_user.id
        )


@rtr.message(Command("help", "h"), mF.chat.id.not_in((cfg.HIGH_GROUP, cfg.WARNING_GROUP)))
async def agent_help(message: Message):
    try:
        f.update_config(config, [txt, cfg])
        firewall_status = firewall3.check(message.from_user.id)
        if firewall_status == firewall3.WHITE_ANCHOR:
            tracker.log(
                command=("HELP", F.MAGENTA + S.BRIGHT),
                status=("AGENT", F.LIGHTBLACK_EX),
                from_user=f.collect_FU(message)
            )
            await message.answer(txt.LPAA.AGENT_HELP)
        elif firewall_status == firewall3.BLACK_ANCHOR:
            await message.answer(txt.LPAA.IN_BLACKLIST)
            tracker.black(f.collect_FU(message))
        else:
            await message.answer(txt.LPAA.NOT_IN_WHITELIST)
            tracker.gray(f.collect_FU(message))
            await sleep(2)
            await message.answer_animation(cfg.MEDIA.NOT_IN_LPAA_WHITELIST)
            print(F.LIGHTBLACK_EX + S.DIM + str(message.from_user.id))
    except Exception as e:
        tracker.error(
            e=e,
            userID=message.from_user.id
        )


@rtr.message(Command("help", "h"), mF.chat.id == cfg.HIGH_GROUP)
async def admin_help(message: Message):
    try:
        f.update_config(config, [txt, cfg])
        await message.answer(txt.LPAA.ADMIN_HELP)
        tracker.log(
            command=("HELP", F.MAGENTA + S.BRIGHT),
            status=("ADMIN", F.LIGHTBLACK_EX),
            from_user=f.collect_FU(message)
        )
    except Exception as e:
        tracker.error(
            e=e,
            userID=message.from_user.id
        )
