import datetime


def date_now() -> str:
    return datetime.date.today().strftime("%Y-%m-%d")


def time_now() -> str:
    return datetime.datetime.now().time().strftime("%H%M%S")


def datetime_now() -> str:
    return datetime.datetime.now().strftime("%Y-%m-%d-%H%M%S")


VARNAME_DATE = "date"
VARNAME_TIME = "time"
VARNAME_DATETIME = "datetime"

VARIABLES = {
    VARNAME_DATE: date_now,
    VARNAME_TIME: time_now,
    VARNAME_DATETIME: datetime_now,
}
