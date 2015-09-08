import calendar
import datetime
import pytz
from dateutil import parser


def dt_fmt(date):
    ''' Format date '''
    return date.strftime('%d %b %H:%M')


def timestamp_fmt(ts, tz='UTC'):
    ''' Format timestamp '''
    return from_timestamp(ts).replace(tzinfo=pytz.utc) \
                             .astimezone(pytz.timezone(tz)) \
                             .strftime('%d %b %H:%M')


def now():
    return datetime.datetime.utcnow()


def parse(dt_str):
    return parser.parse(dt_str)


def timestamp_now():
    return to_timestamp(now())


def from_timestamp(timestamp):
    return datetime.datetime.utcfromtimestamp(timestamp)


def to_timestamp(date):
    timestamp = calendar.timegm(date.utctimetuple())
    return timestamp


def timedelta_fmt(td_object):
    # probably never used
    seconds = int(td_object.total_seconds())
    periods = [
        ('year',        60*60*24*365),
        ('month',       60*60*24*30),
        ('day',         60*60*24),
        ('hour',        60*60),
        ('minute',      60),
        ('second',      1)
        ]

    strings = []
    for period_name, period_seconds in periods:
        if seconds > period_seconds:
            period_value, seconds = divmod(seconds, period_seconds)
            if period_value == 1:
                strings.append("%s %s" % (period_value, period_name))
            else:
                strings.append("%s %ss" % (period_value, period_name))

    return ", ".join(strings)


def timedelta_fmt_rounded(td_object=None, seconds=-1):
    if seconds == -1:
        seconds = int(td_object.total_seconds())
    # name, seconds, value for next period to round up
    periods = [
        ('year',        60*60*24*365, 11),
        ('month',       60*60*24*30,  26),
        ('day',         60*60*24,     18),
        ('hour',        60*60,        46),
        ('minute',      60,           31),
        ('second',      1,             0)
    ]
    cvalue = 0
    cname = ''
    cnext = 999999
    for period_name, period_seconds, period_next in periods:
        if seconds > period_seconds:
            # remaining seconds fit this period
            tvalue, seconds = divmod(seconds, period_seconds)
            if cvalue == 0 and tvalue < cnext:
                # this will be the result period
                cvalue = tvalue
                cname = period_name
                cnext = period_next
            else:
                # check whether to round up
                if tvalue >= cnext:
                    cvalue += 1
                break
        else:
            # seconds don't fit this period
            if cvalue == 0:
                # this can be the result period if next period rounds up
                cname = period_name
                cnext = period_next
            else:
                break

    if cvalue == 1:
        result = '1 ' + cname
    else:
        result = '%s %ss' % (cvalue, cname)
    return result


def since_fmt(date):
    diff = datetime.datetime.now() - date
    # return 'about %s ago (%s // %s // %s secs)' % (timedelta_fmt_rounded(diff), date, diff, int(diff.total_seconds()))
    return 'about %s ago' % timedelta_fmt_rounded(diff)
