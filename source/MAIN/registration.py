from aiogram import Router
from aiogram.filters import CommandStart, CommandObject
from aiogram.types import Message, CallbackQuery, InlineKeyboardButton, LinkPreviewOptions
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.fsm.context import FSMContext
from aiogram import F as mF

from os import getenv
from dotenv import load_dotenv

from aiohttp import ClientSession as aiohttp_ClientSession, TCPConnector
from ssl import create_default_context as ssl_create_default_context, CERT_NONE as ssl_CERT_NONE
from asyncio import sleep
from os.path import exists
from colorama import Fore as F
from random import randint
import jwt

from scripts import f, tracker, exelink, lpsql
from scripts.unix import unix
from scripts.j2 import fromfile_async as j_fromfile_async, fromfile as j_fromfile
from data import config as cfg, txt

from source.MAIN._states import *
import source.MAIN._keyboards as main_keyboard


load_dotenv()
integration_bot_tag = getenv("LYPAY_INTEGRATION_BOT_TAG")
integration_bridge_host = getenv("LYPAY_INTEGRATION_BRIDGE_HOST")
integration_bridge_jwt = getenv("LYPAY_INTEGRATION_BRIDGE_JWT")

rtr = Router()
config = [j_fromfile(cfg.PATHS.LAUNCH_SETTINGS)["config_v"]]
db = lpsql.DataBase("lypay_database.db", lpsql.Tables.MAIN)
print("MAIN/registration router")

base16 = tuple('0123456789abcdef')
base36 = tuple('0123456789abcdefghijklmnopqrstuvwxyz')
letters = tuple('абвгдеёжзийклмнопрстуфхцчшщъыьэюя-–—')


def register_proceed(tg_id: int, name: str, group: str, email: str, tag: str | None, owner: int):
    db.insert("users",
              [
                     tg_id,  # ID
                     name,   # name
                     group,  # class
                     email,  # email
                     tag,    # tag
                     0,      # balance
                     owner   # owner
                 ])
    if not exists(cfg.PATHS.QR + f"{tg_id}.png"):
        exelink.add(f"qr {tg_id}", tg_id)
        db.insert("qr",
                  [
                         tg_id,  # userID
                         None,   # fileID_main
                         None,   # fileID_lpsb
                         None    # fileID_lpaa
                     ])


@rtr.callback_query(RegisterFSM.STATE0, mF.data == 'register_main_cb')
async def main_route(callback: CallbackQuery, state: FSMContext):
    try:
        f.update_config(config, [txt, cfg, main_keyboard])
        await callback.message.edit_text(
            txt.MAIN.REGISTRATION.NEW + "\n" + txt.MAIN.REGISTRATION.NEW_MAIN,
            link_preview_options=LinkPreviewOptions(is_disabled=True)
        )
        await callback.answer()
        exelink.sublist(
            mode='remove',
            name='ccc/main',
            key=callback.message.chat.id,
            userID=callback.from_user.id
        )
        await state.set_state(RegisterFSM.EMAIL)
        await state.update_data(GUEST=False)
        tracker.log(
            command=("REGISTRATION", F.YELLOW),
            status=("MAIN_ROUTE", F.YELLOW),
            from_user=f.collect_FU(callback)
        )
    except Exception as e:
        tracker.error(
            e=e,
            userID=callback.from_user.id
        )


@rtr.callback_query(RegisterFSM.STATE0, mF.data == 'register_guest_cb')
async def guest_route(callback: CallbackQuery, state: FSMContext):
    try:
        f.update_config(config, [txt, cfg, main_keyboard])
        await callback.message.edit_text(
            txt.MAIN.REGISTRATION.NEW + "\n" + txt.MAIN.REGISTRATION.NEW_GUEST,
            link_preview_options=LinkPreviewOptions(is_disabled=True)
        )
        await callback.answer()
        exelink.sublist(
            mode='remove',
            name='ccc/main',
            key=callback.message.chat.id,
            userID=callback.from_user.id
        )
        await state.set_state(RegisterFSM.EMAIL)
        await state.update_data(GUEST=True)
        tracker.log(
            command=("REGISTRATION", F.MAGENTA),
            status=("GUEST_ROUTE", F.MAGENTA),
            from_user=f.collect_FU(callback)
        )
    except Exception as e:
        tracker.error(
            e=e,
            userID=callback.from_user.id
        )


