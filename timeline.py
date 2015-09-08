import collections
import datetools
import itertools
import json
import pprint
from copy import deepcopy
from itertools import izip_longest


class JsonEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Event):
            return obj.as_dict()
        elif isinstance(obj, Timeline):
            return obj.as_list()
        else:
            return json.JSONEncoder.default(self, obj)


class Timeframe(tuple):
    @classmethod
    def __new__(cls, a, *args):
        if not len(args) in (1, 2):
            raise Exception('A timeframe must be initialized by at least one '
                            'and at most two numeric values')
        from_time = args[0]
        if len(args) == 2:
            to_time = args[1]
        else:
            to_time = from_time
        if from_time > to_time:
            raise Exception('A timeframe\'s first point must be less than '
                            'or equal to the second point')
        return super(Timeframe, cls).__new__(cls, (from_time, to_time))

    def __and__(self, other):
        return Timeframe.union((self, other))

    def __repr__(self):
        return 'Timeframe(%s, %s)' % (self[0], self[1])

    @staticmethod
    def intersection(timeframes):
        if timeframes:
            if any(x is None for x in timeframes):
                return None
            from_time = max([x[0] for x in timeframes])
            to_time = min([x[1] for x in timeframes])
            if from_time > to_time:
                return None
            return Timeframe(from_time, to_time)
        return None

    @property
    def is_momentary(self):
        return self[0] == self[1]

    @staticmethod
    def union(timeframes):
        if timeframes:
            return Timeframe(min([x[0] for x in timeframes]),
                             max([x[1] for x in timeframes]))
        return None


class Event(collections.MutableMapping):

    def __init__(self, _at=None, _until=None, *args, **kwargs):
        if _at is None:
            _at = datetools.timestamp_now()
        self._at = _at
        self._until = _until
        self._store = dict()
        self.update(dict(*args, **kwargs))

    def __eq__(self, other):
        if self._at == other._at and self._until == other._until:
            return super(Event, self).__eq__(other)
        return False

    def __ne__(self, other):
        return not self.__eq__(other)

    def __getitem__(self, key):
        return self._store[key]

    def __setitem__(self, key, value):
        self._store[key] = value

    def __delitem__(self, key):
        del self._store[key]

    def __iter__(self):
        return iter(self._store)

    def __len__(self):
        return len(self._store)

    def __repr__(self):
        if not self._until:
                return 'Event(%s %s)' % (self._store.__repr__(), self._at)
        else:
                return 'Event(%s %s-%s)' % (self._store.__repr__(),
                                            self._at, self._until)

    def __str__(self):
        return json.dumps(self, cls=JsonEncoder)

    def as_dict(self, timeinfo=True):
        d = dict(self._store)
        if timeinfo:
            d['_at'] = self._at
            if self._until:
                d['_until'] = self._until
        return d

    def empty(self):
        return not self._store

    @classmethod
    def from_json(cls, serialized):
        fields = json.loads(serialized)
        return cls.from_json_obj(fields)

    @classmethod
    def from_json_obj(cls, json_obj):
        return cls(**json_obj)

    def timeframe(self):
        if self._until is None:
            until = self._at
        else:
            until = self._until
        return Timeframe(self._at, until)

    def project(self, function):
        ''' Projects the event on a different time frame'''
        d = dict(self._store)
        projection = function(self)
        try:
            projection = tuple(projection)
            d['_at'] = projection[0]
            d['_until'] = projection[1]
        except TypeError:
            d['_at'] = projection
        return Event(**d)


