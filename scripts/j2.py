from aiofiles import open as a_open
from json import dumps, loads


def to_(obj: dict[str, ...], *, tab: int = 4, separators: tuple[str, str] = (', ', ': '), string_mode: bool = False) -> str:
    """
    Return string in JSON format

    :param obj: dictionary object with only string-keys
    :param tab: amount of spaces in a tab char
    :param separators: separators for a return string
    :param string_mode: if true, returns a string without new lines
    :return: json-like string from input dictionary
    """

    data = dumps(obj, indent=tab, separators=separators, ensure_ascii=False)
    return data if not string_mode else data.replace('\n', '').replace(' ' * tab, ' ').strip()


def from_(json: str) -> dict[str, ...]:
    """
    :param json: json-like string
    :return: dict
    """

    return loads(json)


def fromfile(abspath: str) -> dict[str, ...]:
    with open(abspath, encoding='utf8') as file:
        return from_(file.read())


async def fromfile_async(abspath: str) -> dict[str, ...]:
    async with a_open(abspath, encoding='utf8') as file:
        return from_(await file.read())
