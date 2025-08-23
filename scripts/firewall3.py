from colorama import Fore as F, Style as S
from os import mkdir, listdir, remove
from os.path import exists

from data.config import PATHS
from scripts.unix import unix


class FireWall:
    BLACK_ANCHOR = "[blacklist anchor]"
    GRAY_ANCHOR = "[not in FireWall anchor]"
    WHITE_ANCHOR = "[whitelist anchor]"
    opened = "nullflag_open_whitelist"

    def __init__(self, bot: str, silent: bool = True):
        """
        :param bot название бота или буквенный код
        :param silent "бесшумный" режим - не выводит сообщение об инициализации
        """
        if not silent:
            print(F.LIGHTCYAN_EX + S.BRIGHT + f"Initializing FireWall III...", end=' ')
        bot = bot.lower()
        if bot == "main" or bot == "m":
            self.BOT = 0
            PATH = PATHS.FIREWALL_MAIN
        elif bot == "lpaa" or bot == "aa":
            self.BOT = 1
            PATH = PATHS.FIREWALL_LPAA
        elif bot == "lpsb" or bot == "sb":
            self.BOT = 2
            PATH = PATHS.FIREWALL_LPSB
        else:
            raise ValueError

        if not exists(PATH + 'W\\'):
            mkdir(PATH + 'W\\')
        if not exists(PATH + 'B\\'):
            mkdir(PATH + 'B\\')
        self.W = PATH + 'W\\'
        self.B = PATH + 'B\\'

        if exists(self.W + self.opened):
            self.freeW = True
        else:
            self.freeW = False

        if not silent:
            print(F.GREEN + S.NORMAL + "OK")

    def open_public(self):
        self.add_white(self.opened)

    def close_public(self):
        self.remove_white(self.opened)

    def check(self, uid: int | str) -> str:
        if exists(self.B + f"{uid}"):
            return self.BLACK_ANCHOR
        elif exists(self.W + f"{uid}") or self.freeW:
            return self.WHITE_ANCHOR
        else:
            return self.GRAY_ANCHOR

    def read(self, uid: int | str) -> str:
        read_b, read_w = '', ''
        if exists(self.B + f"{uid}"):
            with open(self.B + f"{uid}", encoding='utf8') as f:
                read_b = f.read()
        if exists(self.W + f"{uid}"):
            with open(self.W + f"{uid}", encoding='utf8') as f:
                read_w = f.read()

        if len(read_b) == len(read_w) == 0:
            return ''
        else:
            return f'W: {read_w}\nB: {read_b}'

    def add_white(self, uid: int | str, comment: str = '') -> None:
        if not exists(self.W + f"{uid}"):
            with open(self.W + f"{uid}", 'w', encoding='utf8') as f:
                f.write(f"{unix()}\n{comment}")

    def add_black(self, uid: int | str, comment: str = '') -> None:
        if not exists(self.B + f"{uid}"):
            with open(self.B + f"{uid}", 'w', encoding='utf8') as f:
                f.write(f"{unix()}\n{comment}")

    def remove_white(self, uid: int | str) -> None | tuple[float, str]:
        if exists(self.W + f"{uid}"):
            with open(self.W + f"{uid}", encoding='utf8') as f:
                re = f.read()
                re = re.split('\n')
                re = (float(re[0]), '\n'.join(re[1:]))
            remove(self.W + f"{uid}")
            return re
        return None

    def remove_black(self, uid: int | str) -> None | tuple[float, str]:
        if exists(self.B + f"{uid}"):
            with open(self.B + f"{uid}", encoding='utf8') as f:
                re = f.read()
                re = re.split('\n')
                re = (float(re[0]), '\n'.join(re[1:]))
            remove(self.B + f"{uid}")
            return re
        return None

    def list_white(self):
        return listdir(self.W)

    def list_black(self):
        return listdir(self.B)
