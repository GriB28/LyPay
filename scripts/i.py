symbols = list('0123456789abcdefghijklmnopqrstuvwxyz')


def to_id(__num__: int) -> str:
    """
    :param __num__: Число в 10-ричной системе счисления для перевода в 36-ричную
    :return: Число в 36-ричной системе счисления
    """
    __ans__ = ''
    while __num__ > 0:
        __ans__ = symbols[__num__ % 36] + __ans__
        __num__ //= 36
    return __ans__[:2] if len(__ans__) > 1 else '0' + __ans__


def to_int(__id__: str) -> int:
    """
    :param __id__: Число в 36-ричной системе счисления для перевода в 10-ричную
    :return: Число в 10-ричной системе счисления
    """
    return int(__id__, base=36)