@rtr.message(RegisterFSM.EMAIL, mF.text, mF.text != "/cancel")
async def send_email(message: Message, state: FSMContext):
    try:
        f.update_config(config, [txt, cfg, main_keyboard])
        em = message.text.lower().strip()
        if em[-17:] != "@students.sch2.ru" and em[-8:] != "@sch2.ru":
            tracker.log(
                command=("REGISTRATION_EMAIL", F.YELLOW),
                status=("BAD_FORMAT", F.RED),
                from_user=f.collect_FU(message)
            )
            await message.answer(txt.MAIN.REGISTRATION.EMAIL.BAD)
        elif em not in db.searchall("corporation", "email"):
            tracker.log(
                command=("REGISTRATION_EMAIL", F.YELLOW),
                status=("NOT_FOUND", F.RED),
                from_user=f.collect_FU(message)
            )
            await message.answer(txt.MAIN.REGISTRATION.EMAIL.NOT_IN_DATABASE)
        else:
            tracker.log(
                command=("REGISTRATION_EMAIL", F.YELLOW),
                status=("SUCCESS", F.GREEN),
                from_user=f.collect_FU(message)
            )
            await state.set_state(RegisterFSM.CODE)

            code = "".join([base16[randint(0, 15)] for _ in range(32)])

            await state.update_data(EMAIL=em)
            await state.update_data(CODE=code)

            if (await state.get_data())["GUEST"]:
                exelink.email(
                    path=cfg.PATHS.EMAIL + "guest.html",
                    participantEmail=message.text,
                    theme="Регистрация в LyPay: Гостевой доступ",
                    keys={
                        "VERSION": cfg.VERSION,
                        "BUILD": cfg.BUILD,
                        "NAME": f' ({cfg.NAME})' if cfg.NAME != '' else '',
                        "CODE": code,
                        "UID": message.from_user.id,
                        "CID": message.chat.id,
                        "UX": unix()
                    },
                    userID=message.from_user.id
                )
            else:
                exelink.email(
                    path=cfg.PATHS.EMAIL + "main.html",
                    participantEmail=message.text,
                    theme="Регистрация в LyPay",
                    keys={
                        "VERSION": cfg.VERSION,
                        "BUILD": cfg.BUILD,
                        "NAME": f' ({cfg.NAME})' if cfg.NAME != '' else '',
                        "CODE": code
                    },
                    userID=message.from_user.id
                )
            await message.answer(txt.MAIN.REGISTRATION.EMAIL.OK)
    except Exception as e:
        tracker.error(
            e=e,
            userID=message.from_user.id
        )


@rtr.message(RegisterFSM.CODE, mF.text, mF.text != "/cancel")
async def check_email_code(message: Message, state: FSMContext):
    try:
        f.update_config(config, [txt, cfg, main_keyboard])
        data = await state.get_data()
        if message.text.lower().strip() == data["CODE"]:
            if data["GUEST"]:
                await message.answer(txt.MAIN.REGISTRATION.ACTIVATION.NAME_PROCEED)
                await state.set_state(RegisterFSM.GUEST_NAME_INPUT)

            else:
                user = db.search("corporation", "email", data["EMAIL"])
                register_proceed(
                    message.from_user.id,
                    user["name"],
                    user["class"],
                    data["EMAIL"],
                    message.from_user.username,
                    1
                )
                await message.answer(txt.MAIN.REGISTRATION.ACTIVATION.OK,
                                     reply_markup=main_keyboard.update_keyboard(message.from_user.id))
                await state.clear()
            tracker.log(
                command=("ACTIVATION_CODE", F.YELLOW),
                status=("OK", F.GREEN),
                from_user=f.collect_FU(message)
            )

        else:
            await message.answer(txt.MAIN.REGISTRATION.ACTIVATION.WRONG.format(
                email=(await state.get_data())["EMAIL"]
            ))
            tracker.log(
                command=("ACTIVATION_CODE", F.YELLOW),
                status=("WRONG", F.RED),
                from_user=f.collect_FU(message)
            )
    except Exception as e:
        tracker.error(
            e=e,
            userID=message.from_user.id
        )


