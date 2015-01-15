#!/usr/bin/env python
import time
from subprocess import Popen, PIPE, STDOUT
from LOGtailer import LogWatcher

LOG_PATH = '/data/kafka/logs/error.log'

LOG_PATTERN = {
    'broker_error_cnt':[0,'ERROR','TAD_log','fds tad broker error.log count']
}

def callback(filename, lines):
    global LOG_PATTERN

    for value in LOG_PATTERN.itervalues():
        value[0] = 0

    for line in lines:
        for key in LOG_PATTERN:
            if line.find(LOG_PATTERN[key][1]) != -1:
                LOG_PATTERN[key][0] += 1
                print LOG_PATTERN[key][0]

    for key in LOG_PATTERN:
        print key + ':' + str(LOG_PATTERN[key][0])

    #send by gmetric
    for key in LOG_PATTERN:
        p = Popen(['/app/hadoop/monitoring/ganglia/bin/gmetric','-n',key,'-v',str(LOG_PATTERN[key][0]),'-t','uint8','-s','both',
            '-x','600','-g',LOG_PATTERN[key][2],'-T',LOG_PATTERN[key][3],'-u','Count'],stdout=PIPE,stderr=PIPE)
        result = p.stdout.read()
        if result:
            print result
        result_err = p.stderr.read()
        if result_err:
            print result_err
    time.sleep(300)
    #rollback
    for key in LOG_PATTERN:
        p = Popen(['/app/hadoop/monitoring/ganglia/bin/gmetric','-n',key,'-v', '0','-t','uint8','-s','both',
            '-x','600','-g',LOG_PATTERN[key][2],'-T',LOG_PATTERN[key][3],'-u','Count'],stdout=PIPE,stderr=PIPE)
        result = p.stdout.read()
        if result:
            print result
        result_err = p.stderr.read()
        if result_err:
            print result_err

if __name__ == '__main__':
    watcher = LogWatcher(LOG_PATH, callback, True)
    watcher.loop(600)
