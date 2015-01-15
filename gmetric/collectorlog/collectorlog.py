#!/usr/bin/python

import threading
import time
import datetime
from subprocess import Popen, PIPE, STDOUT
from LOGtailer import LogWatcher

exitFlag = 0

TIME_CYCLE_SEC = 600

LOG_INFO = [
    '/data/collector/logs/ading-promo/collector.log',
    '/data/collector/logs/dev-ocb-touch-v5/collector.log',
    '/data/collector/logs/dev-smartwallet-client-v5/collector.log',
    '/data/collector/logs/dev-smartwallet-web-v5/collector.log',
    '/data/collector/logs/is-admin/collector.log',
    '/data/collector/logs/is-merchant-admin/collector.log',
    '/data/collector/logs/ocb-mobile/collector.log',
    '/data/collector/logs/ocb-touch/collector.log',
    '/data/collector/logs/ocb-touch-v5/collector.log',
    '/data/collector/logs/ocb-web/collector.log',
    '/data/collector/logs/oneid/collector.log',
    '/data/collector/logs/pickat-app/collector.log',
    '/data/collector/logs/pickat-web/collector.log',
    '/data/collector/logs/pickatsg-app/collector.log',
    '/data/collector/logs/pickatsg-web/collector.log',
    '/data/collector/logs/pickone/collector.log',
    '/data/collector/logs/search-tstore/collector.log',
    '/data/collector/logs/smartwallet-app-v5/collector.log',
    '/data/collector/logs/smartwallet-client-v5/collector.log',
    '/data/collector/logs/smartwallet-web-dbif-v5/collector.log',
    '/data/collector/logs/smartwallet-web-v5/collector.log',
    '/data/collector/logs/smartwallet-cs1/collector.log',
    '/data/collector/logs/smartwallet-cs2/collector.log',
    '/data/collector/logs/smartwallet-cs3/collector.log',
    '/data/collector/logs/smartwallet-cs4/collector.log',
    '/data/collector/logs/smartwallet-ct1/collector.log',
    '/data/collector/logs/smartwallet-ct2/collector.log',
    '/data/collector/logs/smartwallet-ct3/collector.log',
    '/data/collector/logs/smartwallet-ct4/collector.log',
    '/data/collector/logs/smartwallet-ws1/collector.log',
    '/data/collector/logs/smartwallet-ws2/collector.log',
    '/data/collector/logs/smartwallet-ws3/collector.log',
    '/data/collector/logs/smartwallet-ws4/collector.log',
    '/data/collector/logs/smartwallet-wt1/collector.log',
    '/data/collector/logs/smartwallet-wt2/collector.log',
    '/data/collector/logs/smartwallet-wt3/collector.log',
    '/data/collector/logs/smartwallet-wt4/collector.log',
    '/data/collector/logs/tcoloring/collector.log',
    '/data/collector/logs/tshopping/collector.log',
    '/data/collector/logs/tsports/collector.log',
    '/data/collector/logs/tstore-tlog/collector.log',
    '/data/collector/logs/tstore-iap-encrypt/collector.log',
    '/data/collector/logs/galleon/collector.log',
    '/data/collector/logs/tad-event/collector.log',
    '/data/collector/logs/tad-request/collector.log',
    '/data/collector/logs/ocb-adbag/collector.log',
    '/data/collector/logs/ocb-adbag-dev/collector.log',
    '/data/collector/logs/tbelling/collector.log',
    '/data/collector/logs/tbelling-dev/collector.log',
    '/data/collector/logs/tad-event-bis/collector.log',
    '/data/collector/logs/tad-request-bis/collector.log',
    '/data/collector/logs/smartwallet-syruporder/collector.log',
    '/data/collector/logs/it-logsaver-dlp/collector.log',
    '/data/collector/logs/it-logsaver-paloalto/collector.log',
    '/data/collector/logs/it-logsaver-secudoc/collector.log',
    '/data/collector/logs/it-logsaver-sep/collector.log',
    '/data/collector/logs/search-gifticon/collector.log',
    '/data/collector/logs/search-common-benepia/collector.log',
    '/data/collector/logs/tad-retargeting-dev/collector.log',
    '/data/collector/logs/newtech-server/collector.log',
    '/data/collector/logs/planetground/collector.log',
    '/data/collector/logs/planetground-dev/collector.log',
    '/data/collector/logs/hoppin/collector.log',
    '/data/collector/logs/hoppin-dev/collector.log',
    '/data/collector/logs/tcloud/collector.log',
    '/data/collector/logs/tcloud-dev/collector.log',
    '/data/collector/logs/gifticon/collector.log',
    '/data/collector/logs/gifticon-dev/collector.log',
]