class Timeline(object):
    def __init__(self, events=None, event_cls=None):
        if not events:
            if not event_cls:
                self.event_cls = Event
            else:
                self.event_cls = event_cls
            self._events = list()
            return
        if isinstance(events, str) or isinstance(events, unicode):
            raise Exception('Deprecation error')
        self.event_cls = events[0].__class__
        self._events = events

    def __getitem__(self, index):
        return self._events[index]

    def __eq__(self, other):
        if len(other) != len(self):
            return False
        for idx, item in enumerate(self._events):
            if other[idx] != item:
                return False
        return True

    def __ne__(self, other):
        return not self.__eq__(other)

    def __len__(self):
        return len(self._events)

    def __repr__(self):
        return 'Timeline(%s)' % ','.join([x.__repr__() for x in self._events])

    def __str__(self):
        return json.dumps(self, cls=JsonEncoder)

    def append(self, event):
        if not isinstance(event, self.event_cls):
            raise TypeError("The timeline expects events of type '%s'" %
                            str(self.event_cls))
        self._events.append(event)

    def as_list(self):
        return [x.as_dict() for x in self._events]

    @classmethod
    def copy(cls, other):
        return cls(deepcopy(other._events), other.event_cls)

    def deltas(self, function, as_timeline=True):
        ''' Produces a timeline with deltas between events '''
        a, b = itertools.tee(self._events)
        next(b, None)
        pairwise = itertools.izip(a, b)
        value_deltas = tuple(itertools.starmap(function, pairwise))
        if as_timeline:
            deltas = Timeline()
            for idx, event in enumerate(self._events[1:]):
                deltas.append(Event(_at=event._at, _until=event._until,
                                    **value_deltas[idx]))
            return deltas

    def empty(self):
        return not self._events

    def extend(self, other_history):
        self._events.extend(other_history._events)

    def extend_earlier(self, other_history):
        self._events[0:0] = other_history._events

    def filter(self, function):
        new = Timeline()
        new._events = filter(function, self._events)
        return new

    def first_event(self):
        return self[0]

    def first_events(self, num):
        return self[0:num]

    @classmethod
    def from_json(cls, serialized, event_cls=Event):
        try:
            deserialized = json.loads(serialized)
        except ValueError:
            if serialized != u'None':
                raise Exception('Malformed json history')

            deserialized = []
        return cls.from_events(deserialized, event_cls)

    @classmethod
    def from_events(cls, events, event_cls=Event):
        if not isinstance(events, list):
            raise Exception('Malformed history, expecting a list of dicts')
        events = list(event_cls.from_json_obj(x) for x in events)
        return cls(events)

    def get_event_at(self, timestamp, default=None):
        return next((x for x in self._events if x._at == timestamp), default)

    def last(self, predicate):
        '''
        Returns a timeline with all the consecutive last events that pass
        the predicate function
        '''
        result = Timeline()
        collection = reversed(self._events)
        for ev in collection:
            if predicate(ev):
                result.append(ev)
            else:
                break
        result.reverse()
        return result

    def last_event(self):
        return self[-1]

    def last_events(self, num):
        return self[-num:]

    def map(self, function):
        new = Timeline()
        new._events = [self.event_cls(_at=x._at, _until=x._until,
                                      **function(x))
                       for x in self._events]
        return new

    def pop_first(self):
        return self._events.pop(0)

    def project(self, function):
        new = Timeline()
        new._events = [x.project(function) for x in self._events]
        return new

    @staticmethod
    def pprint(timelines, titles=tuple(), width=80):
        print Timeline.pformat(timelines, titles, width)

    @staticmethod
    def pformat(timelines, titles=tuple(), width=80):
        '''
        Pretty prints one or more timelines side by side
        '''
        if not titles:
            titles = ('',) * len(timelines)
        if len(titles) != len(timelines):
            raise Exception('Titles must be as many as the timelines')
        all_timestamps = set()
        for timeline in timelines:
            all_timestamps.update(set(timeline.timestamps()))

        all_timestamps = sorted(list(all_timestamps))
        full_width = len(timelines) * width
        half_width = full_width / 2
        separator_width = half_width - 10
        separator = '-' * separator_width
        result = '\n'
        result += ' | '.join([x.center(width) for x in titles])
        for timestamp in all_timestamps:
            columns = []
            for timeline in timelines:
                event = timeline.get_event_at(timestamp)
                if event:
                    event = event.as_dict(timeinfo=True)
                    lines = pprint.pformat(event, width=width).split('\n')
                    columns.append([x.ljust(width) for x in lines])
                else:
                    columns.append([])
            date = datetools.from_timestamp(timestamp)
            result += '\n%s %s %s %s\n' % (separator, timestamp,
                                           datetools.dt_fmt(date), separator)
            for line in izip_longest(*columns, fillvalue=' '*width):
                result += ' | '.join(line) + '\n'
        return result

    def reverse(self):
        self._events = list(reversed(self._events))

    def size(self):
        return len(self._events)

    def sort(self):
        self._events = sorted(self._events, key=lambda x: x._at)

    def timeframe(self):
        timeframes = self.timeframes()
        return Timeframe.union(timeframes)

    def timeframes(self):
        return tuple(x.timeframe() for x in self._events)

    def timestamps(self):
        return [x._at for x in self._events]

    def trim(self, max_size):
        while len(self._events) > max_size:
            self.pop_first()

if __name__ == '__main__':
    print '*** Creating a timeline...'
    timeline = Timeline()
    Timeline.pprint([timeline])
    print '*** Adding a creation event...'
    from time import sleep
    sleep(1)
    timeline.append(Event(status='created'))
    Timeline.pprint([timeline])
    sleep(2)
    print '*** Adding an update event...'
    sleep(1)
    timeline.append(Event(status='updated', changes=['1', '2', '3']))
    Timeline.pprint([timeline])
    sleep(2)
    print '*** Adding a delete event...'
    sleep(1)
    timeline.append(Event(status='soft deleted'))
    Timeline.pprint([timeline])
