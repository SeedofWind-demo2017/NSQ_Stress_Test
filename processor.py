import os
import threading
import time
from datetime import datetime
from functools import partial

import nsq
import ujson as json

from client import Client
from playproducer import PlayProducer
from tornado import gen


class ProcessorError(Exception):
    """
    Proccessor Exception
    """
    pass


class Processor(object):
    """
    Where the magic happens
    @attributes
    _PLAYCOUNT - the source of truth for play counts
    _firstime - indicate whether it's first time to do a publish
    _lock - the lock
    _interval - the publish interval for the processor
    _PCratio - producers/consumers for real-life simulation
    _testFileGenerated - indicate whether the testfile for unittest is generated
    """
    _PLAYCOUNT = {}
    _firsttime = True
    _lock = threading.RLock()
    _interval = None
    _PCratio = 1
    _testFileGenerated = False

    def __init__(*args, **kwargs):
        """
        PROHIBIT class from Instantiation
        @raise
        ProcessorError
        """
        raise ProcessorError("Processor is an Engine, Donot Instantiate this Class")

    @classmethod
    @gen.coroutine
    def write_message(cls, topic, data, writer):
        """
        coroutine and class method to spin up producer to produce to consumption queue
        for real-life version of simulation
        @params
        topic - topic for the queue to produce to
        data - data to produce to the target queue
        writer - the producer
        @async
        """
        yield gen.Task(writer.pub, topic, data)

    @classmethod
    def reallife_producer(cls, message, writer):
        """
        Although named producer, it's actually a consumer to consume from the dummy queue
        and invoke write_message mentioned above
        @param
        message - messages on a queue
        writer - the producer
        """
        message.enable_async()
        data = json.loads(message.body)

        data['enque_time'] = PlayProducer.datetime_to_tstamp(datetime.utcnow())
        cls.write_message("real_videos", json.dumps(data), writer)
        message.finish()

    @classmethod
    def startProcessing(cls, n, publish_interval, real_life, PCratio):
        """
        Where the magic happens
        @params
        n - number of reader threads
        publish_interval - interval for processor to publish the play counts to the client
        real_life - bool to indicate weather to run real-life version simulation
        PCratio - producers/consumers for real-life simulation
        @#async
        """
        consume_topic = "Videos"
        cls._interval = publish_interval
        cls._PCratio = PCratio
        if real_life:
            writer = nsq.Writer(['127.0.0.1:4150', ])
            reallife_handler = partial(cls.reallife_producer, writer=writer)
            [nsq.Reader(topic="Videos",
                        message_handler=reallife_handler,
                        nsqd_tcp_addresses=['127.0.0.1:4150', ],
                        channel='worker_group_a') for _ in xrange(cls._PCratio * n)]
            consume_topic = "real_videos"
        [nsq.Reader(topic=consume_topic,
                    message_handler=cls.consumer,
                    nsqd_tcp_addresses=['127.0.0.1:4150', ],
                    channel='worker_group_a') for _ in xrange(n)]
        publisher_thread = threading.Thread(target=cls.startPublisher)
        publisher_thread.daemon = True
        print "\nProcessing Starts, my MASTER\n"
        publisher_thread.start()
        nsq.run()

    @classmethod
    @gen.coroutine
    def consume_async(cls, uuid, enque_time):
        """
        This is invoked when we consume the message off the queue. You can see
        it's a coroutine since the client publish can be expensive and takes a long time
        so we donot want the reader/consumer to wait for it
        """
        def _consume(uuid, enque_time, callback):
            cls._lock.acquire()
            Client.update_stats((enque_time, PlayProducer.datetime_to_tstamp(datetime.utcnow())))
            if uuid in cls._PLAYCOUNT:
                counts = cls._PLAYCOUNT[uuid][0]
                cls._PLAYCOUNT[uuid] = (counts + 1, True)
            else:
                cls._PLAYCOUNT[uuid] = (1, True)
            # real-time upadtes the low counts
            if cls._PLAYCOUNT[uuid][0] < 100:
                Client.update_count((uuid, cls._PLAYCOUNT[uuid][0]))
                cls._PLAYCOUNT[uuid] = (cls._PLAYCOUNT[uuid][0], False)
            cls._lock.release()
            return callback(uuid)
        yield gen.Task(_consume, uuid, enque_time)

    @classmethod
    def consumer(cls, message):
        """
        The consumer that handles the consumption of the message on the queue.
        It invokes consume_async to does its job
        """
        message.enable_async()
        data = json.loads(message.body)
        uuid = data['uuid']
        enque_time = data['enque_time']
        cls.consume_async(uuid, enque_time)
        message.finish()

    @classmethod
    def publish(cls):
        """
        method to publish the playcounts to client maximum 20 msgs each time
        """
        additional_msg = ""
        to_update = {k: v[0] for k, v in Processor._PLAYCOUNT.iteritems() if v[1]}
        # only 20 allowed each time
        to_update = dict(to_update.items()[:20])
        for k in to_update:
            cls._PLAYCOUNT[k] = (cls._PLAYCOUNT[k][0], False)
        if len(to_update) > 0 or cls._firsttime:
            Client.update_counts(to_update)
            cls._testFileGenerated = False
            if cls._firsttime:
                cls._firsttime = False
                additional_msg = "(initial run)"
        else:
            if not cls._testFileGenerated:
                cls._testFileGenerated = True
                test_file = os.path.join(os.getcwd(), "test_dir", "UnittestSource.txt")
                with open(test_file, 'a') as f:
                    print "All consumed, ready for running tests"
                    f.write(json.dumps(cls._PLAYCOUNT))
                    f.write('\n')
                    f.write(Client.export_result())
                    f.write('\n')
                    f.write(Client.export_stats())
            else:
                additional_msg = "(stable run)"
        print "%s less popular videos(uuids) updated %s" % (len(to_update), additional_msg)

    @classmethod
    def startPublisher(cls):
        """
        Start a timer to call publish periodically according to the publish_interval
        """
        while True:
            cls.publish()
            time.sleep(cls._interval)