@rtr.message(RegisterFSM.GUEST_NAME_INPUT, mF.text, mF.text != "/cancel")
async def enter_guest_name(message: Message, state: FSMContext):
    try:
        f.update_config(config, [txt, cfg, main_keyboard])
        censor = tracker.censor(
            from_user=f.collect_FU(message),
            text=message.text
        )
        if not censor:
            await message.answer(txt.MAIN.CMD.CENSOR_BLACK)
            return
        name = ' '.join(map(lambda part: part.capitalize(), message.text.strip().split()))
        if name.count(' ') == 0 or any(letter not in letters for letter in name.replace(' ', '').lower()):
            await message.answer(txt.MAIN.REGISTRATION.ACTIVATION.NAME_BAD_FORMAT)
            tracker.log(
                command=("ENTER_NAME", F.YELLOW),
                status=("BAD_FORMAT", F.RED),
                from_user=f.collect_FU(message)
            )
        else:
            register_proceed(
                message.from_user.id,
                name,
                "гость",
                (await state.get_data())["EMAIL"],
                message.from_user.username,
                0
            )
            await message.answer(txt.MAIN.REGISTRATION.ACTIVATION.OK,
                                 reply_markup=main_keyboard.update_keyboard(message.from_user.id))
            await state.clear()
            tracker.log(
                command=("ENTER_NAME", F.YELLOW),
                status=("SUCCESS", F.GREEN),
                from_user=f.collect_FU(message)
            )
    except Exception as e:
        tracker.error(
            e=e,
            userID=message.from_user.id
        )


# -=-=-=-

@rtr.callback_query(RegisterFSM.STATE0, mF.data == 'register_linking_cb')
async def link_route(callback: CallbackQuery, state: FSMContext):
    try:
        f.update_config(config, [txt, cfg, main_keyboard])
        if (await j_fromfile_async(cfg.PATHS.LAUNCH_SETTINGS))["main_can_register_via_linking"]:
            exelink.sublist(
                mode='remove',
                name='ccc/main',
                key=callback.message.chat.id,
                userID=callback.from_user.id
            )

            code = "".join([base36[randint(0, 35)] for _ in range(50)])
            await state.update_data(LINK_CODE=code)
            await callback.answer()
            await callback.message.edit_text(
                txt.MAIN.REGISTRATION.NEW + "\n" + txt.MAIN.REGISTRATION.NEW_LINK,
                reply_markup=InlineKeyboardBuilder([[
                    InlineKeyboardButton(
                        text="🔗 Привязать",
                        url=f"https://t.me/{integration_bot_tag}?start=lypay_auth_{code}"
                    )
                ]]).as_markup(),
                link_preview_options=LinkPreviewOptions(is_disabled=True)
            )

            await state.set_state(RegisterFSM.LINK)
            tracker.log(
                command=("REGISTRATION", F.YELLOW),
                status=("LINK_ROUTE", F.YELLOW),
                from_user=f.collect_FU(callback)
            )
        else:
            await callback.answer()
            await callback.message.answer(txt.MAIN.REGISTRATION.LINK.FORBIDDEN_BY_SETTINGS)
            tracker.log(
                command=("REGISTRATION", F.YELLOW),
                status=("LINK_ROUTE", F.YELLOW),
                from_user=f.collect_FU(callback)
            )
    except Exception as e:
        tracker.error(
            e=e,
            userID=callback.from_user.id
        )


