#!/usr/bin/env python
from subprocess import Popen, PIPE, STDOUT
from LOGtailer import LogWatcher

LOG_PATH = '/var/log/cron'
LOG_PATTERN = 'FAILED'

def callback(filename, lines):
    global LOG_PATTERN

    count = 0
    for line in lines:
        if line.find(LOG_PATTERN) != -1:
            count += 1
    print count
    #send by gmetric
    p = Popen(['/usr/local/bin/gmetric','-n','crontab_fail',
        '-v',str(count),'-t','uint8','-s','both','-x','1200','-g','FDS_log','-T','Count of failed crontab processes','-u','Count'],stdout=PIPE,stderr=PIPE)
    result = p.stdout.read() 
    if result:
        print result
    result_err = p.stderr.read()
    if result_err:
        print result_err

if __name__ == '__main__':
    watcher = LogWatcher(LOG_PATH, callback, True)
    watcher.loop(1200)
