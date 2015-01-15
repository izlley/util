#!/usr/bin/python

import os
import pwd
import re
import signal
import subprocess
import sys
import time
from subprocess import Popen, PIPE, STDOUT

# java com.skplanet.monitoring.jmx.jmxprobe Kafka SocketServerStats
# If this user doesn't exist, we'll exit immediately.
# If we're running as root, we'll drop privileges using this user.
USER = "hadoop"

JMX_TOOL_PATH = "./jmxprobe-0.0.1.jar"

# We add those files to the classpath if they exist.
CLASSPATH = [
    os.environ['JAVA_HOME']+'/lib/tools.jar',
    '/app/hadoop/monitoring/gan_mod/gmetric/jmxprobe-0.0.1.jar',
    '.' 
]

# Map certain JVM stats so they are unique and shorter
GANGLIA_GRP = {
  "HeapMemoryUsage": "jvm",
  "NonHeapMemoryUsage": "jvm",
  "Usage": "jvm",
  "ProduceRequestsPerSecond": "broker",
  "FetchRequestsPerSecond": "broker",
  "AvgProduceRequestMs": "broker",
  "MaxProduceRequestMs": "broker",
  "AvgFetchRequestMs": "broker",
  "MaxFetchRequestMs": "broker",
  "BytesReadPerSecond": "broker",
  "BytesWrittenPerSecond": "broker",
  "NumFetchRequests": "broker",
  "NumProduceRequests": "broker"
}

# How many times, maximum, will we attempt to restart the JMX collector.
# If we reach this limit, we'll exit with an error.
MAX_RESTARTS = 10

TOP = False  # Set to True when we want to terminate.
RETVAL = 0    # Return value set by signal handler.


def drop_privileges():
    try:
        ent = pwd.getpwnam(USER)
    except KeyError:
        print >>sys.stderr, "Not running, user '%s' doesn't exist" % USER
        sys.exit(13)

    if os.getuid() != 0:
        return

    os.setgid(ent.pw_gid)
    os.setuid(ent.pw_uid)


def kill(proc):
  """Kills the subprocess given in argument."""
  # Clean up after ourselves.
  proc.stdout.close()
  rv = proc.poll()
  if rv is None:
      os.kill(proc.pid, 15)
      rv = proc.poll()
      if rv is None:
          os.kill(proc.pid, 9)  # Bang bang!
          rv = proc.wait()  # This shouldn't block too long.
  print >>sys.stderr, "warning: proc exited %d" % rv
  return rv


def do_on_signal(signum, func, *args, **kwargs):
  """Calls func(*args, **kwargs) before exiting when receiving signum."""
  def signal_shutdown(signum, frame):
    print >>sys.stderr, "got signal %d, exiting" % signum
    func(*args, **kwargs)
    sys.exit(128 + signum)
  signal.signal(signum, signal_shutdown)


def main(argv):
    drop_privileges()
    jar = os.path.normpath(JMX_TOOL_PATH)
    if not os.path.exists(jar):
        print >>sys.stderr, "WTF?!  Can't run, %s doesn't exist" % jar
        return 13
    classpath = [jar]
    for jar in CLASSPATH:
        if os.path.exists(jar):
            classpath.append(jar)
    classpath = ":".join(classpath)

    jmx = subprocess.Popen(
        ["java", "-enableassertions", "-enablesystemassertions",  # safe++
         "-Xmx64m",  # Low RAM limit, to avoid stealing too much from prod.
         "-cp", classpath, "com.skplanet.monitoring.jmx.jmxprobe",
         "--watch", "10", "--long", 
         "Kafka",  # Name of the process.
         # The remaining arguments are pairs (mbean_regexp, attr_regexp).
         # The first regexp is used to match one or more MBeans, the 2nd
         # to match one or more attributes of the MBeans matched.
         "Memory", "Heap",                     # All HBase / hadoop metrics.
         "MemoryPool", "^Usage$",       # Number of threads and CPU time.
         "SocketServerStats", "",    # Number of open files.
         ], stdout=subprocess.PIPE, bufsize=1)
    do_on_signal(signal.SIGINT, kill, jmx)
    do_on_signal(signal.SIGPIPE, kill, jmx)
    do_on_signal(signal.SIGTERM, kill, jmx)
    try:
        prev_timestamp = 0
        while True:
            line = jmx.stdout.readline()

            metric, value, mbean = line.split("\t", 2)
            if metric in GANGLIA_GRP:
                if GANGLIA_GRP[metric] == 'jvm':
                    if metric == 'Usage':
                        metric = re.search('.*name=(.*)',mbean).group(1)
                        metric = metric.lower()
                        metric = metric.replace(' ','_')
                        value = re.search('.*committed=(\d+).*',value).group(1)
                        Popen(['/app/hadoop/monitoring/ganglia/bin/gmetric','-n','broker_'+metric,'-v',
                            value,'-t','float','-s','both','-x','10','-g','jvm',
                            '-u','float'])
                    else:
                        metric = metric.lower()
                        metric = metric.replace(' ','_')
                        value = re.search('.*committed=(\d+).*',value).group(1)
                        Popen(['/app/hadoop/monitoring/ganglia/bin/gmetric','-n','broker_'+metric,'-v',
                            value,'-t','float','-s','both','-x','10','-g','jvm',
                            '-u','float'])
                    #print '##'+metric+','+value
                else:
                    Popen(['/app/hadoop/monitoring/ganglia/bin/gmetric','-n',metric.lower(),'-v',
                        value,'-t','float','-s','both','-x','10','-g',GANGLIA_GRP[metric],
                        '-u','float'])
                    #print '##'+metric+','+value

            sys.stdout.flush()
    finally:
        kill(jmx)
        time.sleep(300)
        return 0  # Ask the tcollector to re-spawn us.


if __name__ == "__main__":
    sys.exit(main(sys.argv))
