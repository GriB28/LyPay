import sqlite3 as sq
import scripts.lpsql.errors

from scripts.unix import unix
from data.config import PATHS

# v1.2a


class Tables:
    MAIN = ['users', 'stores', 'qr', 'shopkeepers', 'logotypes', 'history', 'changing', 'corporation', 'auction',
            'arttest_test1', 'arttest_test4', 'users_reformated']

    SUBLISTS = ['ads', 'ad_approving', 'arttest', 'auction_lot_control', 'ccc', 'hi_frog', 'promo', 'store_form_link']


class DataBase:
    def __init__(self, path: str, tables: list[str]):
        """
        :param path: имя файла базы данных (в директории PATHS.DB)
        :param tables: список имён таблиц в базе (можно выбрать один из списков в классе Tables)
        """
        self.tables = tables

        self.path = path.strip().lower().replace('/', '\\')
        if self.path[0] == '\\':
            self.path = self.path[1:]
        self.path = PATHS.DB + self.path

        try:
            with open(self.path) as _:
                pass
        except FileNotFoundError:
            raise errors.BaseNotFound

    def search(self, table: str, column: str, mean: str | int, quantity: bool = False) -> None | dict[str, ...] | list[dict[str, ...]]:
        """
        [UNIVERSAL]
        Функция поиска.

        Возможные ошибки: TableNotFound, sqlite3.OperationalError: no such column
        :param table: имя таблицы
        :param column: название колонки для поиска
        :param mean: цель поиска
        :param quantity: множественный поиск (по умолчанию выключен)
        :return: если множественный поиск включён, вернёт список словарей, иначе -- один словарь.
        Если записи не найдены, возвращает пустой список, если множественный поиск включён, иначе -- null
        """
        with sq.connect(self.path) as con:
            con.row_factory = sq.Row
            cur = con.cursor()
            if table in self.tables:
                cur.execute("select * from " + table + " where " + column + " = :x", {'x': mean})
                if quantity:
                    res = cur.fetchall()
                    return list(map(dict, res))
                else:
                    res = cur.fetchone()
                    return dict(res) if res is not None else None
            else:
                raise errors.TableNotFound


    def insert(self, table: str, values: list[...]):
        """
        [UNIVERSAL]
        Функция вставки данных в таблицу. Важно, чтобы количество данных совпадало с количеством колонок в таблице.

        Возможные ошибки: TableNotFound, встроенная ошибка sqlite3
        :param table: имя таблицы
        :param values: список данных, перечисленных в порядке колонок таблицы
        """
        with sq.connect(self.path) as con:
            cur = con.cursor()
            if table in self.tables:
                cur.execute("insert into " + table + " VALUES (%s)" % ','.join('?' * len(values)), values)
            else:
                raise errors.TableNotFound


    def delete(self, table: str, userid: int, storeid: str):
        """
        [MAIN DB]
        Функция удаления данных из таблиц changing и shopkeepers.

        Возможные ошибки: TableNotFound, EntryNotFound
        :param table: имя таблицы ('shopkeepers' или 'changing')
        :param userid:
        :param storeid:
        """
        with sq.connect(self.path) as con:
            cur = con.cursor()
            if table in self.tables:
                cur.execute("select * from " + table + " where userid = :x and storeid = :y", {'x': userid, 'y': storeid})
                res = cur.fetchone()
                if res is not None:
                    cur.execute("delete from " + table + " where userid = :x and storeid = :y", {'x': userid, 'y': storeid})
                else:
                    raise errors.EntryNotFound
            else:
                raise errors.TableNotFound


    def delete_user(self, userid: int):
        """
        [MAIN DB]
        Функция удаления записи о user'е из таблицы users.

        Возможные ошибки: IDNotFound
        :param userid: ID пользователя
        """
        with sq.connect(self.path) as con:
            cur = con.cursor()
            cur.execute("select * from users where id = :x", {'x': userid})
            res = cur.fetchone()
            if res is not None:
                cur.execute("delete from users where id = :x", {'x': userid})
            else:
                raise errors.IDNotFound


    def balance_view(self, id: int | str) -> int:
        """
        [MAIN DB]
        Функция просмотра баланса. Автоматически определяет тип объекта (пользователь/магазин) по типу id.

        Возможные ошибки: IDNotFound
        :param id: ID для просмотра баланса
        :return: число
        """
        with sq.connect(self.path) as con:
            con.row_factory = sq.Row
            cur = con.cursor()
            if type(id) is int:
                cur.execute("select balance from users where id = :x", {'x': id})
                res = cur.fetchone()
            else:
                cur.execute("select balance from stores where id = :x", {'x': id})
                res = cur.fetchone()
        if res is not None:
            return res['balance']
        else:
            raise errors.IDNotFound


    def deposit(self, id: int | str, value: int, agent_id: int | str | None = None):
        """
        [MAIN DB]
        Функция по зачислению денег "из воздуха". Автоматически определяет тип объекта (пользователь/магазин) по типу id.
        Имеет необязательный аргумент agentid, при наличии которого запишет транзакцию в таблицу history.

        Возможные ошибки: IDNotFound
        :param id: ID получателя
        :param value: сумма зачисления
        :param agent_id: ID агента (при `зачислении`)
        """
        with sq.connect(self.path) as con:
            cur = con.cursor()
            if type(id) is int:
                cur.execute("select * from users where id = :y", {'y': id})
                res = cur.fetchone()
                if res is not None:
                    cur.execute("update users set balance = balance + :x where id = :y", {'x': value, 'y': id})
                    if agent_id is not None:
                        cur.execute("insert into history values (:d, :x, :y, :z)",{'x': 'u' + str(id), 'y': value, 'd': 'd' + str(agent_id), 'z': unix()})
                else:
                    raise errors.IDNotFound
            else:
                cur.execute("select * from stores where id = :y", {'y': id})
                res = cur.fetchone()
                if res is not None:
                    cur.execute("update stores set balance = balance + :x where id = :y", {'x': value, 'y': id})
                    if agent_id is not None:
                        cur.execute("insert into history values (:d, :x, :y, :z)",{'x': 's' + str(id), 'y': value, 'd': 'd' + str(agent_id), 'z': unix()})
                else:
                    raise errors.IDNotFound


    def transfer(self, id_out: int | str, id_in: int | str, value: int):
        """
        [MAIN DB]
        Функция перевода денег между объектами. Автоматически определяет тип объектов (пользователь/магазин) по типу id.
        Проверяет данные на положительную сумму перевода и наличие у отправителя необходимой суммы денег на балансе. Записывает транзакцию в таблицу history.

        Возможные ошибки: SubzeroInput, NotEnoughBalance, IDNotFound
        :param id_out: ID отправителя
        :param id_in: ID получателя
        :param value: сумма перевода
        """
        with sq.connect(self.path) as con:
            con.row_factory = sq.Row
            cur = con.cursor()
            if value > 0:
                if type(id_out) is int:
                    cur.execute("select balance from users where id = :y", {'y': id_out})
                    res = cur.fetchone()
                else:
                    cur.execute("select balance from stores where id = :y", {'y': id_out})
                    res = cur.fetchone()
                if res['balance'] >= value:
                    self.deposit(id_out, 0 - value)
                    self.deposit(id_in, value)
                    cur.execute("insert into history values (:d, :x, :y, :z)",{'x': 'u' + str(id_in) if type(id_in) is int else 's' + str(id_in) , 'y': value, 'd': 'u' + str(id_out) if type(id_out) is int else 's' + str(id_out), 'z': unix()})
                else:
                    raise errors.NotEnoughBalance
            else:
                raise errors.SubzeroInput


    def searchall(self, table: str, column: str) -> list[...]:
        """
        [UNIVERSAL]
        Функция поиска всех значений определенной колонки определенной таблицы.

        Возможные ошибки: TableNotFound, sqlite3.OperationalError: no such column
        :param table: имя таблицы
        :param column: название колонки
        :return: список
        """
        with sq.connect(self.path) as con:
            con.row_factory = sq.Row
            cur = con.cursor()
            if table in self.tables:
                cur.execute("select " + column + " from " + table)
                res = cur.fetchall()
                return list(map(lambda d: d[column], res))
            else:
                raise errors.TableNotFound


    def get_table(self, table: str) -> list[dict[str, ...]]:
        """
        [UNIVERSAL]
        Функция, возвращающая всю таблицу.

        Возможные ошибки: TableNotFound
        :param table: имя таблицы
        :return: список словарей
        """
        with sq.connect(self.path) as con:
            con.row_factory = sq.Row
            cur = con.cursor()
            if table in self.tables:
                cur.execute("select * from " + table)
                res = cur.fetchall()
                return list(map(dict, res))
            else:
                raise errors.TableNotFound


    def manual(self, comm: str):
        """
        [UNIVERSAL]
        Ручное управление
        :param comm: SQL-запрос
        :return: ответ на запрос списком или None, если ничего не найдено
        """
        with sq.connect(self.path) as con:
            cur = con.cursor()
            cur.execute(comm)
            res = cur.fetchall()
            return res


    def update(self, table: str, check_column: str, check_mean: str | int, update_column: str, update_mean: str | int | None):
        """
        [UNIVERSAL]
        Обновляет указанное значение, выполняя поиск по check_column и check_mean.
        Например: update("users", "userID", 123, "tag", "aboba")

        Возможные ошибки: TableNotFound, EntryNotFound
        :param table: имя таблицы
        :param check_column: название колонки для поиска записи
        :param check_mean: значение колонки для поиска записи
        :param update_column: название колонки для обновления
        :param update_mean: значение для обновления
        """
        with sq.connect(self.path) as con:
            cur = con.cursor()
            if table in self.tables:
                cur.execute("select * from " + table + " where " + check_column + " = :x", {'x': check_mean})
                res = cur.fetchone()
                if res is not None:
                    cur.execute("update " + table + " set " + update_column + " = :x where " + check_column + " = :y", {'x': update_mean, 'y': check_mean})
                else:
                    raise errors.EntryNotFound
            else:
                raise errors.TableNotFound
