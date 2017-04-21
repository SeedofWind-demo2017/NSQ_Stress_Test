import os
import sys
import unittest
import uuid

from client import Client, ClientError
from video.models import Video

proj_path = os.path.join(os.getcwd(), 'video_distributor/')
sys.path.append(proj_path)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "video_distributor.settings")


class TestClient(unittest.TestCase):
    """
    Test the correctness of the Client
    """

    def setUp(self):
        print "\nTestClient"
        self.uuids = [uuid.uuid1().hex for _ in xrange(10)]
        self.data = {k: 1 for k in self.uuids}
        Client.reset(self.uuids)

    def test_update_counts(self):
        Client.update_counts(self.data)
        recs = Video.objects.all()
        for i in recs:
            self.assertEquals(i.count, self.data[i.uuid])

    def test_prohibt_from_initialization(self):
        self.assertRaises(ClientError, Client, "anything")

    @classmethod
    def tearDownClass(cls):
        Client.truncate()

if __name__ == '__main__':
    unittest.main()
