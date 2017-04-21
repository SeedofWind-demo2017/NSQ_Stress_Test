import threading
from subprocess import call


def start_nsqlookupd():
    call(['nsqlookupd'])


def start_nsqd():
    call(['nsqd', '--lookupd-tcp-address=127.0.0.1:4160'])


def start_admin():
    call(['nsqadmin', '--lookupd-http-address=127.0.0.1:4161'])


def start_NSQ():
    nsqlookupd = threading.Thread(target=start_nsqlookupd)
    nsqd = threading.Thread(target=start_nsqd)
    nsqadmin = threading.Thread(target=start_admin)
    nsqlookupd.start()
    nsqd.start()
    nsqadmin.start()

if __name__ == '__main__':
    start_NSQ()
