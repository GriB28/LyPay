from aiogram import Bot
from aiogram.types import Message as aio_message, CallbackQuery as aio_callback, FSInputFile, InputMediaPhoto, InputMediaVideo, ReactionTypeEmoji
from aiogram.exceptions import TelegramRetryAfter

from asyncio import sleep
from importlib import reload

from data.config import QUOTATION_ANCHOR, NEW_LINE_ANCHOR, OPEN_CURLY_BRACKET_ANCHOR, CLOSE_CURLY_BRACKET_ANCHOR, SPACE_ANCHOR, PATHS
from scripts.j2 import fromfile_async as j_fromfile_async, fromfile as j_fromfile
from scripts import exelink
from data.txt import EXE


async def parse_media_cache_ad_packet(*, bot: Bot, tech_message: str, sender_id: int | str, to: int, data: list[list[str]]):
    """
    Обрабатывает запрос отправки рекламы (в группу модерации)
    :param bot: aiogram.Bot
    :param tech_message: блок с техническим текстом
    :param sender_id: userID отправителя для записи в саблист
    :param to: ID группы модерации
    :param data: распакованные медиа в формате
    """
    if data[0][0] in ('photo', 'video'):
        m_id = (await bot.send_media_group(to, [
            (
                InputMediaPhoto(
                    media=data[i][1],
                    caption=data[i][2] if len(data[i]) > 2 and data[i][2] != "None" else None
                )
                if data[i][0] == 'photo' else
                InputMediaVideo(
                    media=data[i][1],
                    caption=data[i][2] if len(data[i]) > 2 and data[i][2] != "None" else None
                )
            ) for i in range(len(data))
        ]))[0].message_id
    else:
        m_id = (await bot.send_message(to, data[0][2])).message_id
    m_id_2 = (await bot.send_message(to, tech_message, reply_to_message_id=m_id)).message_id
    exelink.sublist(
        name='ad_approving',
        key=str(m_id_2),
        data=str(sender_id),
        userID=int(sender_id)
    )


async def send_message(*, bot: Bot, to: int, message: str,
                       file: str | None = None, file_mode: str | None = None,
                       update_keyboard: ... = lambda t: None, reset_keyboard: bool = False) -> None:
    """
    Отправляет сообщение с указанными параметрами
    :param bot: aiogram.Bot
    :param to: userID (chatID)
    :param message: текст
    :param file: данные для особого режима
    :param file_mode: флаг особого режима
    :param update_keyboard: функция обновления reply-клавиатуры
    :param reset_keyboard: флаг обновления reply-клавиатуры
    """
    ok = False
    tries = -2

    while not ok:
        tries += 1
        try:
            if file_mode is None:
                await bot.send_message(to, message, reply_markup=update_keyboard(to) if reset_keyboard else None)
            elif file_mode == 'photo_upload':
                await bot.send_photo(to, FSInputFile(file), caption=message, reply_markup=update_keyboard(to) if reset_keyboard else None)
            elif file_mode == 'photo_cache':
                await bot.send_photo(to, file, caption=message, reply_markup=update_keyboard(to) if reset_keyboard else None)
            elif file_mode == 'video_upload':
                await bot.send_video(to, FSInputFile(file), caption=message, reply_markup=update_keyboard(to) if reset_keyboard else None)
            elif file_mode == 'video_cache':
                await bot.send_video(to, file, caption=message, reply_markup=update_keyboard(to) if reset_keyboard else None)
            elif file_mode == 'media_cache_ad':
                data = list()
                for line in file.split(''):
                    data.append(line.split(':', 2))
                packet = message.split('\u00a0')
                await parse_media_cache_ad_packet(bot=bot, tech_message=packet[0], sender_id=packet[1], to=to, data=data)
            elif file_mode == 'set_reaction':  # to_ - chat_id; message_ - reaction; file_ - message_id
                await bot.set_message_reaction(
                    chat_id=to,
                    message_id=int(file),
                    reaction=[ReactionTypeEmoji(emoji=message[0])]
                )
            elif file_mode == 'sticker':
                await bot.send_sticker(to, file, reply_markup=update_keyboard(to) if reset_keyboard else None)
            else:
                await bot.send_document(to, FSInputFile(file), caption=message, reply_markup=update_keyboard(to) if reset_keyboard else None)
            ok = True
        except TelegramRetryAfter:
            await sleep(2.71828180 ** tries / 2)
        except Exception as e:
            print(to, e, e.args)
            ''' великий фикс анонсов
            exelink.warn(
                text=EXE.ALERTS.MESSAGE_SEND_FAIL.format(
                    bot=bot.token,
                    id=to
                ),
                userID=-1
            )
            '''
            return


def anchor(__s__: str) -> str:
    """
    :param __s__: строка для якорного преобразования
    :return: строка с якорями
    """
    return __s__.replace(
        '\n', NEW_LINE_ANCHOR
    ).replace(
        '{', OPEN_CURLY_BRACKET_ANCHOR
    ).replace(
        '}', CLOSE_CURLY_BRACKET_ANCHOR
    ).replace(
        '"', QUOTATION_ANCHOR
    ).replace(
        ' ', SPACE_ANCHOR
    )


def de_anchor(__s__: str) -> str:
    """
    :param __s__: строка для обратного якорного преобразования
    :return: строка без якорей
    """
    return __s__.replace(
        NEW_LINE_ANCHOR, '\n'
    ).replace(
        OPEN_CURLY_BRACKET_ANCHOR, '{'
    ).replace(
        CLOSE_CURLY_BRACKET_ANCHOR, '}'
    ).replace(
        QUOTATION_ANCHOR, '"'
    ).replace(
        SPACE_ANCHOR, ' '
    )


def collect_FU(__object__: aio_message | aio_callback) -> tuple[int, str | None]:
    """
    :param __object__: aiogram message or callback
    :return: (obj.from_user.id, obj.from_user.username)
    """
    return __object__.from_user.id, __object__.from_user.username


async def read_sublist(__name__: str) -> dict[str, ...]:
    """
    :param __name__: имя листа
    :return: json in dict
    """
    try:
        return await j_fromfile_async(PATHS.LISTS + __name__ + '.json')
    except FileNotFoundError:
        with open(PATHS.LISTS + __name__ + '.json', 'w', encoding='utf8') as f:
            f.write('{}')
        return {}


def update_config(__old_config_version__: list[int], __library_links__: list[...]) -> bool:
    """
    :param __old_config_version__: номер старой версии внутри списка, в списке должен быть только он
    :param __library_links__: список библиотек для перезагрузки
    :return: True если обновление произошло, False в обратном случае
    """
    if len(__old_config_version__) > 1:
        raise ValueError("Аргументы функции update_config указаны неверно.")
    current_v = j_fromfile(PATHS.LAUNCH_SETTINGS)["config_v"]
    if current_v != __old_config_version__[0]:
        __old_config_version__[0] = current_v
        for library in __library_links__:
            reload(library)
        return True
    return False
