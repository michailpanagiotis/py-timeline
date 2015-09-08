#!/usr/bin/python
# -*- coding: utf8 -*-

from timeline.timeline import Timeframe
from unittest import TestCase


class TestTimeframe(TestCase):

    def test_and(self):
        frames = [Timeframe(1, 4), Timeframe(5, 7), Timeframe(3, 6)]
        assert Timeframe.union(frames) == Timeframe(1, 7)

    def test_or(self):
        frames = [Timeframe(2, 4), Timeframe(1, 4), Timeframe(5, 7),
                  Timeframe(3, 6)]
        assert Timeframe.intersection(frames) is None
        frames = [Timeframe(1, 5), Timeframe(5, 7), Timeframe(3, 6)]
        assert Timeframe.intersection(frames) == Timeframe(5, 5)
