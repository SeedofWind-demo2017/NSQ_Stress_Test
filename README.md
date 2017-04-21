# Fun with NSQ

----

### Installation
Since i used django to implement the client and python to write the processor, it will require a little bit effort to setup the virtualenv before you can run this __exciting__ program. Everything is wrapped inside virtualenv, so i promise it will be easy enough for you to get this rolling
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
    eg. (wistia)  ✝  ~/Desktop/wistia 
    ```
4. install all packages inside virtualenv
    ```
    $ pip install -r requirements.txt

    be sure to run this without sudo, so it won't mess up your global python env
    ```
5. setup django
    ```
    You might need to set DJANGO modules by

    $ export DJANGO_SETTINGS_MODULE=video_distributor.settings

    be sure now you at the root level of project folder

    $ python video_distributor/manage.py migrate

    ```
6. run client(django local) server
    ```
    $ python video_distributor/manage.py runserver

    System check identified no issues (0 silenced).
    April 16, 2017 - 13:51:39
    Django version 1.8, using settings 'video_distributor.settings'
    Starting development server at http://127.0.0.1:8000/
    Quit the server with CONTROL-C.
    ```
7. go to the localshot address specified in the terminal and you should be able to see something like this (table will be empty)
![alt text](https://www.dropbox.com/s/595kdzau4ntcna1/nsq_admin2.png?raw=1 "Logo Title Text 1")
![alt text](https://www.dropbox.com/s/eigstjholw486sn/nsq_admin1.png?raw=1 "Logo Title Text 1")


Now you are ready to run the program

____________________

### Functionalities & Usage
Before getting to the demo part, let's go through the functionalities achieved and their usages

###### Functionalities
Achieved basic requirements and extra functionalities(marked by __etra__)
1. Simulation program can put specified number of messages(_default 10,000_) on the initial queue for specified number of videos(_default 100_) via __PlayProducer__.
    * each message in the queue is a JSON string has a GUID video_id attribute
    * (__extra__) each message tracks a enqueue time for pormance analysis
    * (__extra__) user can specify how many messages and how many video(uuids) for the present simulation at run time
2. Simulation Program  utilizes  __processor__ to
    * read each message off the queue, updating the play count of the respective video, and publishing the result to the client.
    * For videos with 100 less plays, their stats are published to client at real time
    * For videos with 100 or more plays, their stats are published to the client with user specified interval
    * (__exra__) user can specify pusblish_interval at run time
    * Each time the __processor__ publishes (i.e. makes a call to) to the __client__, it can provide updated play counts for at most _20 videos_ in a single message.
    * An updated play count for a video will only be published to the client if the play count for that video has changed since it was last published.
    * (__extra__)user can run the simulation in a real-life fashion at run time where
        * instead of all messages are initially backed up in the queue (default behavior), producer and consumer are spinned up at the same time
        * this is much more real-life  and gives us better idea how the processor performs
        * (__extra__) user can specify the _producer/consumer ratio_ for real-life simulation at run time
    * (__extra__) user can specify how many consumer threads to use at run time
    * (__extra__) user can start the nsq service automatically via the driver program
3. Simulation Program utilizes __client__ to
    * Display the play counts published from __processor__
    * (__extra__) Measure the real-time and average consumption time via dashboard
    * (__extra__)The *client* is a very user-friendly django web-app(dashboard) to view real-time counts and performance measure
    * (__extra__)The *client* is automatically updating counts (real-time display) except the charts (too large). You will see what i'm talking about in the demo part
4. (__extra__) All unittests can be found in the test_dir, this program is also written in a (almost) test-driven fashion. I will discuss how to run the unittests and what it covers in a sec
    *  The tests for processor are a bit unique since it relies on the output of a simulation. Since the NSQ control is not low-level enough for me to signal outiside of the main thread
    * So the tests for processor should be run after a simulation. it will skip some test cases(correctness for simulation) otherwise

###### Usage
1. Start nsq service.
This step __can be skipped__ if you choose to use the main driver to start nsq automatically. however, i donot suggest doing that since it will make the stdout quite noisy and messy. So follow this flow initially perhaps?
```
$ pytho startNSQ_Service.py
```
2. start the django client
    ```
    $ python video_distributor/manage.py runserver

    System check identified no issues (0 silenced).
    April 16, 2017 - 13:51:39
    Django version 1.8, using settings 'video_distributor.settings'
    Starting development server at http://127.0.0.1:8000/
    ```
    go to the localhost address specified in the terminal and you should be able to see something like this (table will be empty)
    ![alt text](https://www.dropbox.com/s/595kdzau4ntcna1/nsq_admin2.png?raw=1 "Logo Title Text 1")
    ![alt text](https://www.dropbox.com/s/eigstjholw486sn/nsq_admin1.png?raw=1 "Logo Title Text 1")
3. Now we are ready to run the driver, you can invoke -h to see the usages function
    ```
    (wistia)  ✝  ~/Desktop/wistia  python main.py -h
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
      -nsq, --start_nsq     choose to start nsq for automatically, will require the
                            service to be started manually otherwise by using
                            python startNSQ_Service.py. We suggest start
                            it manually since the message might be noisy if we
                            start it for you here
      -r, --real_life       choose to use real-life simulation instead ofbacking
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
![alt text](https://www.dropbox.com/s/ablzhpcm3w6s0a7/nsq_basic1.png?raw=1 "Logo Title Text 1")
![alt text](https://www.dropbox.com/s/7dwxdvnkig3xr82/nsq_basic2.png?raw=1 "Logo Title Text 1")

*  you should observe that the PlayCounts table is updating real-time for small counts
*  you should see very intuitive messages printed out to terminal (in a rather submissive manner)
*  you should observe the performance measure
    * real-time consumption time is the consumption time for the most recent message consumed
    * average is the average time
    * For the backedup version, the consumption time plot is a straight line for obvious reasons


###### UnitTest
you will be able to run all unittests after you see the All Consumed message from the terminal
```
(wistia)  ✝  ~/Desktop/wistia  python main.py runTests
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
the a producer/consumer will take message from that queue to produce to the queue where the proccessor then consumes
```
python main.py -nm 10000 -r
```
![alt text](https://www.dropbox.com/s/omu7d9dpk6lyuva/nsq_real1.png?raw=1 "Logo Title Text 1")
![alt text](https://www.dropbox.com/s/9gfqkh1is3nrklr/nsq_real2.png?raw=1 "Logo Title Text 1")

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
    * This class is initializable
* Processor
    * process the message from the queue
    * now if it's the real-life version simulation, processor will also spin up a producer/consumer to read Message from initial dummy queue
    and put it to the real consumption queue without any transformation
    * keeps a Python Dictionary (as class variable) as the source of truth for playcounts
    * responsible for publishing the counts to client (invoking methods on client)
    * This class is not initializable
* Client
    * This is a fairly complex implementation i have here, but i think it's nice to have a front-end app to monitor everything
    * Client consists of
        * a django app to display counts and performance measure
        * a class to called Client to control the django models via ORM (invoked by publishing method from Proccesor and reset from PlayProducer)

The detailed documentation can be seen in the code itself

###### Unittest
This program is written in a fairly test-driven manner with one complication that i cannot really start the process of NSQ from a unittest in python.
So to test the correctness of the processor (messages all consumed? counts eventually persistent?), i output a log file each time for each simulation.
and some cases of  unittests for processor is based on that file. When the file is not populated correctly (does not contain all the json strings it requries), it
will skip corresponding test cases
All the test cases classes are located in the test_dir folder.

*  Test Processor - 4 tests
*  Test Client  - 2 tests
*  Test PlayProducer - 1 test

###### NOTES FYI
The Sqllite database i used is not optimized(actually terrible) for multi-threading usage. It might lock the database if you try to use too many threads. When that happens
__Simply restart the local server__


______________


### Post Mortem
###### Had fun with NSQ
First i have to say, it's a fun project to do. I was not familiar with NSQ. It has some rather interesting design. 
compared to other brokers like RabbitMQ. Nsq is
* designed with distributed feature in mind, this allows it to achieve rather good processing speed easily
* very nice publish-subscribe model and thanks to this design, it seems can achieve much better availability compared to rabbit
* ridiculously easy to setup
* The only thing i might __complain__ is the Python library is not really low-level enough
###### Things I learnt
* Learnt how to use NSQ
* Had a more in-depth look at Python multi-threading. Now due to the global lock, python is not really performant when it comes to multi-threading. In this case for a global dictionary, it is automatically thread-safe. You can see i manually implemented a lock. It's just for peace of mind
There are ways to achive a better performance in terms of multi-threading in python which i will discuss later

###### Things i would do differently & Possible Improvements
Given the limited time i have, i am __fairly satisfied__ with what i have here. However, quite a few improvements can be done to this program
*  Use __react/angular__ to achieve component loading at client side
    * You might observe the django app at the client side is not too responsive, this is because under the hood it's firing off AJAX calls to update the table and charts
    * A much better way is to use something like react to update individual component via a api call to signal the database model change

*  Get better multi-threading performance
    * Like i mentioned, it's not really performant to run multi-threading due to the global interpreter lock
    * One option is to use a different implementation of Python, like Jython or IronPython. That way, you still get the benefits of having the Python language without having to deal with the GIL. However, you wouldn't have the ability to use the CPython-only libraries.

*  This is __far beyond the scope__, but it will be extra fun to make it more real-life. That is to host NSQ on server(s) and simulate a real Async Task processing workflow. NSQ is optimized for multi-node processing. So this is the only one to do it a solid