@rtr.message(RegisterFSM.LINK, CommandStart(deep_link=True))
async def check_link(message: Message, state: FSMContext, command: CommandObject):
    try:
        f.update_config(config, [txt, cfg, main_keyboard])
        await message.delete()
        token = command.args[6:]
        tries = 0
        jwt_code = None
        ssl_context = ssl_create_default_context()
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl_CERT_NONE
        while tries < 3:
            try:
                async with aiohttp_ClientSession(connector=TCPConnector(ssl=ssl_context)) as session:
                    async with session.get(f"{integration_bridge_host}/{token}") as response:
                        if response.status == 200:
                            jwt_code = (await response.text()).strip('"')
                            break
                        else:
                            raise Exception
            except:
                await sleep(1)
                tries += 1
        if jwt_code is None:
            await message.answer(txt.MAIN.REGISTRATION.LINK.BAD_REQUEST)
            tracker.log(
                command=("REGISTRATION", F.YELLOW),
                status=("BAD_REQUEST", F.RED),
                from_user=f.collect_FU(message)
            )
            exelink.warn(
                text=txt.EXE.ALERTS.BRIDGE_BAD_REQUEST,
                userID=message.from_user.id
            )
        else:
            data = await state.get_data()
            try:
                decoded_json = jwt.decode(jwt_code, integration_bridge_jwt, algorithms=["HS256"])

                if decoded_json["auth_code"] != data["LINK_CODE"] or decoded_json["telegram_id"] != message.from_user.id:
                    code = "".join([base36[randint(0, 35)] for _ in range(50)])
                    await state.update_data(LINK_CODE=code)
                    await message.answer(
                        txt.MAIN.REGISTRATION.LINK.BAD_TOKEN_CHECK,
                        reply_markup=InlineKeyboardBuilder([[
                            InlineKeyboardButton(
                                text="Привязать 🔗",
                                url=f"https://t.me/{integration_bot_tag}?start=lypay_auth_{code}"
                            )
                        ]]).as_markup()
                    )
                    tracker.log(
                        command=("REGISTRATION", F.YELLOW),
                        status=("BAD_TOKEN_CHECK", F.RED),
                        from_user=f.collect_FU(message)
                    )
                else:
                    decoded_email = decoded_json["email"]
                    base_request = db.search("corporation", "email", decoded_email)
                    if base_request is None:
                        await message.answer(txt.MAIN.REGISTRATION.LINK.BAD_EMAIL_CHECK)
                        m_id = (await message.answer(
                            txt.MAIN.REGISTRATION.NEW,
                            reply_markup=main_keyboard.registerCMD,
                            link_preview_options=LinkPreviewOptions(is_disabled=True)
                        )).message_id
                        exelink.sublist(
                            mode='add',
                            name='ccc/main',
                            key=message.chat.id,
                            data=m_id,
                            userID=message.from_user.id
                        )
                        await state.clear()
                        await state.set_state(RegisterFSM.STATE0)
                        tracker.log(
                            command=("REGISTRATION", F.YELLOW),
                            status=("BAD_EMAIL_CHECK", F.RED),
                            from_user=f.collect_FU(message)
                        )
                    else:
                        decoded_class = 'сотрудник' if decoded_json["role"] in ("admin", "teacher") else \
                            ('гость' if decoded_json["role"][:6] == "parent" else None)
                        if decoded_class is None:
                            decoded_class = base_request["class"]

                        await state.update_data(JWT=decoded_json)

                        m_id = (await message.answer(
                            txt.MAIN.REGISTRATION.LINK.CONFIRM.format(
                                name=base_request["name"],
                                group=decoded_class,
                                email=decoded_email
                            ),
                            reply_markup=main_keyboard.registerLinkCMD
                        )).message_id
                        exelink.sublist(
                            mode='add',
                            name='ccc/main',
                            key=message.chat.id,
                            data=m_id,
                            userID=message.from_user.id
                        )
                        await state.set_state(RegisterFSM.CONFIRM_LINKING)
                        tracker.log(
                            command=("REGISTRATION", F.YELLOW),
                            status=("CONFIRM_LINKED_DATA", F.GREEN),
                            from_user=f.collect_FU(message)
                        )
            except jwt.ExpiredSignatureError:
                code = "".join([base36[randint(0, 35)] for _ in range(50)])
                await state.update_data(LINK_CODE=code)
                await message.answer(
                    txt.MAIN.REGISTRATION.LINK.TOKEN_EXPIRED,
                    reply_markup=InlineKeyboardBuilder([[
                        InlineKeyboardButton(
                            text="Привязать 🔗",
                            url=f"https://t.me/{integration_bot_tag}?start=lypay_auth_{code}"
                        )
                    ]]).as_markup()
                )
                tracker.log(
                    command=("REGISTRATION", F.YELLOW),
                    status=("TOKEN_EXPIRED", F.RED),
                    from_user=f.collect_FU(message)
                )
            except jwt.InvalidTokenError:
                code = "".join([base36[randint(0, 35)] for _ in range(50)])
                await state.update_data(LINK_CODE=code)
                await message.answer(
                    txt.MAIN.REGISTRATION.LINK.INVALID_TOKEN,
                    reply_markup=InlineKeyboardBuilder([[
                        InlineKeyboardButton(
                            text="Привязать 🔗",
                            url=f"https://t.me/{integration_bot_tag}?start=lypay_auth_{code}"
                        )
                    ]]).as_markup()
                )
                tracker.log(
                    command=("REGISTRATION", F.YELLOW),
                    status=("INVALID_TOKEN", F.RED),
                    from_user=f.collect_FU(message)
                )
    except Exception as e:
        tracker.error(
            e=e,
            userID=message.from_user.id
        )


