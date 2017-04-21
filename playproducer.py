import calendar
import os
from random import shuffle
import uuid
from collections import Counter
from datetime import date, datetime

import numpy as np
import requests
import ujson as json
from client import Client

LOWMSG_RATIO = 0.2
AVG_RATIO = 0.5
NONTRENDING_VALUE = 100
REAL_TOPIC = "real_videos"


class PlayProducer(object):
    """
    Responsible for generating raw messages to the initial queue
    """

    def __init__(self, num_total_messages, num_videos, topic_name, post_url, delete_url, log=True):
        self.num_total_messages = num_total_messages
        self.num_videos = num_videos
        self.topic = topic_name
        self.post_url = post_url
        self.delete_url = delete_url
        self.log = log

    @staticmethod
    def datetime_to_tstamp(dt):
        """
        Convert datetime into tstamp (secs since epoch), preserving microsecond
        precision (timetuple strips it out) static because can be use generally
        """
        if dt is None:
            return None
        if isinstance(dt, datetime):
            return calendar.timegm(dt.timetuple()) + dt.microsecond / 1000000.
        elif isinstance(dt, date):
            return calendar.timegm(dt.timetuple())

    @staticmethod
    def sampler(samples, sum_to, range_list):
        """
        method to generate a list of n numbers given targeted sum equal to k, and each element
        must be within speciifed range
        @params
        samples - number of samples/messages in our classes
        sum_to - target sum
        range_list - eg. [1,99]
        @return
        List of elements satisfy the constraint
        """
        assert range_list[0] < range_list[1]
        arr = np.random.rand(samples)
        sum_arr = sum(arr)

        new_arr = np.array([int((item / sum_arr) * sum_to) if (int((item / sum_arr) * sum_to) >
                            range_list[0]and int((item / sum_arr) * sum_to) < range_list[1])
                            else np.random.choice(range(range_list[0], range_list[1] + 1))
                            for item in arr])
        difference = sum(new_arr) - sum_to
        while difference != 0:
            if difference < 0:
                for idx in np.random.choice(range(len(new_arr)), abs(difference)):
                    if new_arr[idx] != range_list[1]:
                        new_arr[idx] += 1

            elif difference > 0:
                for idx in np.random.choice(range(len(new_arr)), abs(difference)):
                    if new_arr[idx] != 0 and new_arr[idx] != range_list[0]:
                        new_arr[idx] -= 1
            difference = sum(new_arr) - sum_to
        return new_arr

    def generateRawData(self):
        """
        @return the raw messages strings ready for putting on the intiial queue
        """
        uuids = [uuid.uuid1().hex for _ in xrange(self.num_videos)]
        self.nsq_delete()
        Client.reset(uuids)
        num_low_videos = int(self.num_videos * LOWMSG_RATIO)
        num_low_messages = int(num_low_videos * (LOWMSG_RATIO) * AVG_RATIO * NONTRENDING_VALUE)
        low_range = [1, NONTRENDING_VALUE - 1]
        avg_msg = int((self.num_total_messages * (1 - LOWMSG_RATIO)) / self.num_videos)
        high_range = [avg_msg, avg_msg * 2]
        low_videos = uuids[:num_low_videos]
        high_videos = uuids[num_low_videos:]
        batch_data = self.get_batchData(low_videos, num_low_messages, low_range)
        batch_data += self.get_batchData(high_videos,
                                         self.num_total_messages - num_low_messages, high_range)
        shuffle(batch_data)
        batch_data = ''.join(batch_data)
        # publish data
        self.publish_batchData(batch_data)
        # log the input when asked, default action for normal run except unittests
        test = [s.strip() for s in batch_data.splitlines()]
        ids = []
        for i in test:
            if i:
                id = json.loads(i).get('uuid')
                if id:
                    ids.append(id)
        c = Counter(ids)
        if self.log:

            print ("set up done, %d messages for %d vidoes queued to Videos(initial)"
                   "queue" % (self.num_total_messages, self.num_videos))
            test_file = os.path.join(os.getcwd(), "test_dir", "UnittestSource.txt")
            with open(test_file, 'w+') as f:
                f.write(json.dumps(c))
                f.write('\n')
        return c

    def nsq_publish(self, data):
        """
        mpub the data
        """
        url = self.post_url + self.topic
        r = requests.post(url, data)

    def nsq_delete(self):
        """
        delete given topics
        """
        url = self.delete_url + self.topic
        r = requests.post(url)
        url = self.delete_url + REAL_TOPIC
        r = requests.post(url)

    def get_batchData(self, uuids, num_messages, value_range):
        """
        get data that are ready to publishing (batched)
        """
        values = PlayProducer.sampler(len(uuids), num_messages, value_range)
        assignment = dict(zip(uuids, values))
        batch_data = []
        for k, v in assignment.items():
            for i in xrange(v):
                data = {}
                data['uuid'] = k
                data['enque_time'] = PlayProducer.datetime_to_tstamp(datetime.utcnow())
                batch_data.append(json.dumps(data) + '\n')
        return batch_data

    def publish_batchData(self, large_batchData):
        """
        since the list is large, we cut it half to publish
        """
        batch_list = large_batchData.split('\n')
        batch_part1 = '\n'.join(batch_list[:self.num_total_messages / 2])
        batch_part2 = '\n'.join(batch_list[self.num_total_messages / 2:])
        self.nsq_publish(batch_part1)
        self.nsq_publish(batch_part2)
