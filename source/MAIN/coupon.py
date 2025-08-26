from aiogram import F as mF
from aiogram import Router
from aiogram.filters.command import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from colorama import Fore as F, Style as S

from data import txt
from data.config import PATHS
from scripts import f, firewall3, tracker, exelink, lpsql
from scripts.j2 import fromfile as j2_fromfile

import source.MAIN._keyboards as main_keyboard
from source.MAIN._states import *

rtr = Router()
config = [j2_fromfile(PATHS.LAUNCH_SETTINGS)["config_v"]]
firewall3 = firewall3.FireWall('MAIN')
db = lpsql.DataBase("lypay_database.db", lpsql.Tables.MAIN)
print("MAIN/coupon router")


@rtr.message(Command("coupon"))
async def promo_start(message: Message, state: FSMContext):
    try:
        f.update_config(config, [txt, main_keyboard])
        firewall_status = firewall3.check(message.from_user.id)
        if firewall_status == firewall3.WHITE_ANCHOR:
            if j2_fromfile(PATHS.LAUNCH_SETTINGS)["main_can_use_promo"]:
                await message.answer(txt.MAIN.PROMO_CODE.START, reply_markup=main_keyboard.update_keyboard(message.from_user.id, True))
                await state.set_state(CouponFSM.ID)
                await state.update_data(COUPON_ID=None)
                tracker.log(
                    command=("PROMOCODE", F.YELLOW + S.BRIGHT),
                    from_user=f.collect_FU(message)
                )
            else:
                await message.answer(txt.MAIN.PROMO_CODE.FORBIDDEN_BY_SETTINGS)
                tracker.log(
                    command=("PROMOCODE", F.YELLOW + S.BRIGHT),
                    status=("FORBIDDEN_BY_SETTINGS", F.RED + S.DIM),
                    from_user=f.collect_FU(message)
                )
        elif firewall_status == firewall3.BLACK_ANCHOR:
            tracker.black(f.collect_FU(message))
            await message.answer(txt.MAIN.CMD.IN_BLACKLIST)
        else:
            tracker.gray(f.collect_FU(message))
            await message.answer(txt.MAIN.CMD.NOT_IN_WHITELIST)
    except Exception as e:
        tracker.error(
            e=e,
            userID=message.from_user.id
        )


@rtr.message(CouponFSM.ID, mF.text)
async def input_promo(message: Message, state: FSMContext):
    try:
        f.update_config(config, [txt, main_keyboard])
        coupon_id = message.text.lower()
        coupons = await f.read_sublist("promo")
        keys = list(coupons.keys())
        for key in keys:
            if key != key.lower():
                coupons[key.lower()] = coupons[key]
                coupons.pop(key)
        if coupon_id in coupons.keys():
            coupon = coupons[coupon_id].rsplit(';', 2)
            if coupon[2] == '1':
                await state.update_data(COUPON_ID=coupon_id)
                m_id = (await message.answer(txt.MAIN.PROMO_CODE.INPUT.format(
                    id=coupon_id,
                    author=coupon[0],
                    value=coupon[1]
                ), reply_markup=main_keyboard.promoCMD)).message_id
                exelink.sublist(
                    mode='add',
                    name='ccc/main',
                    key=message.chat.id,
                    data=m_id,
                    userID=message.from_user.id
                )
                tracker.log(
                    command=("PROMOCODE", F.YELLOW + S.BRIGHT),
                    status=("INPUT", F.YELLOW),
                    from_user=f.collect_FU(message)
                )
            else:
                await message.answer(txt.MAIN.PROMO_CODE.ALREADY_ACTIVATED)
                tracker.log(
                    command=("PROMOCODE", F.YELLOW + S.BRIGHT),
                    status=("ALREADY_ACTIVATED", F.RED + S.DIM),
                    from_user=f.collect_FU(message)
                )
        else:
            await message.answer(txt.MAIN.PROMO_CODE.BAD_ID)
            tracker.log(
                command=("PROMOCODE", F.YELLOW + S.BRIGHT),
                status=("BAD_ID", F.RED + S.DIM),
                from_user=f.collect_FU(message)
            )
    except Exception as e:
        tracker.error(
            e=e,
            userID=message.from_user.id
        )


@rtr.callback_query(mF.data == "promo_activate_cb")
async def activate_promo(callback: CallbackQuery, state: FSMContext):
    try:
        f.update_config(config, [txt, main_keyboard])
        coupons = await f.read_sublist("promo")
        keys = list(coupons.keys())
        for key in keys:
            if key != key.lower():
                coupons[key.lower()] = coupons[key]
                coupons.pop(key)

        try:
            coupon_id = (await state.get_data())["COUPON_ID"]
        except KeyError:
            coupon_id = None
        if coupon_id in coupons.keys():
            coupon = coupons[coupon_id].rsplit(';', 2)
            if coupon[2] == '1':
                coupon[2] = '0'
                exelink.sublist(
                    name="promo",
                    key=coupon_id,
                    data=';'.join(coupon),
                    userID=callback.from_user.id
                )
                db.deposit(callback.from_user.id, int(coupon[1]), f"_promo:{coupon_id}")
                await callback.message.edit_text(callback.message.text + "\n\n> Активирован")
                await callback.message.answer(txt.MAIN.PROMO_CODE.ACTIVATE)
                await callback.message.answer(txt.MAIN.DEPOSIT.UPDATE.format(value=f'+{coupon[1]}'),
                                              reply_markup=main_keyboard.update_keyboard(callback.from_user.id))
                exelink.sublist(
                    mode='remove',
                    name='ccc/main',
                    key=callback.message.chat.id,
                    userID=callback.from_user.id
                )
                tracker.log(
                    command=("PROMOCODE", F.YELLOW + S.BRIGHT),
                    status=("ACTIVATED", F.GREEN),
                    from_user=f.collect_FU(callback)
                )
            else:
                await callback.message.edit_text(callback.message.text + "\n\n> " + txt.MAIN.PROMO_CODE.ALREADY_ACTIVATED[1:])
                tracker.log(
                    command=("PROMOCODE", F.YELLOW + S.BRIGHT),
                    status=("ALREADY_ACTIVATED", F.RED + S.DIM),
                    from_user=f.collect_FU(callback)
                )
        else:
            await callback.message.edit_text(callback.message.text + "\n\n> " + txt.MAIN.PROMO_CODE.BECOME_BAD_ID[1:])
            tracker.log(
                command=("PROMOCODE", F.YELLOW + S.BRIGHT),
                status=("BECOME_BAD_ID", F.RED + S.DIM),
                from_user=f.collect_FU(callback)
            )

        await callback.answer()
    except Exception as e:
        tracker.error(
            e=e,
            userID=callback.from_user.id
        )
