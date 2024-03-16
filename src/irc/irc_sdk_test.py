import time
import unittest

from src.irc.irc_sdk import IRCSDK


class TestIRCSDKMethods(unittest.TestCase):

    def test_create_irc(self):
        irc = IRCSDK(None)
        self.assertTrue(irc)

    def test_connect(self):
        irc = IRCSDK({
            'host': 'irc.rizon.net',
            'port': 6667,
            'nick': 'testtest-pyechat',
            'channel': '#pyechat',
        })
        irc.connect(None)
        # sleep for 10 seconds
        time.sleep(10)
        # irc.join('#pyechat')
        # self.assertTrue(irc.irc)

    def test_onconnect(self):
        irc = IRCSDK()
        irc.connect()
        self.assertTrue(irc.event)

