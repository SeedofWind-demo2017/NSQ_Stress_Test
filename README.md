# Fun with NSQ

----

### Installation
Since I used Django to implement the client and python to write the processor, it will require a little bit effort to setup the virtualenv before you can run this __exciting__ program. Everything is wrapped inside virtualenv, so I promise it will be easy enough for you to get this rolling
###### Pre-requisites
I will assume those packages are installed correctly already
* Python 2.7
* Golang + NSQ (follow [this](http://nsq.io/deployment/installing.html) to install)

###### Setup

1. Download/clone the project folder and step in
2. Install virtualEnv for python
    ```
    $ sudo pip install virtualenv
    ```
3. create and activate virtualenv. You can create your virtualenv anywhere with any name, but this guide will create the virtualenv inside project folder with default name
    ```
    $ cd project_path
    $ virutalenv .
    $ source bin/activate

    Now you should see the virtualenv is activated
    eg. (NSQ_Stress_Test)  ✝  ~/Desktop/NSQ_Stress_Test 
    ```
4. install all packages inside virtualenv
    ```
    $ pip install -r requirements.txt

    be sure to run this without sudo, so it won't mess up your global python env
    ```
5. setup Django
    ```
    You might need to set DJANGO modules by

    $ export DJANGO_SETTINGS_MODULE=video_distributor.settings

    be sure now you are at the root level of project folder

    $ python video_distributor/manage.py migrate

    ```
6. run client(Django local) server
    ```
    $ python video_distributor/manage.py runserver

    System check identified no issues (0 silenced).
    April 16, 2017 - 13:51:39
    Django version 1.8, using settings 'video_distributor.settings'
    Starting development server at http://127.0.0.1:8000/
    Quit the server with CONTROL-C.
    ```
7. go to the localshot address specified in the terminal and you should be able to see something like this
![alt text](https://www.dropbox.com/s/f3n05qqhwiiodnx/wistia_1.png?raw=1 "Logo Title Text 1")
![alt text](https://www.dropbox.com/s/hm1g7sp4an2hc2s/wistia_2.png?raw=1 "Logo Title Text 1")


Now you are ready to run the program

____________________

###  Usage
Before getting to the demo part, let's breifly dicuss the usages

1. Start nsq service.
This step __can be skipped__ if you choose to use the main driver to start nsq automatically. however, i do not suggest doing that since it will make the stdout quite noisy and messy.
```
$ python startNSQ_Service.py
```
2. start the django client
    ```
    $ python video_distributor/manage.py runserver

    System check identified no issues (0 silenced).
    April 16, 2017 - 13:51:39
    Django version 1.8, using settings 'video_distributor.settings'
    Starting development server at http://127.0.0.1:8000/
    ```
    go to the localhost address specified in the terminal and you should be able to see something like this
    ![alt text](https://www.dropbox.com/s/f3n05qqhwiiodnx/wistia_1.png?raw=1 "Logo Title Text 1")
    ![alt text](https://www.dropbox.com/s/hm1g7sp4an2hc2s/wistia_2.png?raw=1 "Logo Title Text 1")
3. Now we are ready to run the driver, you can invoke -h to see the usages function
    ```
    (NSQ_Stress_Test)  ✝  ~/Desktop/NSQ_Stress_Test  python main.py -h
    usage: main.py [-h] [-nt NUM_THREADS] [-nm NUM_MESSAGES] [-nv NUM_VIDEOS]
                   [-ui UPDATE_INTERVAL] [-pcr PC_RATIO] [-nsq] [-r]
                   action

    Program to run a video play counts simulation utilizing NSQ and Django

    positional arguments:
      action                runTests/run

    optional arguments:
      -h, --help            show this help message and exit
      -nt NUM_THREADS, --num_threads NUM_THREADS
                            number of threads for consumer in the processor,
                            default 2
      -nm NUM_MESSAGES, --num_messages NUM_MESSAGES
                            number of messages to consume, default 100,000
      -nv NUM_VIDEOS, --num_videos NUM_VIDEOS
                            number of videos with distinctive uuids, default 100
      -ui UPDATE_INTERVAL, --update_interval UPDATE_INTERVAL
                            number of seconds processor publish to client, default
                            30
      -pcr PC_RATIO, --pc_ratio PC_RATIO
                            # producers/ # consumers for real-life simulation,
                            default 1
      -nsq, --start_nsq     choose to start nsq for automatically. This rogram
                            requiresthe service to be started manually
                            otherwise.You can use python startNSQ_Service.py to
                            start it manually. We also suggest start it manually
                            since the message might be noisy otherwise
      -r, --real_life       choose run use real-life simulation instead ofbacking
                            up the queue to start with
    ```
    The usage function is rather clear. Here are few examples and explanation regarding the running of the driver
    *  $ python main.py run
        ```
        This is the simplest version, run everything use default value
        ```
    *  $ python main.py run -nt 3 -nm 10000 -nv 100 -ui 60 -nsq -r
        ```
        This means
        Start nsq for me
        Using real-life simulation (produce and consume at same time)
        10,000 messages to be produced
        for 100 videos
        using 3 threads for consumer, 3 threads for producer, one for updater
        ```
    *  one can also easily run Unittests using the driver
        ```
        $ python main.py runTests
        ```
        you can also run individual or all tests using python unittests module
        ```
        $ python -m  unittest discover test_dir -v
        ```


________________


### Demo & Analysis
Demo and analysis for two simulation runs and its corresponding unittests

##### Basic Backed-up Queue Version

###### Demo
This is the simulation version where all messages are backed up initially on the queue
```
python main.py run -nm 10000
```
![alt text](https://www.dropbox.com/s/5bczfwgf7ozpoap/wistia_3.png?raw=1 "Logo Title Text 1")
![alt text](https://www.dropbox.com/s/7ho9sg2trikzz91/wistia_4.png?raw=1 "Logo Title Text 1")

*  you should observe that the PlayCounts table is updating real-time for small counts
*  you should see very intuitive messages printed out to terminal (in a rather submissive manner)
*  you should observe the performance measure
    * real-time consumption time is the consumption time for the most recent message consumed
    * average is the average time
    * For the backed up version, the consumption time plot is a straight line for obvious reasons


###### UnitTest
you will be able to run all unittests after you see the All Consumed message from the terminal
```
(NSQ_Stress_Test)  ✝  ~/Desktop/NSQ_Stress_Test  python main.py runTests
Running Unittest for you my MASTER
All unittestcase classes are locatedin /test_dir, be sure to have a successful consumptiong process to ensure test_processor do its job, otherweise,correctness tests are skipped

test_prohibt_from_initialization (test_client_unittest.TestClient) ...
TestClient
ok
test_update_counts (test_client_unittest.TestClient) ...
TestClient
ok
test_should_create_msgs (test_playproducer_unittest.TestPlayProducer) ...
TestPlayProducer
ok
test_client_has_correct_count (test_proccessor_unittest.TestProccsor) ... TestProccsor
ok
test_messages_should_be_all_consumed (test_proccessor_unittest.TestProccsor) ... TestProccsor
ok
test_proccessor_has_correct_count (test_proccessor_unittest.TestProccsor) ... TestProccsor
ok
test_prohibt_from_initialization (test_proccessor_unittest.TestProccsor) ... TestProccsor
ok

----------------------------------------------------------------------
Ran 7 tests in 0.181s

OK
```

##### Real-Life Version Simulation
###### Demo
This is the simulation where we start the producer (produce messages to the queue) and
consumer at the same time. The way i implemented it is actually first put all messages in a dummy queue
the a producer/consumer will take message from that queue to produce to the queue where the processor then consumes
```
python main.py -nm 10000 -r
```
![alt text](https://www.dropbox.com/s/g21b0dbgr50s299/wistia_5.png?raw=1 "Logo Title Text 1")
![alt text](https://www.dropbox.com/s/fa79b5l708y2jqi/wistia_6.png?raw=1 "Logo Title Text 1")

* You can observe terminal printed out useful messages(in a submissive manner) to indicate the configuration of this run
* PlayCounts table act similar to last basic simulation
* The real difference is the consumption time, as you can see, the message now spends much less time in the queue

###### UnitTests
Same as last one

_______________

### Design & Implementation

###### Program
The design is fully OOP and consists of 3 parts
* PlayProducer
    * generate messages and uuids to put into the initial NSQ queue
    * also responsible for reset queues and __client__ database (by calling client methods)
    * This class cannot be instantiated
* Processor
    * process the message from the queue
    * now if it's the real-life version simulation, processor will also spin up a producer/consumer to read Message from initial dummy queue
    and put it to the real consumption queue without any transformation
    * keeps a Python Dictionary (as class variable) as the source of truth for play counts
    * responsible for publishing the counts to client (invoking methods on client)
    * This class cannot be instantiated
* Client
    * This is a fairly complex implementation i have here, but i think it's nice to have a front-end app to monitor everything
    * Client consists of
        * a Django app to display counts and performance measure
        * a class to called Client to control the Django models via ORM (invoked by publishing method from Processor and reset from PlayProducer)

The detailed documentation can be seen in the code itself

###### Unittest
This program is written in a fairly test-driven manner with one complication that i cannot really start the process of NSQ from a unittest in python.
So to test the correctness of the processor (messages all consumed? counts eventually persistent?), i output a log file each time for each simulation.
and some cases of  unittests for processor is based on that file. When the file is not populated correctly (does not contain all the json strings it requires), it
will skip corresponding test cases
All the test cases classes are located in the test_dir folder.

*  Test Processor - 4 tests
*  Test Client  - 2 tests
*  Test PlayProducer - 1 test

###### NOTES FYI
The Sqlite database i used is not optimized(actually terrible) for multi-threading usage. It might lock the database if you try to use too many threads. When that happens
__Simply restart the local server__
