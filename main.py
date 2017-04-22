"""
The driver program
"""
import argparse
import threading
import time
from subprocess import call
from requests import ConnectionError

from playproducer import PlayProducer
from processor import Processor
from startNSQ_Service import start_NSQ

POST_URL = 'http://127.0.0.1:4151/mpub?topic='
DELETE_URL = 'http://127.0.0.1:4151/topic/delete?topic='
LOOKUPD_HTTP_ADDRESS = ['http://127.0.0.1:4161']
TOPIC_NAME = "Videos"
NUM_TOTALMESSAGES = 10000
NUM_TOTAL = 100


def main():

    parser = argparse.ArgumentParser(
        description="Program to run a video play counts simulation utilizing NSQ and Django")
    parser.add_argument('action', action="store", help="runTests/run")
    parser.add_argument("-nt", "--num_threads", action="store", type=int, default=2,
                        help=" number of threads for consumer in the processor, default 2")
    parser.add_argument("-nm", "--num_messages", action="store", type=int, default=100000,
                        help="number of messages to consume, default 100,000")
    parser.add_argument("-nv", "--num_videos", action="store", type=int, default=100,
                        help="number of videos with distinctive uuids, default 100")
    parser.add_argument("-ui", "--update_interval", action="store", type=int, default=30,
                        help="number of seconds processor publish to client, default 30")
    parser.add_argument("-pcr", "--pc_ratio", action="store", type=int, default=1,
                        help="# producers/ # consumers for real-life simulation, default 1")
    parser.add_argument("-nsq", "--start_nsq", action="store_true",
                        help="choose to start nsq for automatically. This rogram requires"
                        "the service to be started manually otherwise."
                        "You can use python startNSQ_Service.py to start it manually."
                        " We also suggest start it manually since the message might be noisy otherwise")
    parser.add_argument("-r", "--real_life", action="store_true",
                        help="choose run use real-life simulation instead of"
                        "backing up the queue to start with")

    args = parser.parse_args()
    num_messages = args.num_messages
    num_videos = args.num_videos
    num_threads = args.num_threads
    pc_ratio = args.pc_ratio
    publish_interval = args.update_interval
    real_life = args.real_life
    if num_messages / num_videos < 100:
        print "too few messages (%s) for given videos (%s) " % (num_messages, num_videos)
        return
    if args.action == "runTests":
        print "Running Unittest for you my MASTER\nAll unittestcase classes are located"\
        "in /test_dir, be sure to have a successful consumption "\
        "process to ensure test_processor do its job. Otherwise,"\
         "correctness tests are skipped \n"
        commands = "python -m  unittest discover test_dir -v"
        call(commands.split())
    elif args.action == "run":
        if args.start_nsq:
            nsqService = threading.Thread(target=start_NSQ)
            nsqService.daemon = True
            nsqService.start()
            print "Starting NSQ SERVICE"
            time.sleep(3)
        try:
            playproducer = PlayProducer(num_messages, num_videos,
                                    "Videos", POST_URL, DELETE_URL)
            playproducer.generateRawData()
        except ConnectionError:
            print "you need to start NSQ first. You can either start"\
             "it maunally or via driver\n please refer to readme"
            return
        except Exception as e:
            print type(e)
            return

        if real_life:
            msg = ", real_life version(producing and consuming at the same time)"
        else:
            msg = ", back_up version(messages statically put on queue first)"
        print "Spinning up the Processor%s.\nI am utilizing %d threads" % (msg, num_threads)
        print "The update/publish interval is %s seconds" % publish_interval
        Processor.startProcessing(num_threads, publish_interval, real_life, pc_ratio)
    else:
        print "action must be runTests or run"


if __name__ == '__main__':
    main()