METRIC_NAME = [
    'col-ading-promo',
    'col-dev-ocb-touch-v5',
    'col-dev-smartwallet-client-v5',
    'col-dev-smartwallet-web-v5',
    'col-is-admin',
    'col-is-merchant-admin',
    'col-ocb-mobile',
    'col-ocb-touch',
    'col-ocb-touch-v5',
    'col-ocb-web',
    'col-oneid',
    'col-pickat-app',
    'col-pickat-web',
    'col-pickatsg-app',
    'col-pickatsg-web',
    'col-pickone',
    'col-search-tstore',
    'col-smartwallet-app-v5',
    'col-smartwallet-client-v5',
    'col-smartwallet-web-dbif-v5',
    'col-smartwallet-web-v5',
    'col-smartwallet-cs1',
    'col-smartwallet-cs2',
    'col-smartwallet-cs3',
    'col-smartwallet-cs4',
    'col-smartwallet-ct1',
    'col-smartwallet-ct2',
    'col-smartwallet-ct3',
    'col-smartwallet-ct4',
    'col-smartwallet-ws1',
    'col-smartwallet-ws2',
    'col-smartwallet-ws3',
    'col-smartwallet-ws4',
    'col-smartwallet-wt1',
    'col-smartwallet-wt2',
    'col-smartwallet-wt3',
    'col-smartwallet-wt4',
    'col-tcoloring',
    'col-tshopping',
    'col-tsports',
    'col-tstore-tlog',
    'col-tstore-iap-encrypt',
    'col-galleon',
    'col-tad-event',
    'col-tad-request',
    'col-ocb-adbag',
    'col-ocb-adbag-dev',
    'col-tbelling',
    'col-tbelling-dev',
    'col-tad-event-bis',
    'col-tad-request-bis',
    'col-smartwallet-syruporder',
    'col-it-logsaver-dlp',
    'col-it-logsaver-paloalto',
    'col-it-logsaver-secudoc',
    'col-it-logsaver-sep',
    'col-search-gifticon',
    'col-search-common-benepia',
    'col-tad-retargeting-dev',
    'col-newtech-server',
    'col-planetground',
    'col-planetground-dev',
    'col-hoppin',
    'col-hoppin-dev',
    'col-tcloud',
    'col-tcloud-dev',
    'col-gifticon',
    'col-gifticon-dev',
]

class myThread (threading.Thread):
    def __init__(self, threadID, path, metric, cycle):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.path = path
        self.metric = metric
        self.cycle = cycle
        self.errcnt = 0
    def run(self):
        #print self.metric + ', ' + self.path + ', ' + str(self.errcnt) + ' ,' + str(self.cycle) + ' ,' + str(self.threadID)
        watcher = LogWatcher(self.path, self.callback, True)
        watcher.loop(self.cycle)
        print "Exiting " + self.threadID

    def callback(self, filename, lines):
        self.errcnt = 0
        if lines != '':
            for line in lines:
                if len(line.split()) > 2:
                    if line.split()[2] == 'ERROR':
                        self.errcnt += 1; 
        print str(datetime.datetime.now()) + '>' + str(self.errcnt) + ' : ' + self.metric + ', ' + self.path + ' ,' + str(self.threadID)

        #send by gmetric
        p = Popen(['/app/run/monitoring/ganglia/bin/gmetric', '-n',self.metric, '-v',str(self.errcnt),
                '-t', 'uint8', '-s', 'both', '-x', str(self.cycle), '-g', 'collector', '-T', self.metric, '-u', 'Count'],
                stdout=PIPE,stderr=PIPE)
        result = p.stdout.read()
        if result:
            print result
        result_err = p.stderr.read()
        if result_err:
            print result_err

def print_time(threadName, delay, counter):
    while counter:
        if exitFlag:
            thread.exit()
        time.sleep(delay)
        print "%s: %s" % (threadName, time.ctime(time.time()))
        counter -= 1

if __name__ == '__main__':
    # Create new threads
    threads = []
    i = 0
    for path, metric in zip(LOG_INFO, METRIC_NAME):
        threads.append( myThread(i+1, path, 'errcnt_' + metric, TIME_CYCLE_SEC) )
        i += 1

    # Start new Threads
    for thread in threads:
        #print str(thread.threadID) + ', ' + thread.path
        thread.start()

    print "Exiting Main Thread"