@rtr.callback_query(RegisterFSM.CONFIRM_LINKING, mF.data == "register_link_confirm_cb")
async def link_confirm(callback: CallbackQuery, state: FSMContext):
    try:
        f.update_config(config, [txt, cfg, main_keyboard])
        await callback.message.edit_text(callback.message.text + "\n> 'Всё верно ✅'")
        await callback.answer()

        decoded_json = (await state.get_data())["JWT"]
        decoded_email = decoded_json["email"]
        base_request = db.search("corporation", "email", decoded_email)
        decoded_class = 'сотрудник' if decoded_json["role"] in ("admin", "teacher") else \
            ('гость' if decoded_json["role"][:6] == "parent" else None)
        if decoded_class is None:
            decoded_class = base_request["class"]
        decoded_owner = 3 if decoded_json["role"][:6] == "parent" else 2

        register_proceed(
            callback.from_user.id,
            base_request["name"],
            decoded_class,
            decoded_email,
            callback.from_user.username,
            decoded_owner
        )

        await callback.message.answer(txt.MAIN.REGISTRATION.ACTIVATION.OK,
                                      reply_markup=main_keyboard.update_keyboard(callback.from_user.id))
        await state.clear()
        exelink.sublist(
            mode='remove',
            name='ccc/main',
            key=callback.message.chat.id,
            userID=callback.from_user.id
        )
        tracker.log(
            command=("REGISTRATION", F.YELLOW),
            status=("LINKED_SUCCESSFULLY", F.GREEN),
            from_user=f.collect_FU(callback)
        )
    except Exception as e:
        tracker.error(
            e=e,
            userID=callback.from_user.id
        )


@rtr.callback_query(RegisterFSM.CONFIRM_LINKING, mF.data == "register_link_back_cb")
async def link_get_back(callback: CallbackQuery, state: FSMContext):
    try:
        f.update_config(config, [txt, cfg, main_keyboard])
        await callback.message.edit_text(callback.message.text + "\n> 'Назад ◀️'")
        await callback.answer()

        m_id = (await callback.message.answer(
            txt.MAIN.REGISTRATION.NEW_FROM_LINK_DENY,
            reply_markup=main_keyboard.registerCMD,
            link_preview_options=LinkPreviewOptions(is_disabled=True)
        )).message_id
        exelink.sublist(
            mode='add',
            name='ccc/main',
            key=callback.message.chat.id,
            data=m_id,
            userID=callback.from_user.id
        )
        await state.update_data(LINK_CODE=None)
        await state.set_state(RegisterFSM.STATE0)
    except Exception as e:
        tracker.error(
            e=e,
            userID=callback.from_user.id
        )
