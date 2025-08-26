from aiogram import Router
from aiogram.types import Message
from aiogram.filters.command import Command
from aiogram.fsm.context import FSMContext

from colorama import Fore as F, Style as S
from random import randint

from scripts import f, tracker, firewall3, lpsql, exelink
from scripts.j2 import fromfile as j_fromfile
from data import config as cfg, txt

from source.LPSB._states import *
import source.LPSB._keyboards as main_keyboard
from source.LPSB.submenu.items import rtr as items_r
from source.LPSB.submenu.settings import rtr as settings_r
from source.LPSB.submenu.abstract import rtr as abstract_r


rtr = Router()
rtr.include_routers(
    items_r,
    settings_r,
    abstract_r
)
config = [j_fromfile(cfg.PATHS.LAUNCH_SETTINGS)["config_v"]]
firewall3 = firewall3.FireWall("LPSB")
db = lpsql.DataBase("lypay_database.db", lpsql.Tables.MAIN)
print("LPSB/menu router")


@rtr.message(Command("menu"))
async def menu(message: Message, state: FSMContext):
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
                await state.set_state(MenuFSM.MENU)
                tracker.log(
                    command=("MENU", F.BLUE + S.BRIGHT),
                    from_user=f.collect_FU(message)
                )
                storeID = db.search("shopkeepers", "userID", message.from_user.id)["storeID"]
                m_id = (await message.answer(
                    txt.LPSB.CMD.MENU_TABLET.format(
                        id=storeID,
                        balance=db.balance_view(storeID)
                    ),
                    reply_markup=main_keyboard.menuCMD["main"]
                )).message_id
                exelink.sublist(
                    mode='add',
                    name='ccc/lpsb',
                    key=message.chat.id,
                    data=m_id,
                    userID=message.from_user.id
                )
            elif current == MenuFSM.MENU:
                await message.delete()
            elif current in MenuFSM.__states__:
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
                    storeID = db.search("shopkeepers", "userID", message.from_user.id)
                    if storeID is None:
                        return
                    storeID = storeID["storeID"]
                    while True:
                        db.delete("changing", message.from_user.id, storeID)
                except lpsql.errors.EntryNotFound:
                    pass

                tracker.log(
                    command=("MENU_CANCELLED", F.BLUE + S.DIM),
                    from_user=f.collect_FU(message)
                )
                await menu(message, state)
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
            print(F.LIGHTBLACK_EX + S.DIM + str(message.from_user.id))
    except Exception as e:
        tracker.error(
            e=e,
            userID=message.from_user.id
        )
