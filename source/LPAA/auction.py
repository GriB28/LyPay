from aiogram import Router
from aiogram import F as mF
from aiogram.types import Message, InlineKeyboardButton, CallbackQuery
from aiogram.filters.command import Command
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import InlineKeyboardBuilder

from colorama import Fore as F, Style as S

from scripts import f, firewall3, tracker, lpsql, exelink
from scripts.j2 import fromfile as j_fromfile
from data import txt
from data.config import PATHS

from source.LPAA._states import *


rtr = Router()
config = [j_fromfile(PATHS.LAUNCH_SETTINGS)["config_v"]]
firewall3 = firewall3.FireWall('LPAA', silent=True)
print("LPAA/auction router")


@rtr.message(Command("auction"))
async def auction_sequence(message: Message, state: FSMContext):
    try:
        f.update_config(config, [txt])
        auc_num = message.text.split()[1:]
        if len(auc_num) == 0:
            lotIDs = lpsql.searchall("auction", "lotID")
            lotID = 1 if len(lotIDs) == 0 else max(lotIDs) + 1
        else:
            lotID = int(auc_num[0])
        await state.update_data(LOT=lotID)
        await message.answer(txt.LPAA.AUCTION.NAME)
        await state.set_state(AuctionFSM.NAME)
        tracker.log(
            command=("AUCTION_LOT", F.CYAN),
            status=("START", F.YELLOW),
            from_user=f.collect_FU(message)
        )
    except Exception as e:
        tracker.error(
            e=e,
            userID=message.from_user.id
        )


@rtr.message(AuctionFSM.NAME, mF.text)
async def set_name(message: Message, state: FSMContext):
    try:
        f.update_config(config, [txt])
        await state.update_data(NAME=message.text)
        await message.answer(txt.LPAA.AUCTION.PRICE)
        await state.set_state(AuctionFSM.PRICE)
        tracker.log(
            command=("AUCTION_LOT", F.CYAN),
            status=("NAME", F.YELLOW),
            from_user=f.collect_FU(message)
        )
    except Exception as e:
        tracker.error(
            e=e,
            userID=message.from_user.id
        )


@rtr.message(AuctionFSM.PRICE, mF.text)
async def set_price(message: Message, state: FSMContext):
    try:
        f.update_config(config, [txt])
        try:
            price = int(message.text)
            if price <= 0:
                raise ValueError

            await state.update_data(PRICE=price)
            await message.answer(txt.LPAA.AUCTION.AUC_ID)
            await state.set_state(AuctionFSM.AUC_ID)
            tracker.log(
                command=("AUCTION_LOT", F.CYAN),
                status=("PRICE", F.YELLOW),
                from_user=f.collect_FU(message)
            )
        except ValueError:
            await message.answer(txt.LPAA.BAD_ARG)
            tracker.log(
                command=("AUCTION_LOT", F.CYAN),
                status=("PRICE", F.RED + S.DIM),
                from_user=f.collect_FU(message)
            )
    except Exception as e:
        tracker.error(
            e=e,
            userID=message.from_user.id
        )


@rtr.message(AuctionFSM.AUC_ID, mF.text)
async def set_buyer(message: Message, state: FSMContext):
    try:
        f.update_config(config, [txt])
        try:
            auc_id = int(message.text)
            if auc_id not in lpsql.searchall("stores", "auctionID"):
                raise ValueError

            await state.update_data(AUC_ID=auc_id)
            saved = await state.get_data()
            m_id = (await message.answer(txt.LPAA.AUCTION.CONFIRM.format(
                lotID=saved["LOT"],
                name=saved["NAME"],
                price=saved["PRICE"],
                number=message.text
            ), reply_markup=InlineKeyboardBuilder([[InlineKeyboardButton(
                text="ОК",
                callback_data=f"lot+{saved["LOT"]}+{saved["NAME"]}+{saved["PRICE"]}+{message.text}"
            )]]).as_markup())).message_id
            exelink.sublist(
                mode='add',
                name='ccc/lpaa',
                key=message.chat.id,
                data=m_id,
                userID=message.from_user.id
            )
            await state.clear()
            tracker.log(
                command=("AUCTION_LOT", F.CYAN),
                status=("AUC_ID", F.YELLOW),
                from_user=f.collect_FU(message)
            )
        except ValueError:
            await message.answer(txt.LPAA.BAD_ARG)
            tracker.log(
                command=("AUCTION_LOT", F.CYAN),
                status=("AUC_ID", F.RED + S.DIM),
                from_user=f.collect_FU(message)
            )
    except Exception as e:
        tracker.error(
            e=e,
            userID=message.from_user.id
        )


@rtr.callback_query(mF.data.count("lot") > 0)
async def confirm_buying(callback: CallbackQuery):
    try:
        f.update_config(config, [txt])
        await callback.answer()
        saved = dict(zip([None, 'LOT', 'NAME', 'PRICE', 'AUC_ID'], callback.data.split('+')))
        storeID = lpsql.search("stores", "auctionID", saved["AUC_ID"])["ID"]
        try:
            lpsql.transfer(storeID, "auction_transfer_route", int(saved["PRICE"]))
            lpsql.insert("auction", [
                int(saved["LOT"]),      # lotID
                saved["NAME"],          # name
                int(saved["PRICE"]),    # price
                int(saved["AUC_ID"])    # auctionID
            ])
            for userID in lpsql.searchall("shopkeepers", "userID"):
                if lpsql.search("shopkeepers", "userID", userID)["storeID"] == storeID:
                    exelink.message(
                        text=txt.LPAA.AUCTION.MESSAGE.format(
                            lot=saved["LOT"],
                            name=saved["NAME"],
                            price=saved["PRICE"]
                        ),
                        bot="LPSB",
                        participantID=userID,
                        userID=callback.from_user.id
                    )
            exelink.sublist(
                mode='remove',
                name='ccc/lpaa',
                key=callback.message.chat.id,
                userID=callback.from_user.id
            )
            await callback.message.edit_text(callback.message.text + txt.LPAA.AUCTION.CONFIRMED)
            tracker.log(
                command=("AUCTION_LOT", F.CYAN),
                status=("CONFIRM", F.GREEN),
                from_user=f.collect_FU(callback)
            )
        except lpsql.errors.NotEnoughBalance:
            await callback.message.answer(txt.LPAA.AUCTION.NOT_ENOUGH_MONEY.format(
                lotID=saved["LOT"],
                balance=lpsql.balance_view(storeID)
            ))
            tracker.log(
                command=("AUCTION_LOT", F.CYAN),
                status=("PRICE", F.RED + S.DIM),
                from_user=f.collect_FU(callback)
            )
    except Exception as e:
        tracker.error(
            e=e,
            userID=callback.from_user.id
        )
