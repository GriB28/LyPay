import sqlite3
from os import getcwd as cwd, mkdir, listdir, startfile, getenv
from psutil import process_iter, AccessDenied as psutil_AccessDenied
from os.path import exists
from dotenv import load_dotenv
from webbrowser import open as w_open
from time import time as unix, sleep
from datetime import datetime
from colorama import Fore as F, Style as S, init as c_init, just_fix_windows_console

from data import config as cfg
from data.txt import EXE as txt_EXE
from scripts import j2, firewall3, lpsql, exelink

c_init(autoreset=True)
just_fix_windows_console()


class Launcher:
    """
    Лаунчер LyPay

    help -- страница помощи

    search <text_string> [-user] [-store] [-message] [-log] -- поиск элементов
    <text_string>: текстовый аргумент без новых строк для поиска
    ключ -user: поиск по базе данных пользователей
    ключ -user: поиск по базе данных магазинов
    ключ -message: поиск по сохранённым сообщениям
    ключ -log: поиск по сохранённым логам (включает поиск по сообщениям)

    logs [-read <file_name>] [-save <file_name>]
    -read <file_name> -- прочтение сохранённых логов
    @local = cwd()
    @logs = cwd() -> ../logs
    -save <file_name> -- назначение файла для следующей записи
    -reset -- сброс названия файла до значения по умолчанию (lypay_%d-%m-%Y_%H-%M.log)

    open <file_name> -- открывает файл
    @local = cwd()
    @logs = cwd() -> ../logs

    start <script_name> -- запускает скрипт
    варианты: main, bot, lpaa, admin, executor, exe, lpsb, stores, every, everything
    """
    def __init__(self):
        self.commands = {
            'exit':      [''],
            'help':      [''],
            'search':    ['-user <query>', '-store <query>', '-sql <sql-query>'],
            'start':     ['main', 'executor', 'admin', 'stores', 'everything'],
            'launch':    [''],
            'stats':     ['-agent <ID>', '-store <ID>'],
            'open':      [''],
            'log':       ['-read ...', '-save ...', '-reset'],
            'settings':  ['set', 'read', 'current', 'update'],
            'unix':      ['now', '-difference <u1> <u2>', '-add <u1> <u2>', '-seconds <u>'],
            'balance':   ['<key> <operator> <amount>'],
            'firewall3': ['<bot> -read <ID>', '<bot> -addw <ID> [...]', '<bot> -removew <ID>', '<bot> -addb <ID> [...]',
                          '<bot> -removeb <ID>', '<bot> -open', '<bot> -close', '<bot> -list'],
            'auction_transfer': ['<store> <amount>'],
            'auction_read':     [''],
            'auction_remove':   ['<amount [abs]>'],
            'off':              ['main', 'executor', 'admin', 'stores', 'everything'],
            'shutdown':         [''],
            'extra':            ['-store <hostID> [<ID>]', '-user <ID> <tag> <name>_<surname> <class> <email>'],
            'heartbeat':        [''],
            'config':           ['-update']
        }
        self.settings_array = j2.fromfile(cfg.PATHS.LAUNCH_SETTINGS)
        if self.settings_array["launch"]:
            exelink.warn(
                text=txt_EXE.ALERTS.LAUNCH_EXIT_FAIL_DETECTED,
                userID=-1
            )
            exelink.message(
                bot='LPAA',
                text=' ',
                file_path=cfg.MEDIA.SERVER_DOWN,
                file_mode='sticker',
                participantID=cfg.WARNING_GROUP,
                userID=-1
            )
        self.last_error, self.last_success = None, None

        print(F.LIGHTBLACK_EX + S.BRIGHT + "Filling config.PATHS...", end=' ')
        created_dirs = 0
        for path in cfg.PATHS.all:
            if not exists(path) and path[path.find(cwd()) + 1 + len(cwd()):].count('.') == 0:
                mkdir(path)
                if created_dirs == 0:
                    print(F.LIGHTYELLOW_EX + "missing directory(-ies) found")
                print(F.LIGHTBLACK_EX + f"> created '{path}'")
                created_dirs += 1
        if created_dirs == 0:
            print(F.LIGHTGREEN_EX + "OK")

        print(F.LIGHTBLACK_EX + S.BRIGHT + "Checking the main database...", end=' ')
        try:
            length = len(lpsql.searchall("users", "ID"))
            print(F.LIGHTGREEN_EX + f"{length} user{'s' if length > 1 else ''} found")
        except Exception as e:
            if "lypay_database.db" not in listdir(cwd() + "database"):
                print(F.LIGHTRED_EX + "NOT FOUND")
            else:
                print(F.LIGHTRED_EX + "UNKNOWN ERROR")
                print(F.LIGHTBLACK_EX + S.BRIGHT + f" > {e.args}")
            input(F.LIGHTBLACK_EX + S.BRIGHT + "> press 'enter' to exit <")
            exit()

        print(F.LIGHTBLACK_EX + S.BRIGHT + "Auction compatibility check...", end=' ')
        if lpsql.searchall("stores", "ID").count("auction_transfer_route") == 0:
            lpsql.insert("stores", [
                "auction_transfer_route",       # ID
                "Покупка лотов аукциона",       # name
                0,                              # hostID
                "auction_transfer_route",       # description
                False,                          # logo
                0,                              # balance
                None,                           # hostEmail
                0,                              # auctionID
                None                            # placeID
            ])
            print(F.LIGHTYELLOW_EX + S.NORMAL + "CREATED")
        else:
            print(F.LIGHTGREEN_EX + S.NORMAL + "OK")

        print(F.LIGHTBLACK_EX + S.BRIGHT + "Reading .env config...", end=' ')
        found = load_dotenv()
        if not found:
            print(F.LIGHTRED_EX + "FAILED")
            print(F.LIGHTBLACK_EX + S.BRIGHT + " > trying to find system ENV variables...", end=' ')
            loaded_env = {
                getenv("LYPAY_MAIN_TOKEN"),
                getenv("LYPAY_STORES_TOKEN"),
                getenv("LYPAY_ADMINS_TOKEN"),
                getenv("LYPAY_EMAIL_MAIL"),
                getenv("LYPAY_EMAIL_HOST"),
                getenv("LYPAY_EMAIL_PORT"),
                getenv("LYPAY_EMAIL_PASSWORD"),
                getenv("LYPAY_INTEGRATION_BRIDGE_JWT"),
                getenv("LYPAY_INTEGRATION_BRIDGE_HOST"),
                getenv("LYPAY_INTEGRATION_BOT_TAG")
            }
            if None in loaded_env:
                print(F.LIGHTRED_EX + "FAILED", "Please, check the root directory and manually configure .env, then restart", sep='\n')
                input(F.LIGHTBLACK_EX + S.BRIGHT + "> press 'enter' to exit <")
                exit()
            else:
                print(F.LIGHTGREEN_EX + "OK")
        else:
            print(F.LIGHTGREEN_EX + "DONE")

        print(F.LIGHTBLACK_EX + S.BRIGHT + "Last launch...", end=' ')
        unix_delta = round(unix()) - self.settings_array["last_launch"]
        time_delta_s = unix_delta % 60
        time_delta_m = unix_delta // 60 % 60
        time_delta_h = unix_delta // 60 // 60 % 24
        time_delta_d = unix_delta // 60 // 60 // 24
        time_string = f"{time_delta_d}:" if time_delta_d > 0 else ''
        time_string += f"{time_delta_h:02d}:" + f"{time_delta_m:02d}:" + f"{time_delta_s:02d} ago"
        print(
            (F.LIGHTRED_EX if time_delta_d > 1 else F.LIGHTBLACK_EX) + time_string,
            end=(F.LIGHTBLACK_EX + "\n > " + F.YELLOW + "recommend to use '" +
                 F.LIGHTYELLOW_EX + "settings set update_names true" +
                 F.YELLOW + "'\n") if time_delta_d > 1 else '\n'
        )

        self.firewalls = {
            "main": firewall3.FireWall('MAIN', silent=True),
            "lpaa": firewall3.FireWall('LPAA', silent=True),
            "lpsb": firewall3.FireWall('LPSB', silent=True)
        }
        self.update_settings("launch", True)

    def close(self):
        self.update_settings("last_launch", int(unix()))
        self.update_settings("launch", False)

    def update_settings(self, key: str, value: ...) -> int:
        '''
        :param key: имя настройки для изменения
        :param value: новое значение
        :return: -1, если произошла ошибка. 0, если новое значение не совпадает по типу со старым. 1, если успешно заменено.
        '''
        try:
            if type(value) is type(self.settings_array[key]) or value is None or self.settings_array[key] is None:
                self.settings_array[key] = value
                with open(cfg.PATHS.LAUNCH_SETTINGS, 'w', encoding='utf8') as f:
                    f.write(j2.to_(self.settings_array))
                return 1
            return 0
        except:
            return -1

    def error_handle(self, command: str, info: str, text: str = "") -> None:
        if len(text) > 0:
            print(S.BRIGHT + F.RED + f"[{command}]" + F.LIGHTRED_EX + f"({info}): {text}")
        else:
            print(S.BRIGHT + F.RED + f"[{command}]" + F.LIGHTRED_EX + f"({info})")
        self.last_error = command

    def success_handle(self, command: str, info: str, text: str = "") -> None:
        if len(text) > 0:
            print(S.DIM + F.GREEN + f"[{command}]" + F.LIGHTBLACK_EX + f"({info}): {text}")
        else:
            print(S.DIM + F.GREEN + f"[{command}]" + F.LIGHTBLACK_EX + f"({info})")
        self.last_success = command

    def help(self):
        print(F.LIGHTBLACK_EX + S.BRIGHT + "HELP page")
        print(F.LIGHTBLUE_EX + "Available commands:")
        for command in self.commands.keys():
            print(F.YELLOW + command, end='')
            print(': ', end='')
            print(F.GREEN + ', '.join(self.commands[command]))

    def firewall(self, *args):
        if args[0] == 'help':
            # todo: help page
            pass
        elif len(args) == 2:
            command = args[1]
            try:
                if command == '-open':
                    self.firewalls[args[0]].open_public()
                    self.success_handle("firewall3.open_public", "Success")
                elif command == '-close':
                    self.firewalls[args[0]].close_public()
                    self.success_handle("firewall3.close_public", "Success")
                elif command == '-list':
                    print('whitelist:', self.firewalls[args[0]].list_white())
                    print('blacklist:', self.firewalls[args[0]].list_black())
                else:
                    self.error_handle("firewall3.argument", "ArgumentError", f"Can't parse arguments {args}")
            except Exception:
                self.error_handle("firewall3.argument", "KeyError", f"Bad bot name: {args[0]}")
        elif len(args) >= 3:
            command = args[1]
            if len(args) > 3:
                comment = ' '.join(args[3:])
            else:
                comment = ''
            if command == '-addw':
                self.firewalls[args[0]].add_white(args[2], comment)
                self.success_handle("firewall3.add_white", "Success")
            elif command == '-removew':
                self.firewalls[args[0]].remove_white(args[2])
                self.success_handle("firewall3.remove_white", "Success")
            elif command == '-addb':
                self.firewalls[args[0]].add_black(args[2], comment)
                self.success_handle("firewall3.add_black", "Success")
            elif command == '-removeb':
                self.firewalls[args[0]].remove_black(args[2])
                self.success_handle("firewall3.remove_black", "Success")
            elif command == '-read':
                print(F.YELLOW + S.NORMAL + self.firewalls[args[0]].read(args[2]))
                self.success_handle("firewall3.read", "Success")
            else:
                self.error_handle("firewall3.argument", "ArgumentError", f"Can't parse arguments {args}")

    def statistics(self, *args):
        if args[0] == 'help':
            # todo: help page
            pass
        elif args[0] == '-global':
            total = 0
            print("WORK IS STILL IN PROGRESS")
            '''for agent in [file for file in listdir(cfg.PATHS.STATISTICS) if file[-5:] == 'agent']:
                with open(cfg.PATHS.STATISTICS + agent, encoding='utf8') as f:
                    read_ = f.readlines()
                print(F.CYAN + S.NORMAL + f"{read_[0]}", end='')
                sum_ = sum([int(line.split(': ')[1].replace('\n', '')) for line in read_[1:]])
                total += sum_
                print(F.CYAN + S.NORMAL + f"- total: {sum_} {cfg.VALUTA.SHORT}")
                print(F.CYAN + S.NORMAL + f"- average: {round(sum_ / (unix() - float(read_[1].split(': ')[0])), 3)} {cfg.VALUTA.SHORT}")
            print(F.YELLOW + S.BRIGHT + "Total amount through agents:", total, cfg.VALUTA.SHORT)'''

            total_stores = dict()
            for cheque in listdir(cfg.PATHS.STORES_CHEQUES):
                store_ = cheque.split('_')[1]
                js_ = j2.fromfile(cfg.PATHS.STORES_CHEQUES + cheque)
                if js_["status"]:
                    if store_ not in total_stores.keys():
                        total_stores[store_] = [dict(), 0]
                    for i in range(len(js_["items"])):
                        item_ = js_["items"][i]["text"]
                        multy_ = js_["multipliers"][i]
                        price_ = js_["items"][i]["price"]

                        if item_ not in total_stores[store_][0].keys():
                            total_stores[store_][0][item_] = 0
                        total_stores[store_][0][item_] += multy_
                        total_stores[store_][1] += multy_ * price_

            total_stores = dict(sorted(total_stores.items(), key=lambda item: item[1][1]))

            for key, value in total_stores.items():
                print(F.GREEN + S.NORMAL + key + ':')
                print(F.YELLOW + S.DIM + '- cheques total*:', value[1], cfg.VALUTA.SHORT)
                for item_key, item_value in value[0].items():
                    print(F.LIGHTBLACK_EX + S.BRIGHT + item_key + f': {item_value}')

            print(F.YELLOW + S.BRIGHT + "Total amount through stores:", sum(t[1] for t in total_stores.values()), cfg.VALUTA.SHORT)
        elif len(args) > 1:
            if args[0] == '-agent':
                try:
                    print("WORK IS IN PROGRESS")
                    '''with open(cfg.PATHS.STATISTICS + f"{args[1]}.agent", encoding='utf8') as f:
                        read_ = f.readlines()
                    print(F.CYAN + S.NORMAL + f"{read_[0]}", end='')
                    sum_ = sum([int(line.split(': ')[1].replace('\n', '')) for line in read_[1:]])
                    print(F.CYAN + S.NORMAL + f"- total: {sum_} {cfg.VALUTA.SHORT}")
                    print(
                        F.CYAN + S.NORMAL + f"- average: {round(sum_ / (unix() - float(read_[1].split(': ')[0])), 3)} {cfg.VALUTA.SHORT}")'''
                except:
                    self.error_handle("statistics.agent", "FileNotFound", f"File '{args[1]}.agent' wasn't found!")
            elif args[0] == '-store':
                items = dict()
                balance = 0
                for cheque in listdir(cfg.PATHS.STORES_CHEQUES):
                    store_ = cheque.split('_')[1]
                    if store_ == args[1]:
                        js_ = j2.fromfile(cfg.PATHS.STORES_CHEQUES + cheque)
                        if js_["status"]:
                            for i in range(len(js_["items"])):
                                item_ = js_["items"][i]["text"]
                                multy_ = js_["multipliers"][i]
                                price_ = js_["items"][i]["price"]

                                if item_ not in items.keys():
                                    items[item_] = 0
                                items[item_] += multy_
                                balance += multy_ * price_
                print(F.YELLOW + S.DIM + '- cheques total*:', balance, cfg.VALUTA.SHORT)
                print(F.YELLOW + S.DIM + '- items:')
                for item_key, item_value in items.items():
                    print('   ', F.LIGHTBLACK_EX + S.BRIGHT + item_key + f': {item_value}')
            else:
                self.error_handle("statistics.argument", "ArgumentError", f"Can't identify argument: '{args[0]}'")
        else:
            self.error_handle("statistics.argument", "ArgumentError", f"Program can't parse argument(s): '{args}'")

    def search(self, *args):
        if args[0] == 'help':
            # todo: help page
            pass
        else:
            mode = args[0]
            query = ' '.join(list(map(lambda s: s.strip(), list(args[1:]))))
            found = False

            if mode == "-user":
                for id_ in lpsql.searchall("users", "ID"):
                    js_ = lpsql.search("users", "ID", id_)
                    if sum([query in str(v).lower() for v in js_.values()]) or query == str(id_):
                        found = True
                        print(f"User #{id_}:")
                        for key, value in js_.items():
                            key_c = key.lower()
                            value_c = str(value).lower()
                            if query not in key_c and query not in value_c:
                                print(f"- {key}: {value}")
                            elif query in key_c:
                                print("- " + F.GREEN + S.BRIGHT + f"{key}", f": {value}", sep='')
                            else:
                                print(f"- {key}: " + F.GREEN + S.BRIGHT + f"{value}", sep='')
                        print()
                if not found:
                    print("Nothing found!\n")

            elif mode == "-store":
                for id_ in lpsql.searchall("stores", "ID"):
                    js_ = lpsql.search("stores", "ID", id_)
                    if sum([query in str(v).lower() for v in js_.values()]) or query == id_:
                        found = True
                        print(f"Store #{id_}:")
                        for key, value in js_.items():
                            key_c = key.lower()
                            value_c = str(value).lower()
                            if query not in key_c and query not in value_c:
                                print(f"- {key}: {value}")
                            elif query in key_c:
                                print("- " + F.GREEN + S.BRIGHT + f"{key}", f": {value}", sep='')
                            else:
                                print(f"- {key}: " + F.GREEN + S.BRIGHT + f"{value}", sep='')
                        if not exists(cfg.PATHS.STORES_KEYBOARDS + id_):
                            return
                        print("- items:")
                        for item in listdir(cfg.PATHS.STORES_KEYBOARDS + id_):
                            js_ = j2.fromfile(cfg.PATHS.STORES_KEYBOARDS + id_ + '/' + item)
                            for key, value in js_.items():
                                key_c = key.lower()
                                value_c = str(value).lower()
                                if query not in key_c and query not in value_c:
                                    print(f"  - {key}: {value}")
                                elif query in key_c:
                                    print("  - " + F.GREEN + S.BRIGHT + f"{key}", f": {value}", sep='')
                                else:
                                    print(f"  - {key}: " + F.GREEN + S.BRIGHT + f"{value}", sep='')
                            print()
                        print()
                if not found:
                    print("Nothing found!\n")

            elif mode == "-sql":
                self.sql(query)

            else:
                query = mode + ' ' + query
                query = query.strip()
                print(query)
                for id_ in lpsql.searchall("users", "ID"):
                    js_ = lpsql.search("users", "ID", id_)
                    if sum([query in str(v).lower() for v in js_.values()]) or query == str(id_):
                        found = True
                        print(f"User #{id_}:")
                        for key, value in js_.items():
                            key_c = key.lower()
                            value_c = str(value).lower()
                            if query not in key_c and query not in value_c:
                                print(f"- {key}: {value}")
                            elif query in key_c:
                                print("- " + F.GREEN + S.BRIGHT + f"{key}", f": {value}", sep='')
                            else:
                                print(f"- {key}: " + F.GREEN + S.BRIGHT + f"{value}", sep='')
                        print()
                for id_ in lpsql.searchall("stores", "ID"):
                    js_ = lpsql.search("stores", "ID", id_)
                    if sum([query in str(v).lower() for v in js_.values()]) or query == id_:
                        found = True
                        print(f"Store #{id_}:")
                        for key, value in js_.items():
                            key_c = key.lower()
                            value_c = str(value).lower()
                            if query not in key_c and query not in value_c:
                                print(f"- {key}: {value}")
                            elif query in key_c:
                                print("- " + F.GREEN + S.BRIGHT + f"{key}", f": {value}", sep='')
                            else:
                                print(f"- {key}: " + F.GREEN + S.BRIGHT + f"{value}", sep='')
                        if not exists(cfg.PATHS.STORES_KEYBOARDS + id_):
                            return
                        print("- items:")
                        for item in listdir(cfg.PATHS.STORES_KEYBOARDS + id_):
                            js_ = j2.fromfile(cfg.PATHS.STORES_KEYBOARDS + id_ + '/' + item)
                            for key, value in js_.items():
                                key_c = key.lower()
                                value_c = str(value).lower()
                                if query not in key_c and query not in value_c:
                                    print(f"  - {key}: {value}")
                                elif query in key_c:
                                    print("  - " + F.GREEN + S.BRIGHT + f"{key}", f": {value}", sep='')
                                else:
                                    print(f"  - {key}: " + F.GREEN + S.BRIGHT + f"{value}", sep='')
                            print()
                        print()
                if not found:
                    print("Nothing found!\n")
                    self.error_handle("search.nothing", "NothingFound")
                else:
                    self.success_handle("search.found", "Successfully")

    # async
    def balance(self, *args):
        self.error_handle("command.outdated", "Outdated", "Sorry, this command is inaccessible from v1.4.1")

    # async
    def auction_transfer(self, *args):
        self.error_handle("command.outdated", "Outdated", "Sorry, this command is inaccessible from v1.4.1")

    # async
    def auction_read(self, *args):
        self.error_handle("command.outdated", "Outdated", "Sorry, this command is inaccessible from v1.4.1")

    # async
    def auction_remove(self, *args):
        self.error_handle("command.outdated", "Outdated", "Sorry, this command is inaccessible from v1.4.1")

    def logs(self, *args):
        self.error_handle("command.outdated", "Outdated", "Sorry, this command is inaccessible from v1.3")

    def open(self, *args):
        if args[0] == 'help':
            # todo: help page
            pass
        else:
            path = args[0].replace('@local', cwd()).replace('@exe', cfg.PATHS.EXE).replace('/', '\\')
            if exists(path):
                w_open(path)
                self.success_handle("open.open", f"Successfully opened {args[0]}")
            else:
                self.error_handle("open.argument", "RequestNotExist", f"There is no file or directory at '{path}'!")

    def start(self, *args, silent: bool = False) -> bool:
        if args[0] == 'help':
            # todo: help page
            return False
        else:
            launch_setup = """
@ECHO ON
chcp 65001 > NUL
cd /d "%~dp0"
"""
            if args[0] == 'main' or args[0] == 'bot':
                launch_setup += f'start "LyPay: main" cmd /c python main.py lypay_{cfg.VERSION}_launch_stamp'

            elif args[0] == 'executor' or args[0] == 'exe':
                launch_setup += f'start "LyPay: exe" cmd /c python executor.py lypay_{cfg.VERSION}_launch_stamp'

            elif args[0] == 'stores' or args[0] == 'store' or args[0] == 'lpsb':
                launch_setup += f'start "LyPay: stores" cmd /c python stores.py lypay_{cfg.VERSION}_launch_stamp'

            elif args[0] == 'admins' or args[0] == 'admin' or args[0] == 'lpaa':
                launch_setup += f'start "LyPay: admins" cmd /c python admins.py lypay_{cfg.VERSION}_launch_stamp'

            elif args[0] == 'every' or args[0] == 'everything' or args[0] == 'all':
                launch_setup += f"""
start "LyPay: main" cmd /c python main.py lypay_{cfg.VERSION}_launch_stamp
start "LyPay: exe" cmd /c python executor.py lypay_{cfg.VERSION}_launch_stamp
start "LyPay: admins" cmd /c python admins.py lypay_{cfg.VERSION}_launch_stamp
start "LyPay: stores" cmd /c python stores.py lypay_{cfg.VERSION}_launch_stamp
"""

            else:
                self.error_handle("start.argument", "ArgumentError",
                                  f"There is no argument '{args[1]}' associated with 'open'!")
                return False

            launch_setup += """
del /s /q %0 > NUL
exit
"""
            with open("launch.bat", 'w', encoding='utf8') as f:
                f.write(launch_setup)
            sleep(self.settings_array["launch_timeout"])
            startfile("launch.bat")
            if not silent:
                self.success_handle("start.instance", f"Successfully started: {args[0]}")
            return True

    def off(self, *args, silent: bool = False) -> bool:
        try:
            if args[0] == 'help':
                # todo: help page
                pass

            elif args[0] == 'main' or args[0] == 'bot':
                for process in process_iter():
                    if process.name() == "python.exe" and len(process.cmdline()) > 0 and process.cmdline()[1:] == ['main.py', f'lypay_{cfg.VERSION}_launch_stamp']:
                        process.kill()
                        if not silent:
                            self.success_handle("off.instance", f"Successfully turned off: {args[0]}")
                        break

            elif args[0] == 'executor' or args[0] == 'exe':
                for process in process_iter():
                    if process.name() == "python.exe" and len(process.cmdline()) > 0 and process.cmdline()[1:] == ['executor.py', f'lypay_{cfg.VERSION}_launch_stamp']:
                        process.kill()
                        if not silent:
                            self.success_handle("off.instance", f"Successfully turned off: {args[0]}")
                        break

            elif args[0] == 'stores' or args[0] == 'store' or args[0] == 'lpsb':
                for process in process_iter():
                    if process.name() == "python.exe" and len(process.cmdline()) > 0 and process.cmdline()[1:] == ['stores.py', f'lypay_{cfg.VERSION}_launch_stamp']:
                        process.kill()
                        if not silent:
                            self.success_handle("off.instance", f"Successfully turned off: {args[0]}")
                        break

            elif args[0] == 'admins' or args[0] == 'admin' or args[0] == 'lpaa':
                for process in process_iter():
                    if process.name() == "python.exe" and len(process.cmdline()) > 0 and process.cmdline()[1:] == ['admins.py', f'lypay_{cfg.VERSION}_launch_stamp']:
                        process.kill()
                        if not silent:
                            self.success_handle("off.instance", f"Successfully turned off: {args[0]}")
                        break

            elif args[0] == 'every' or args[0] == 'everything' or args[0] == 'all':
                for process in process_iter():
                    if process.name() == "python.exe" and len(process.cmdline()) > 0 and process.cmdline()[-1] == f'lypay_{cfg.VERSION}_launch_stamp':
                        process.kill()
                if not silent:
                    self.success_handle("off.instance", f"Successfully turned off: {args[0]}")

            else:
                self.error_handle("off.argument", "ArgumentError", f"There is no argument '{args[0]}' associated with 'off'!")
                return False
            return True
        except psutil_AccessDenied:
            self.error_handle("off.process", "AccessDenied", f"Can't find running '{args[0]}'! Access to core process pid=0: denied.")
            return False

    def restart(self, *args):
        if args[0] == 'help':
            # todo: help page
            pass
        elif args[0] in ('main', 'lpaa', 'admin', 'admins', 'lpsb', 'stores', 'store', 'exe', 'every', 'everything', 'all'):
            off_ok = self.off(*args, silent=True)
            start_ok = self.start(*args, silent=True)
            if off_ok and start_ok:
                self.success_handle("restart.instance", f"Successfully restarted: {args[0]}")
        else:
            self.error_handle("restart.argument", "ArgumentError", f"There is no argument '{args[0]}' associated with 'off'!")

    def settings(self, *args):
        if args[0] == 'help':
            # todo help page
            pass
        elif args[0] == 'current' or args[0] == 'curr' or args[0] == 'c':
            print(j2.to_(self.settings_array).replace('\n\t"', '\n  "'))
        elif args[0] == 'read' or args[0] == 'r':
            print(j2.to_(j2.fromfile(cfg.PATHS.LAUNCH_SETTINGS)).replace('\n\t"', '\n  "'))
        elif args[0] == 'set':
            current = j2.fromfile(cfg.PATHS.LAUNCH_SETTINGS)
            try:
                if args[1] in current.keys():
                    value = ' '.join(args[2:])
                    if value == 'false':
                        c = False
                    elif value == 'true':
                        c = True
                    elif value == 'none' or value == 'null':
                        c = None
                    else:
                        try:
                            c = int(value)
                        except:
                            try:
                                c = eval(value)
                            except:
                                self.error_handle("settings.set.-1", "ParseError", f"Can't parse '{value}'")
                                return

                    upd = self.update_settings(args[1], c)
                    if upd == 1:
                        self.success_handle("settings.set.1", "Success")
                        if args[1] == 'auction':
                            print(F.YELLOW + S.BRIGHT + "Don't forget to update LPSB's avatar and name!")
                    elif upd == -1:
                        self.error_handle("settings.set.-1", "KeyError", f"Type of the new value must be {type(self.settings_array[args[1]])}")
                    else:
                        self.error_handle("settings.set.0", "ValueError", f"Type of the new value must be {type(self.settings_array[args[1]])}")
                else:
                    self.error_handle("settings.notFound", "SettingError", f"There is no setting '{args[1]}'!")
            except IndexError:
                self.error_handle("settings.argument", "ArgumentError", "You need to specify an argument for this command!")
        elif args[0] == 'update':
            self.settings_array = j2.fromfile(cfg.PATHS.LAUNCH_SETTINGS)
            self.success_handle("settings.update", "Success")
        else:
            self.error_handle("settings.argument", "ArgumentError", f"There is no argument '{args[0]}' associated with 'settings'!")

    def unix(self, *args):
        if args[0] == 'help':
            # todo help page
            pass
        elif args[0].replace('.', '').isnumeric():
            try:
                print(F.LIGHTGREEN_EX + S.DIM + datetime.fromtimestamp(float(args[0])).strftime('%d.%m.%Y, %X'))
            except Exception:
                self.error_handle("unix.value", "ValueError", f"Can't create float from '{args[0]}'")
        elif args[0] == "now" or args[0] == "n":
            print(F.LIGHTGREEN_EX + S.DIM + f"{round(unix(), 2)}")
        elif args[0] == "-diff" or args[0] == "-difference" or args[0] == "-d":
            try:
                a1 = args[1]
                a2 = args[2]
                try:
                    d1 = datetime.fromtimestamp(float(a1))
                    try:
                        d2 = datetime.fromtimestamp(float(a2))
                        print(F.LIGHTGREEN_EX + S.DIM + f"{d2.second - d1.second} s")
                    except ValueError:
                        self.error_handle("unix.value", "ValueError", f"Can't create float from '{args[2]}'")
                except ValueError:
                    self.error_handle("unix.value", "ValueError", f"Can't create float from '{args[1]}'")
            except IndexError:
                self.error_handle("unix.argument", "ArgumentError", "You need to specify 2 arguments for this command!")
        elif args[0] == "-add" or args[0] == "-a":
            try:
                a1 = args[1]
                a2 = args[2]
                try:
                    d1 = datetime.fromtimestamp(float(a1))
                    try:
                        d2 = datetime.fromtimestamp(float(a2))
                        print(F.LIGHTGREEN_EX + S.DIM + f"{d1.second + d2.second} s")
                    except ValueError:
                        self.error_handle("unix.value", "ValueError", f"Can't create float from '{args[2]}'")
                except ValueError:
                    self.error_handle("unix.value", "ValueError", f"Can't create float from '{args[1]}'")
            except IndexError:
                self.error_handle("unix.argument", "ArgumentError", "You need to specify 2 arguments for this command!")

        elif args[0] == "-seconds" or args[0] == "-second" or args[0] == "-s":
            try:
                seconds = float(args[1])
                minutes = seconds // 60
                seconds %= 60
                hours = minutes // 60
                minutes %= 60
                days = hours // 24
                hours %= 24
                print(F.LIGHTGREEN_EX + S.DIM + f"{days}d {hours}h {minutes}m {seconds}s")
            except IndexError:
                self.error_handle("unix.argument", "ArgumentError", "You need to specify an argument for this command!")
            except ValueError:
                self.error_handle("unix.value", "ValueError", f"Can't create float from '{args[1]}'")
        else:
            self.error_handle("unix.argument", "ArgumentError", f"There is no argument '{args[0]}' associated with 'unix'!")

    def sql(self, arg: str):
        try:
            print(arg)
            query = lpsql.manual(arg)
            if len(query) > 0:
                query = list(map(lambda item: list(map(str, item)), query))
                max_seps = [0] * len(query[0])
                for line in query:
                    for i in range(len(line)):
                        if len(line[i]) > max_seps[i]:
                            max_seps[i] = len(line[i])

                for line in query:
                    for i in range(len(line)):
                        print(line[i], end=' ' * (max_seps[i] + 3 - len(line[i])))
                    print()
        except sqlite3.Error as e:
            self.error_handle("search.sql", "sqlite3Error", e.__str__())
        except Exception as e:
            if self.settings_array["show_unknown_errors"]:
                self.error_handle("search.sql", "Unknown", "Unknown error: " + e.__str__())

    def extra(self, *args):
        if args[0] == 'help':
            # todo help page
            pass
        if len(args) > 1:
            if args[0] == '-store':
                try:
                    hostID = args[1]
                    last_index = len([store for store in lpsql.searchall("stores", "ID") if store[0] == 'i'])
                    try:
                        storeID = args[2]
                    except IndexError:
                        storeID = f"i{str(last_index+1).zfill(2)}"

                    self.firewalls["lpsb"].add_white(hostID, "added via extra command")
                    lpsql.insert(
                        "stores",
                        [
                            storeID,                                                    # ID
                            storeID,                                                    # name
                            hostID,                                                     # hostID
                            f"generated by Launcher Extra at {round(unix(), 2)}",       # description
                            False,                                                      # logo
                            0,                                                          # balance
                            None,                                                       # hostEmail
                            None,                                                       # auctionID
                            None                                                        # placeID
                        ]
                    )
                    lpsql.insert(
                        "shopkeepers",
                        [
                            hostID,  # userID
                            storeID  # storeID
                        ]
                    )
                    lpsql.insert(
                        "logotypes",
                        [
                            storeID,    # storeID
                            None,       # fileID_main
                            None        # fileID_lpsb
                        ]
                    )
                    self.success_handle("extra.store", "Successfully added a store")
                except:
                    self.error_handle("extra.argument", "ArgumentError", f"Can't parse the following arguments: {args[1:]}")
            elif args[0] == '-user':
                try:
                    userID = args[1]
                    tag = args[2]
                    name = args[3].replace('_', ' ')
                    group = args[4]
                    email = args[5]

                    lpsql.insert("users",
                                 [
                                     userID,    # ID
                                     name,      # name
                                     group,     # class
                                     email,     # email
                                     tag,       # tag
                                     0,         # balance
                                     1          # owner
                                 ])
                    if not exists(cfg.PATHS.QR + f"{userID}.png"):
                        exelink.add(f"qr {userID}", 0)
                        lpsql.insert("qr",
                                     [
                                         userID,    # userID
                                         None,      # fileID_main
                                         None,      # fileID_lpsb
                                         None       # fileID_lpaa
                                     ])

                    self.success_handle("extra.user", "Successfully added a user")
                except:
                    self.error_handle("extra.argument", "ArgumentError", f"Can't parse the following arguments: {args[1:]}")

            else:
                self.error_handle("extra.argument", "ArgumentError", f"There is no argument '{args[0]}' associated with 'extra'!")
        else:
            self.error_handle("extra.argument", "ArgumentError", f"You have to assiciate more than 1 argument! Look here for more info: " + F.YELLOW + "help")

    def heartbeat(self):
        with open("heartbeat.bat", 'w') as launch_file:
            launch_file.write(r"""
@ECHO OFF
chcp 65001 > NUL
cd /d "%~dp0"
start "LyPay Heartbeat" /min cmd /c bokeh serve --show source\SRV\plots.py
del /s /q %0 > NUL
exit
""")
        sleep(self.settings_array["launch_timeout"])
        startfile("heartbeat.cmd")
        self.success_handle("heartbeat.launch", "Successfully started measuring")

    def config(self, *args):
        if args[0] == 'help':
            # todo help page
            pass
        elif args[0] == '-update':
            if len(args) > 1:
                n = int(args[1])
            else:
                n = self.settings_array["config_v"] + 1
            self.update_settings("config_v", n)
            self.success_handle("config.update", "Successfully updated current snapshot")
        else:
            query = args[0].upper()
            try:
                print(F.YELLOW + S.DIM + eval(f"cfg.{query}"))
                self.success_handle("config.print", "Successfully found config data")
            except:
                self.error_handle("config.argument", "NotFound", f"Can't find {query} in current config!")


