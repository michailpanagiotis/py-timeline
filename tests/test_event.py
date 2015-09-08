#!/usr/bin/python
# -*- coding: utf8 -*-

from timeline.timeline import Event, Timeframe
from unittest import TestCase


class TestEvent(TestCase):

    def test_project(self):
        ev = Event(_at=1, timeframe=[4, 5], sample=6)
        p = ev.project(lambda x: (x['timeframe'][0], x['timeframe'][1]))
        assert str(p) == ('{"sample": 6, "_until": 5, "_at": 4, '
                          '"timeframe": [4, 5]}')

    def test_timeframe(self):
        ev = Event(_at=1, timeframe=[4, 5], sample=6)
        assert ev.timeframe() == Timeframe(1, 1)
        p = ev.project(lambda x: (x['timeframe'][0], x['timeframe'][1]))
        assert p.timeframe() == Timeframe(4, 5)
        p = ev.project(lambda x: x['timeframe'])
