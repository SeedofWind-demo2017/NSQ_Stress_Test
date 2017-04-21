import unittest

from playproducer import PlayProducer

POST_URL = 'http://127.0.0.1:4151/mpub?topic='
DELETE_URL = 'http://127.0.0.1:4151/topic/delete?topic='


class TestPlayProducer(unittest.TestCase):
    """
    Test the correctness of the processor
    """
    def setUp(self):
        print "\nTestPlayProducer"
        self.playproducer = PlayProducer(1000, 10, "test", POST_URL, DELETE_URL, False)

    def test_should_create_msgs(self):
        c = self.playproducer.generateRawData()
        self.assertEquals(len(c), 10)
        self.assertEquals(sum(c.values()), 1000)

    def tearDown(self):
        self.playproducer.nsq_delete()

if __name__ == '__main__':
    unittest.main()
