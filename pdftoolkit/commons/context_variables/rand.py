import random
import string
import uuid as uid
from sys import maxsize
from typing import Dict, Any

MAX_RAND_NUM = maxsize
MIN_RAND_NUM = 0

RAND_STR_LEN = 16
RAND_STR_CHARS = string.ascii_letters + string.digits

VARNAME_RAND_NUM = "rand"
VARNAME_RAND_STR = "randstr"
VARNAME_UUID = "uuid"


def rand(ctx: Dict[str, Any]) -> int:
    max_num = MAX_RAND_NUM
    if "MAX_RAND_NUM" in ctx:
        tmp = ctx["MAX_RAND_NUM"]
        if isinstance(tmp, int):
            max_num = tmp

    min_num = MIN_RAND_NUM
    if "MIN_RAND_NUM" in ctx:
        tmp = ctx["MIN_RAND_NUM"]
        if isinstance(tmp, int):
            min_num = tmp

    if max_num < min_num:
        max_num, min_num = min_num, max_num

    return random.randint(min_num, max_num)


def rand_str(ctx: Dict[str, Any]):
    str_len = ctx.get("RAND_STR_LEN", RAND_STR_LEN)
    if str_len < 1:
        str_len = 1

    rand_chars = ctx.get("RAND_STR_CHARS", RAND_STR_CHARS)
    if isinstance(rand_chars, str):
        rand_chars = RAND_STR_CHARS
    return "".join(random.choice(rand_chars) for _ in range(str_len))


def uuid() -> str:
    return uid.uuid4().hex


VARIABLES = {
    VARNAME_RAND_NUM: rand,
    VARNAME_RAND_STR: rand_str,
    VARNAME_UUID: uuid,
}
