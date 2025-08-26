from datetime import datetime

from winsound import PlaySound, SND_ASYNC
from colorama import Fore, Style, init as c_init
from pyfiglet import figlet_format as media_text
from traceback import format_exc
from os import environ

from scripts import exelink, lpsql
from scripts.unix import unix
from data.config import PATHS, NAME, VERSION
from data.txt import LPAA as t_LPAA, EXE as t_EXE

c_init(autoreset=True)

db = lpsql.DataBase("lypay_database.db", lpsql.Tables.MAIN)

BOT = ''
LENGTH = 36


def startup(bot: str, *updates: str) -> None:
    """
    Печатает в консоль приветствие
    :param bot: main | lpaa | lpsb | auc
    """
    bot = bot.upper()
    if bot not in ("MAIN", "LPAA", "LPSB", "AUC"):
        raise ValueError
    global BOT
    BOT = bot

    bot_text = media_text("LyPay | " + bot)
    version_text = media_text(' '.join(list(VERSION)))
    print(bot_text)
    print(version_text)
    print(NAME)
    print("INFO LOGS", datetime.now().strftime('%d/%m/%y'))
    print()
    for u in updates:
        print(u)
    print()
    PlaySound('SystemAsterisk', SND_ASYNC)


def log(*, command: tuple[str, str], status: tuple[str, str] = None, from_user: tuple[int, str | None]) -> None:
    """
    Простой лог
    :param command: первая часть, текст / цвет
    :param status: вторая часть, текст / цвет
    :param from_user: (userID, tag)
    """
    t = datetime.now()
    print()
    length = LENGTH - len(command[0])

    if check(from_user):
        update(from_user)

    if status is None:
        print(
            '[', ' ' * (length % 2 + length // 2), command[1] + command[0],
            ' ' * (length // 2), ']',
            sep='', end='   '
        )
    else:
        length -= len(status[0]) + 1
        print(
            '[', ' ' * (length % 2 + length // 2),
            command[1] + command[0], ':',
            status[1] + status[0],
            ' ' * (length // 2), ']',
            sep='', end='   '
        )
    print(
        '[',
        Fore.YELLOW + Style.DIM + t.strftime('%X'),
        ']',
        end='   '
    )
    print(
        '[',
        Fore.CYAN + Style.BRIGHT + str(from_user[1] if from_user[1] else from_user[0]),
        ']',
        end='   '
    )
    if BOT == "LPSB" or BOT == "AUC":
        store = db.search("shopkeepers", "userID", from_user[0])
        if store:
            print(
                '[',
                Fore.GREEN + Style.BRIGHT + store["storeID"] + Style.RESET_ALL,
                ']',
                end=''
            )
    print()


def black(from_user: tuple[int, str | None]) -> None:
    log(
        command=("IN_BLACKLIST", Fore.RED + Style.BRIGHT),
        from_user=from_user
    )
    exelink.warn(
        text=t_EXE.WHITELIST.BLACK.format(id=from_user[0], tag='@' + from_user[1] if from_user[1] else '–'),
        userID=from_user[0]
    )


def gray(from_user: tuple[int, str | None]) -> None:
    log(
        command=("NOT_IN_WHITELIST", Fore.RED + Style.BRIGHT),
        from_user=from_user
    )
    exelink.warn(
        text=t_EXE.WHITELIST.GRAY.format(id=from_user[0], tag='@' + from_user[1] if from_user[1] else '–'),
        userID=from_user[0]
    )


def censor(*, from_user: tuple[int, str | None], text: str, text_length_flag: bool = True) -> bool:
    """
    Возвращает True, если сообщение прошло проверку. False -- в обратном случае.
    :param from_user: FU data
    :param text: текст для проверки
    :param text_length_flag: флаг проверки длины текста. True -- если проверка длины необходима
    :return: bool
    """
    list_gray = ["https", "http"]
    list_black = ["<b", "</b", "<a", "</a", "<i", "</i", "<span", "</span", "<tg-spoiler", "</tg-spoiler", "<code",
                  "</code", "<s", "</s", "<u", "</u", "<blockquote", "</blockquote"]
    gray_warn = False
    black_warn = False

    if text_length_flag and len(text) >= 250:
        gray_warn = True
    if not gray_warn:
        for line in list_gray:
            if text.find(line) != -1:
                gray_warn = True
                break

    for line in list_black:
        if text.find(line) != -1:
            black_warn = True
            break

    if black_warn:
        exelink.warn(
            text=t_LPAA.SPAM_B.format(
                user=from_user[0],
                bot=BOT,
                message=text.replace('<', '‹').replace('>', '›')
            ),
            userID=from_user[0]
        )
        return False
    if gray_warn:
        exelink.warn(
            text=t_LPAA.SPAM.format(
                user=from_user[0],
                bot=BOT,
                message=text
            ),
            userID=from_user[0]
        )
    return True


def check(from_user: tuple[int, str | None]) -> bool | None:
    user = db.search("users", "ID", from_user[0])
    if user is None:
        return None
    return user["tag"] != from_user[1]


def update(from_user: tuple[int, str | None]) -> None:
    db.update("users", "ID", from_user[0], "tag", from_user[1])


def error(*, e: Exception, userID: int) -> None:
    unix_timestamp = unix()
    error_timestamp = f"error_{round(unix_timestamp * 100)}"
    full_trace = format_exc()
    log_path = PATHS.EXE + f"{error_timestamp}.log"

    with open(log_path, 'w', encoding='utf8') as tmp_f:
        tmp_f.write(full_trace)

    crop_trace = ''
    newlines = 0
    for i in range(len(full_trace)-1, -1, -1):
        if newlines > 3:
            break
        if full_trace[i] == '\n':
            newlines += 1
        crop_trace = full_trace[i] + crop_trace

    exelink.error_traceback(
        err=f"#{error_timestamp}\n\nlast trace call: <code>{crop_trace}</code>\nuser id: <code>{userID}</code>",
        userID=userID,
        error_log=log_path
    )

    parsed_traceback_anchor = full_trace.rfind("Traceback:")
    full_trace = full_trace[parsed_traceback_anchor:]

    file_ = 42
    full_trace = full_trace[file_+1:]
    file_str = full_trace[:full_trace.find(',')-1]

    line_ = full_trace.find(' ') + 6
    full_trace = full_trace[line_:]
    line_str = full_trace[:full_trace.find(',')]

    in_ = full_trace.find(' ') + 4
    full_trace = full_trace[in_:]
    in_str = full_trace[:full_trace.find('\n')]

    print()
    print("Error ", Fore.RED + f"#{error_timestamp}", ':', sep='')
    print(Fore.BLUE + "TIME:", Fore.LIGHTBLACK_EX + datetime.fromtimestamp(unix_timestamp).strftime('%X'))
    print(Fore.GREEN + "NAME:", Fore.LIGHTBLACK_EX + get_full_class_error_name(e))
    print(Fore.YELLOW + "FILE:", Fore.LIGHTBLACK_EX + file_str.replace(fr'{environ['LOCALAPPDATA']}\Programs\Python\Python313\Lib', '%pyBIN%'))
    print(Fore.YELLOW + "LINE:", Fore.LIGHTBLACK_EX + line_str)
    print(Fore.YELLOW + "IN:  ", Fore.LIGHTBLACK_EX + in_str)
    print()


def get_full_class_error_name(obj: Exception):
    module = obj.__class__.__module__
    if module is None or module == str.__class__.__module__:
        return obj.__class__.__name__
    return module + '.' + obj.__class__.__name__
