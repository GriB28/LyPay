from os.path import exists
from time import sleep
from data.config import PATHS, WARNING_GROUP
from data.txt import EXE
from scripts import j2, unix


def add(task: str, userID: int, subtasks: list[str] | None = None):
    unix_stamp = f"{unix.raw() % 1000}"[:8].replace('.', '')
    while exists(PATHS.EXE + f'{userID}_{unix_stamp}.json') or exists(PATHS.EXE + f'{userID}_{unix_stamp}_0.sub'):
        sleep(.002)
        unix_stamp = f"{unix.raw() % 1000}"[:8].replace('.', '')
    with open(PATHS.EXE + f'{userID}_{unix_stamp}.json', 'w', encoding='utf8') as t:
        t.write(j2.to_({
            "unix": unix.unix(),
            "sub": len(subtasks) if subtasks else 0,
            "task": task
        }))
    if subtasks:
        for i in range(len(subtasks)):
            with open(PATHS.EXE + f'{userID}_{unix_stamp}_{i}.sub', 'w', encoding='utf8') as st:
                st.write(subtasks[i])


def message(*, text: str, file_path: str | None = None, file_mode: str | None = None, bot: str, participantID: int, reset: bool = False, userID: int):
    """
    :param text: текст сообщения
    :param file_path: путь к фото или файлу для отправки (если есть)
    :param file_mode: режим отправки file_path: 'file' отправит как файл,
    'photo_upload' загрузит файл как фото с диска, 'photo_cache' запросит кэшированное фото с серверов ТГ,
    'video_upload' и 'video_cache' сделают то же самое для видео,
    'media_cache_ad' отправит медиа группу, собранную по ID объектов в file_path (ad only)
    'set_reaction' поставит реакцию на сообщение для chat_id=participantID, message_id=file_path
    'sticker' отправит стикер по ID из file_mode
    :param bot: название бота
    :param participantID: получатель
    :param reset: нужно ли сбросить клавиатуру
    :param userID: -
    """
    if len(text) == 0 or file_mode not in ('file', 'photo_upload', 'photo_cache', 'video_upload', 'video_cache',
                                           'media_cache_ad', 'set_reaction', 'sticker', None):
        raise ValueError("Аргументы функции message указанны неверно.")
    bot = bot.upper()
    if bot not in ('MAIN', 'LPSB', 'LPAA', 'SRV'):
        raise ValueError("Аргумент 'bot' функции message указан неверно.")
    add(f"message {bot} {participantID} {int(reset)}", userID, [text] + (([file_mode] + [file_path]) if file_path else []))


def email(*, path: str, participantEmail: str, theme: str, keys: dict[str, ...] | None = None, files: list[str] | None = None, userID: int):
    """
    :param path: путь до html-файла с основой письма и текстом
    :param participantEmail: email получателя
    :param theme: тема письма
    :param keys: словарь ключей для замены (по умолчанию не используется)
    :param files: список (абсолютных) путей к файлам для отправки в качестве приложенных файлов (по умолчанию не используется)
    :param userID: -
    """
    if len(path) == 0 or len(participantEmail) == 0 or len(theme) == 0:
        raise ValueError("Аргументы функции email указанны неверно.")
    if files is not None:
        if sum(1 for file in files if not exists(file)) > 0:
            raise FileNotFoundError("Некоторые файлы из прикреплённых не найдены.")
    add(f"email {participantEmail}", userID, [path, theme] + ([j2.to_(keys)] if keys else []) + (files if files else []))


def cheque(*, participantStoreID: str, chequeID: str, userID: int):
    """
    :param participantStoreID: получатель (магазин)
    :param chequeID: -
    :param userID: -
    """
    add(f"cheque {participantStoreID} {chequeID}", userID)


def warn(*, text: str, userID: int):
    """
    :param text: текст предупреждения
    :param userID: -
    """
    message(text=text, bot='LPAA', participantID=WARNING_GROUP, userID=userID)


def error_traceback(*, err: str, error_log: str, userID: int):
    """
    :param err: текст ошибки
    :param error_log: путь до файла с логом
    :param userID: -
    """
    message(text=err, file_path=error_log, file_mode='file', bot='LPAA', participantID=WARNING_GROUP, userID=userID)


def send_snapshot(*path_args, pid: int, userID: int):
    """
    загружает из * все пути для создания снапшота
    :param pid: исполнительный process ID
    :param userID: -
    """
    snapshots = list()
    for path in path_args:
        with open(path, encoding='utf8') as task_file:
            snapshots.append(f"snapshot:task\n[{path}]\n<code>{task_file.read()}</code>")

    message(
        text=EXE.ALERTS.SNAPSHOT_FORMAT.format(pid=pid, snaps='\n\n'.join(snapshots) if len(snapshots) > 0 else "*ничего нет*\n*звуки сверчков*"),
        bot='LPAA',
        participantID=WARNING_GROUP,
        userID=userID
    )


def photo(*, bot: str, fileID: str, path: str, userID: int):
    """
    :param bot: бот ('main', 'lpsb' или 'lpaa')
    :param fileID: фото
    :param path: путь для скачивания
    :param userID: -
    """
    bot = bot.lower()
    if bot not in ('main', 'lpsb', 'lpaa'):
        raise ValueError("Аргумент bot функции photo указан неверно.")
    add(f"photo {bot} {fileID}", userID, [path])


def sublist(*, mode: str = 'add', name: str, key: str | int, data: str | int | None = None, userID: int):
    """
    :param mode: 'add' или 'remove'
    :param name: имя листа
    :param key: ключ, по которому будет записана/удалена запись
    :param data: значение для записи
    :param userID: -
    """
    if name.count(' ') > 0:
        raise ValueError("Аргумент name функции sublist не должен содержать пробелы.")
    if mode not in ('add', 'remove'):
        raise ValueError("Аргумент mode функции sublist указан неверно.")
    if mode == 'add' and data is None:
        raise ValueError("Аргумент data функции sublist не может быть пуст в режиме записи.")
    add(f"sublist {mode} {name} {key}", userID, [str(data)] if mode == 'add' and data is not None else None)


def ccc_remove_keyboard(*, bot: str, chat_id: int | str, message_id: int, text: str, userID: int):
    """
    :param bot: бот ('main', 'lpsb' или 'lpaa')
    :param chat_id: -
    :param message_id: -
    :param text: -
    :param userID: -
    """
    bot = bot.lower()
    if bot not in ('main', 'lpsb', 'lpaa'):
        raise ValueError("Аргумент bot функции ccc_remove_keyboard указан неверно.")
    add(f"ccc_edit {bot} {chat_id} {message_id}", userID, [text])
