import json
import os
import unittest
from processor import Processor, ProcessorError


class SourceIndex:
    INITIAL_COUNTDIC = 0
    PROCESSOR_COUNTDIC = 1
    CLIENT_COUNTDIC = 2
    CLIENT_STATSDIC = 3


class TestProccsor(unittest.TestCase):
    """
    Test the correctness of the processor
    """
    def setUp(self):
        print "TestProccsor"
        testsource = os.path.join(os.path.dirname(__file__), 'UnittestSource.txt')
        self._file_should_be_ready(testsource)
        self.source = [json.loads(s) for s in self.source]
        self.source[SourceIndex.PROCESSOR_COUNTDIC] = \
            {k: v[0] for k, v in self.source[SourceIndex.PROCESSOR_COUNTDIC].iteritems()}
        client_dic = {}
        for data in self.source[SourceIndex.CLIENT_COUNTDIC]:
            client_dic[data['uuid']] = data['count']
        self.source[SourceIndex.CLIENT_COUNTDIC] = client_dic

    def _file_should_be_ready(self, testsource):
        try:
            with open(testsource, 'r') as f:
                self.source = f.readlines()
        except IOError:
            self.skipTest(TestProccsor)
        if len(self.source) != 4:
            print ("Please wait for processor finishing consuming the message")
            self.skipTest(TestProccsor)

    def test_proccessor_has_correct_count(self):

        self.assertEqual(self.source[SourceIndex.PROCESSOR_COUNTDIC],
                         self.source[SourceIndex.INITIAL_COUNTDIC])

    def test_client_has_correct_count(self):
        self.assertEqual(self.source[SourceIndex.CLIENT_COUNTDIC],
                         self.source[SourceIndex.INITIAL_COUNTDIC])

    def test_messages_should_be_all_consumed(self):
        message_consumed = len(self.source[SourceIndex.CLIENT_STATSDIC])
        message_produced = sum(self.source[SourceIndex.INITIAL_COUNTDIC].values())
        self.assertTrue(abs(message_consumed - message_produced) <= 1)

    def test_prohibt_from_initialization(self):
        self.assertRaises(ProcessorError, Processor, "anything")
if __name__ == '__main__':
    unittest.main()
