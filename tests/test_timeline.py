#!/usr/bin/python
# -*- coding: utf8 -*-

from timeline.timeline import Event, Timeline, Timeframe
from unittest import TestCase


class TestTimeline(TestCase):

    def test_append(self):
        timeline = Timeline()
        timeline.append(Event(body='created', _at=1408628762))
        timeline.append(Event(body='processed', _at=1408628769))
        assert len(timeline) == 2
        assert timeline[-1]['body'] == 'processed'
        assert timeline[-1]._at == 1408628769
        timeline.append(Event(body='ended', _at=1408628778))
        assert len(timeline) == 3
        assert timeline[-1]['body'] == 'ended'
        assert timeline[-1]._at == 1408628778

    def test_deserialize(self):
        serialized = ('[{"_at":1408628700, "body": "step1"}, '
                      '{"_at":1408628700, "body": "step2"}]')
        timeline = Timeline.from_json(serialized)
        assert len(timeline) == 2
        assert timeline[-1]['body'] == 'step2'
        assert timeline[-1]._at == 1408628700

    def test_serialize(self):
        timeline = Timeline()
        timeline.append(Event(body='created', _at=1408628762))
        timeline.append(Event(body='processed', _at=1408628769))
        assert str(timeline) == ('[{"body": "created", "_at": 1408628762}, '
                                 '{"body": "processed", "_at": 1408628769}]')

    def test_trim(self):
        timeline = Timeline()
        timeline.append(Event(body='created', _at=1408628762))
        timeline.append(Event(body='processed', _at=1408628769))
        timeline.append(Event(body='ended', _at=1408628778))
        timeline.trim(2)
        assert len(timeline) == 2
        assert timeline[0]['body'] == 'processed'
        assert timeline[0]._at == 1408628769

    def test_map(self):
        expected = Timeline()
        expected.append(Event(body='created', _at=1408628762))
        expected.append(Event(body='processed', _at=1408628769))
        expected.append(Event(body='ended', _at=1408628778))
        to_map = Timeline()
        to_map.append(Event(a=1, body='created', _at=1408628762))
        to_map.append(Event(a=2, body='processed', _at=1408628769))
        to_map.append(Event(a=3, body='ended', _at=1408628778))
        mapped = to_map.map(lambda x: {'body': x['body']})
        assert mapped == expected

    def test_last_consecutive(self):
        timeline = Timeline()
        timeline.append(Event(body='created', _at=1408628762))
        timeline.append(Event(body='processed', _at=1408628769))
        timeline.append(Event(body='ended', _at=1408628778))
        test = timeline.last(lambda x: x._at <= 1408628769)
        assert len(test) == 0
        test = timeline.last(lambda x: x._at > 1408628762)
        assert len(test) == 2
        assert test[0]._at == 1408628769
        assert test[0]['body'] == 'processed'

    def test_timeframe(self):
        timeline = Timeline()
        timeline.append(Event(body='created', _at=1408628762))
        timeline.append(Event(body='processed', _at=1408628769,
                              _until=1408628779))
        timeline.append(Event(body='ended', _at=1408628778))
        assert timeline.timeframe() == Timeframe(1408628762, 1408628779)

    def test_project(self):
        timeline = Timeline()
        timeline.append(Event(body='created', _at=1408628762,
                        timeframe=[4, 5]))
        timeline.append(Event(body='processed', _at=1408628769,
                        timeframe=[7, 8]))
        timeline.append(Event(body='ended', _at=1408628778,
                        timeframe=[10, 50]))
        projected = timeline.project(lambda x: x['timeframe'])
        assert projected[0]._at == 4
        assert projected[1]._until == 8
