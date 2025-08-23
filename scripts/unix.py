from time import time as raw


def raw2unix(__raw__: float) -> float:
    return round(__raw__, 2)


def unix() -> float:
    return raw2unix(raw())
