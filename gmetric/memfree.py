#!/usr/bin/env python
import time
from subprocess import Popen, PIPE, STDOUT
from LOGtailer import LogWatcher

COMMAND = '/usr/bin/free'
METRIC = 'mem_realfree'
CYCLE = 30

if __name__ == '__main__':
    while(1):
        p = Popen(['/usr/bin/free'], stdout=PIPE, stderr=PIPE)
        result = p.stdout.readline()
        total = free = 0
        while result:
            #print result
            strsplit = result.split()
            if strsplit[0] == 'Mem:':
                total = int(strsplit[1])
            if strsplit[0] == '-/+':
                free = int(strsplit[3])
            result = p.stdout.readline()
        #print 'TOT=' + str(total) + ',FREE=' + str(free) + ',%=' + str((float(free)/total)*100)

        #send by gmetric
        p = Popen(['/app/di/monitoring/ganglia/bin/gmetric','-n',METRIC,'-v',str((float(free)/total)*100),'-t','float','-s','both',
            '-x',str(CYCLE),'-g','memory','-T','(free + cache + buffer)/total_mem %','-u','%'],stdout=PIPE,stderr=PIPE)
        result = p.stdout.read()
        if result:
            print result
        result_err = p.stderr.read()
        if result_err:
            print result_err
        time.sleep(CYCLE)