# -=-=-=-

launcher = Launcher()
auto_restart = launcher.settings_array["auto_restart_cmd"]
if auto_restart is not None:
    cmd_not_lowered = auto_restart.strip().split()
    cmd = list(map(lambda s: s.lower(), cmd_not_lowered))
    print()
    print(F.LIGHTBLUE_EX + "Autorestart event", "has been triggered with following argument:")
    print(F.YELLOW + ">>> " + ' '.join(cmd_not_lowered))
else:
    cmd_not_lowered = ''
    cmd = list()

while True:
    if len(cmd) == 0:
        pass
    #
    elif cmd[0] == 'exit':
        break
    #
    elif cmd[0] == 'help' or cmd[0] == 'h':
        launcher.help()
    #
    elif cmd[0] == 'search' or cmd[0] == 'se':
        try:
            launcher.search(*cmd[1:])
        except IndexError:
            launcher.error_handle("search.argument", "ArgumentError", "You need to specify an argument for this command!")
    #
    elif cmd[0] == 'auction_transfer' or cmd[0] == 'auc' or cmd[0] == 'auction':
        print("[OUTDATED] Sorry, this command is no longer supported by the Launcher.")
        launcher.auction_transfer()
    #
    elif cmd[0] == 'auction_read' or cmd[0] == 'auc_read':
        print("[OUTDATED] Sorry, this command is no longer supported by the Launcher.")
        launcher.auction_read()
    #
    elif cmd[0] == 'auction_remove' or cmd[0] == 'auc_remove':
        print("[OUTDATED] Sorry, this command is no longer supported by the Launcher.")
        launcher.auction_remove()
    #
    elif cmd[0] == 'open':
        try:
            launcher.open(*cmd[1:])
        except IndexError:
            launcher.error_handle("open.argument", "ArgumentError", "You need to specify an argument for this command!")
    #
    elif cmd[0] == 'logs':
        print("[OUTDATED] Sorry, this command is no longer supported by the Launcher.")
        launcher.logs()
    #
    elif cmd[0] == 'balance':
        print("[OUTDATED] Sorry, this command is no longer supported by the Launcher.")
        launcher.balance()
    #
    elif cmd[0] == 'firewall3':
        try:
            launcher.firewall(*cmd[1:])
        except IndexError:
            launcher.error_handle("firewall3.argument", "ArgumentError", "You need to specify an argument for this command!")
    #
    elif cmd[0] == 'start' or cmd[0] == 'st':
        try:
            launcher.start(*cmd[1:])
        except IndexError:
            launcher.error_handle("start.argument", "ArgumentError", "You need to specify an argument for this command!")
    #
    elif cmd[0] == 'launch':
        launcher.start("all")
    #
    elif cmd[0] == 'off':
        try:
            launcher.off(*cmd[1:])
        except IndexError:
            launcher.error_handle("off.argument", "ArgumentError", "You need to specify an argument for this command!")
    #
    elif cmd[0] == 'shutdown':
        launcher.off("all")
    #
    elif cmd[0] == 'restart':
        try:
            launcher.restart(*cmd[1:])
        except IndexError:
            launcher.error_handle("restart.argument", "ArgumentError", "You need to specify an argument for this command!")
    #
    elif cmd[0] == 'settings':
        try:
            launcher.settings(*cmd[1:])
        except IndexError:
            launcher.error_handle("settings.argument", "ArgumentError", "You need to specify an argument for this command!")
    #
    elif cmd[0] == 'unix':
        try:
            launcher.unix(*cmd[1:])
        except IndexError:
            launcher.error_handle("unix.argument", "ArgumentError", "You need to specify an argument for this command!")
    #
    elif cmd[0] == 'statistics' or cmd[0] == 'statistic' or cmd[0] == 'stats' or cmd[0] == 'stat':
        try:
            launcher.statistics(*cmd[1:])
        except IndexError:
            launcher.error_handle("statistics.argument", "ArgumentError", "You need to specify an argument for this command!")
    #
    elif cmd[0] == 'extra':
        try:
            launcher.extra(*cmd[1:])
        except IndexError:
            launcher.error_handle("extra.argument", "ArgumentError", "You need to specify an argument for this command!")
    #
    elif cmd[0] == 'heartbeat':
        launcher.heartbeat()
    #
    elif cmd[0] == 'config':
        try:
            launcher.config(*cmd[1:])
        except IndexError:
            launcher.error_handle("config.argument", "ArgumentError", "You need to specify an argument for this command!")
    #
    elif launcher.settings_array["show_unknown_errors"]:
        launcher.error_handle("un_exp_0.argument", "KeyError", "Unknown command, try: " + F.YELLOW + "help")

    print()
    cmd_not_lowered = input(S.NORMAL + F.GREEN + ">>> " + F.LIGHTGREEN_EX).strip().split()
    cmd = list(map(lambda s: s.lower(), cmd_not_lowered))
    print(F.RESET + S.RESET_ALL, end='')

launcher.close()
