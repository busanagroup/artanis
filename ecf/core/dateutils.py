from __future__ import annotations

import datetime as dt

leapYearTable: list[int] = [31, 29, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
nonLeapYearTable: list[int] = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
dateDelta: int = 693594
hoursPerDay: int = 24
minsPerHour: int = 60
secsPerMin: int = 60
millisPerSec: int = 1000
minsPerDay: int = hoursPerDay * minsPerHour
secsPerDay: int = minsPerDay * secsPerMin
secsPerHour: int = secsPerMin * minsPerHour
millisPerDay: int = secsPerDay * millisPerSec

Delphi_D1 = 365
Delphi_D4 = Delphi_D1 * 4 + 1
Delphi_D100 = Delphi_D4 * 25 - 1
Delphi_D400 = Delphi_D100 * 4 + 1


def _is_leap_year(year: int) -> bool:
    return ((year % 4) == 0) and (((year % 100) != 0) or ((year % 400) == 0))


def valid_timestamp(date: int, time: int) -> bool:
    return (time >= 0) and (date > 0) and (time < millisPerDay)


def timestamp_to_delphi_datetime(date: int, time: int) -> float:
    val: float = 0
    if valid_timestamp(date, time):
        temp = (date - dateDelta) * millisPerDay
        temp = (temp + time) if temp >= 0 else (temp - time)
        val = float(temp / millisPerDay)
    return val


def delphi_encode_date(year: int, month: int, day: int) -> float:
    encoded: float = 0
    days_table: list = leapYearTable if _is_leap_year(year) else nonLeapYearTable
    if not (((((year < 1) or (year > 9999)) or (month < 1)) or (month > 12)) or (day > days_table[month - 1])):
        local_year = year - 1
        local_day = day
        for idx in range(0, month - 1):
            local_day += days_table[idx]
        encoded = ((int(local_year * 365) + int(local_year / 4) - int(local_year / 100) +
                    int(local_year / 400) + local_day) - dateDelta)
    return encoded


def delphi_encode_time(hour: int, minute: int, second: int, millis: int) -> float:
    encoded: float = 0
    if not ((((hour >= hoursPerDay) or (minute >= minsPerHour)) or (second >= secsPerMin)) or (
            millis >= millisPerSec)):
        ttime = ((hour * (minsPerHour * secsPerMin * millisPerSec)) +
                 (minute * secsPerMin * millisPerSec) + (second * millisPerSec) + millis)
        encoded = timestamp_to_delphi_datetime(dateDelta, ttime)
    return encoded


def delphi_encode_datetime(year: int, month: int, day: int,
                           hour: int, minute: int, second: int, millisecond: int) -> float:
    dval = delphi_encode_date(year, month, day)
    tval = delphi_encode_time(hour, minute, second, millisecond)
    return dval + tval


def delphi_from_date(val: dt.date):
    return delphi_encode_date(val.year, val.month, val.day)


def delphi_from_time(val: dt.time):
    return delphi_encode_time(val.hour, val.minute, val.second, int(val.microsecond / 1000))


def delphi_from_datetime(val: dt.datetime):
    return delphi_encode_datetime(val.year, val.month, val.day, val.hour, val.minute, val.second,
                                  int(val.microsecond / 1000))


def delphi_from_datelong(val: int):
    nint: int = int(val)
    d = int(nint % 100)
    m = int(nint / 100) % 100
    y = int(nint / 10000)
    return delphi_encode_date(y, m, d)


def delphi_from_timelong(val: int):
    nint: int = int(val)
    s = int(nint % 100)
    m = int(nint / 100) % 100
    h = int(nint / 10000)
    return delphi_encode_time(h, m, s, 0)


def delphi_from_datetimelong(val: int):
    nlong: int = int(val)
    s = int(nlong % 100)
    m = int(nlong / 100) % 100
    h = int(nlong / 10000) % 100
    dd = int(nlong / 1000000) % 100
    mm = int(nlong / 100000000) % 100
    yy = int(nlong / 10000000000)
    return delphi_encode_datetime(yy, mm, dd, h, m, s, 0)


def extract_delphi_time(delphi_time: float) -> tuple[int, int, int, int, int, int, int] | None:
    temp = round(delphi_time * float(millisPerDay))
    temp2 = int(temp / millisPerDay)
    tdate = int(dateDelta + temp2)
    ttime = abs(temp) % millisPerDay
    min_count = int(ttime / (secsPerMin * millisPerSec))
    milis_count = int(ttime % (secsPerMin * millisPerSec))
    _hour = int(min_count / minsPerHour)
    _minute = int(min_count % minsPerHour)
    _seconds = int(milis_count / millisPerSec)
    _millis = int(milis_count % millisPerSec)
    if tdate <= 0:
        _year = 0
        _month = 0
        _day = 0
    else:
        tdate -= 1
        y = 1
        while tdate >= Delphi_D400:
            tdate -= Delphi_D400
            y += 400

        i = int(tdate / Delphi_D100)
        d = int(tdate % Delphi_D100)
        if i == 4:
            i -= 1
            d += Delphi_D100
        y += (i * Delphi_D100)
        i = int(d / Delphi_D4)
        d = int(d % Delphi_D4)
        y += (i * 4)
        i = int(d / Delphi_D1)
        d = int(d % Delphi_D1)
        if i == 4:
            i -= 1
            d += Delphi_D1
        y += i
        days_table = leapYearTable if _is_leap_year(y) else nonLeapYearTable
        m = 0
        while True:
            i = days_table[m]
            if d < i:
                break
            d -= i
            m += 1
        _year = y
        _month = m + 1
        _day = int(d) + 1
    return int(_year), int(_month), int(_day), int(_hour), int(_minute), int(_seconds), int(_millis)


def delphi_to_datelong(delphi_time: float) -> int:
    _year, _month, _day, _hour, _minute, _seconds, _millis = extract_delphi_time(delphi_time)
    return (_year * 10000) + (_month * 100) + _day


def delphi_to_timelong(delphi_time: float) -> int:
    _year, _month, _day, _hour, _minute, _seconds, _millis = extract_delphi_time(delphi_time)
    return (_hour * 10000) + (_minute * 100) + _seconds


def delphi_to_datetimelong(delphi_time: float) -> int:
    _year, _month, _day, _hour, _minute, _seconds, _millis = extract_delphi_time(delphi_time)
    return (_year * 10000000000) + (_month * 100000000) + (_day * 1000000) + \
        (_hour * 10000) + (_minute * 100) + _seconds


def delphi_to_date(delphi_time: float) -> dt.date:
    _year, _month, _day, _hour, _minute, _seconds, _millis = extract_delphi_time(delphi_time)
    return dt.date(_year, _month, _day)


def delphi_to_time(delphi_time: float) -> dt.time:
    _year, _month, _day, _hour, _minute, _seconds, _millis = extract_delphi_time(delphi_time)
    return dt.time(_hour, _minute, _seconds, _millis)


def delphi_to_datetime(delphi_time: float) -> dt.datetime:
    _year, _month, _day, _hour, _minute, _seconds, _millis = extract_delphi_time(delphi_time)
    return dt.datetime(_year, _month, _day, _hour, _minute, _seconds, _millis * 1000)


if __name__ == "__main__":
    today = dt.datetime.now()
    print(today)
    dtoday = delphi_from_datetime(today)
    print(delphi_to_datetime(dtoday))
