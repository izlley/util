#!/usr/bin/env python
import re
import os
import time
from subprocess import Popen, PIPE, STDOUT
from datetime import datetime

PLOBLEM = 'echo "***** 1san Nagios *****\n\n-Notification Type: PROBLEM\n\n-Service: TAD_BROCKER_STATE_CHK\n-Host: ISF-TADlogr2\n-Address: 172.19.106.130\n-State: CRITICAL\n\n-Date/Time: ' + str(datetime.now())  + '\n\n-Additional Info:\n\nZookeeper path \"/brokers/ids/2\" is bad\n\n-Notes:\n\nTAD Broker down!\n\n" | /app/run/monitoring/sendEmail/sendEmail -f God@1san-Nagios -s 10.40.30.85:25 -u "** PRLOBLEM Service Alert: ISF-TADlogr2/TAD_BROCKER_STATE_CHK is CRITICAL **" -t 6047@skplanet.com'

RECOVERY = '/usr/bin/printf "%b" "***** 1san Nagios *****\n\n-Notification Type: RECOVERY\n\n-Service: TAD_BROCKER_STATE_CHK\n-Host: ISF-TADlogr2\n-Address: 172.19.106.130\n-State: RECOVERY\n\n-Date/Time: ' + str(datetime.now())  + '\n\n-Additional Info:\n\nZookeeper path "/brokers/ids/2" is good\n\n-Notes:\n\n | /app/run/monitoring/sendEmail/sendEmail -f God@1san-Nagios -s 10.40.30.85:25 -u "** RECOVERY Service Alert: ISF-TADlogr2/TAD_BROCKER_STATE_CHK is OK **" -t 6047@skplanet.com'


if __name__ == '__main__':
#    global PLOBLEM
#    global RECOVERY
    wasBad = False
    while (1):
        p = Popen(['/usr/bin/telnet 172.19.106.130 8651|grep broker'],stdout=PIPE,stderr=PIPE,shell=True)
        m = re.search('(VAL=")([0-9]+)(")',p.stdout.read())
        print m.groups()
        if m.group(2) == '0' and wasBad == False:
            # send email
            print 'send problem mail:' + PLOBLEM 
            Popen([PLOBLEM],stdout=PIPE,stderr=PIPE,shell=True)
            wasBad = True
        elif m.group(2) == '1' and wasBad == True:
            print 'send recovery mail'
            Popen([RECOVERY],stdout=PIPE,stderr=PIPE,shell=True)
            wasBad = False
        time.sleep(600)

