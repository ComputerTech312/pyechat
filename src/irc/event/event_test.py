import unittest
from .event import Event
from unittest.mock import MagicMock

class TestEventMethods(unittest.TestCase):

    def test_create_event(self):
        event = Event()
        self.assertTrue(event)

    def test_fire_event(self):
        mock = MagicMock()
        event = Event()
        event.on('test', mock)
        event.emit('test', 'hello')
        mock.assert_called_with('hello')

    def test_fire_event_no_listener(self):
        event = Event()
        event.emit('test', 'hello')
        self.assertTrue(True)
