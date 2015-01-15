#!/usr/bin/env python
from subprocess import Popen, PIPE, STDOUT
from LOGtailer import LogWatcher

LOG_PATH = '/log/collector/'
#LOG_PATH = '/usr/local/lib64/ganglia/gmetric/'
LOG_PATTERN = 'retrying...'

def callback(filename, lines):
    global LOG_PATTERN

    count = 0
    for line in lines:
        if line.find(LOG_PATTERN) != -1:
            count += 1
    print count
    #send by gmetric
    p = Popen(['/usr/local/bin/gmetric','-n','fds_collector_append_fail',
        '-v',str(count),'-t','uint8','-s','both','-x','300','-g','FDS_log','-T','fds collector failed with append hang','-u','Count'],stdout=PIPE,stderr=PIPE)
    result = p.stdout.read() 
    if result:
        print result
    result_err = p.stderr.read()
    if result_err:
        print result_err

if __name__ == '__main__':
    watcher = LogWatcher(LOG_PATH, callback)
    watcher.loop(300)
