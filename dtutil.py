import datetime


def addZero(num):
    if num < 10:
        num = "0" + str(num)
    return num


def getTime(dt, hour=True, minute=True, second=False):
    tm = dt.time()
    timeString = "{}".format(addZero(tm.hour))
    if minute:
        timeString += ":{}".format(addZero(tm.minute))
    if second:
        timeString += ":{}".format(addZero(tm.second))
    return timeString


def getDate(dt, day=True, month=True, year=True, sep="-"):
    date = []
    if year:
        date.append(str(dt.year))
    if month:
        date.append(str(addZero(dt.month)))
    if day:
        date.append(str(addZero(dt.day)))
    return sep.join(date)


def getDateAndTime(dt):
    dateValue = getDate(dt)
    timeValue = getTime(dt, hour=True, minute=True, second=True)
    return timeValue + " | " + dateValue


def getDateAndTimeShort(dt):
    dV = getDate(dt, day=True, month=True, year=False, sep="-")
    tV = getTime(dt, hour=True, minute=True, second=False)
    return dV + "., " + tV


def nowToWeekNumYear(passedWeeks=0):
    now = datetime.datetime.utcnow()
    string = datetimeToWeekNumYear(now, passedWeeks)
    return string


def datetimeToWeekNumYear(unixTime, passedWeeks=0):
    weekAndYear = unixTime.isocalendar()
    yearNum = weekAndYear[0]
    weekNum = weekAndYear[1]
    if passedWeeks >= weekNum:
        yearNum -= 1
        weekNum = weekNum-passedWeeks + 52
    else:
        weekNum = weekNum - passedWeeks
    return "{}-{}".format(yearNum, weekNum)


def getNextWeekday(weekday, hour=0, minute=0, second=0):
    d = datetime.datetime.utcnow()
    t = datetime.timedelta((7 + weekday - d.weekday()) % 7)
    newD = (d + t).replace(hour=hour, minute=minute, second=second)
    return newD


def isoToDates(isoDates):
    dates = [datetime.fromisoformat(date) for date in isoDates]
    return dates


def get_timedelta_string(delta):
    d_unit = "days" if delta.days > 1 else "day"
    days_string = "{} {}".format(delta.days, d_unit) if delta.days > 0 else ""
    hours, rest = divmod(delta.seconds, 3600)
    minutes, seconds = divmod(rest, 60)

    seconds_string = ":0{}".format(
        seconds) if seconds < 10 else ":{}".format(seconds)
    seconds_string = seconds_string if seconds > 0 else ""
    hours_string = "{}h".format(
        hours) if minutes == 0 and seconds == 0 else "{}".format(hours)
    hours_string = "" if hours == 0 and minutes == 0 and seconds == 0 else hours_string
    minute_string = ":0{}".format(
        minutes) if minutes < 10 else ":{}".format(minutes)
    minute_string = "" if minutes == 0 and seconds == 0 else minute_string

    delta_string = "{} {}{}{}".format(
        days_string, hours_string, minute_string, seconds_string)
    return delta_string
