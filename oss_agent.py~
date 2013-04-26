#! /usr/bin/python
# -*- coding: utf-8 -*-

# Author: HC

#Proj: OneSystemShock
#Local Monitoring daemon

import sys
import os
import time
import threading
import datamodels
import rpyc
import syslog
import ConfigParser
import logging
import atexit
import ast
import socket
import subprocess
from Daemon import Daemon
from CFGLoader import AgentConfigLoad
from signal import SIGTERM

syslog.syslog('OSS_Agent starting.')

def startlog(level) :
    logging.basicConfig(filename="/var/log/oss_agent.log", format='%(asctime)s - %(name)s - %(levelname)s: %(message)s', level=level)
    logging.info("Starting logging facilities.")
    
def requestcheck(check, checkconf) :
    try :
        result = subprocess.check_call([check, checkconf]) 
    except CalledProcessError, e:
        syslog.syslog("Check " + check + " failed.")
        return DataCheck(check,2, e)
    try :
        DataCheck(result)
    except :
        pass
    if isinstance(DataCheck, result) :
        return result
    else :
        syslog.syslog("Check " + check + " does not return valid object.")
        return DataCheck(check, 2, "Check " + check + " does not return valid object.")
    
    
class oss_monagent(threading.Thread) :
    def __init__(self, config) :
        threading.Thread.__init__(self)
        self.config = config
    
    def run(self) :
        sys.path.append(self.config.plugins)
        plugins = []
        for n in os.listdir(self.config.plugins) :
            ncfg = os.path.join(self.config.pluginsconf, os.splitext(os.path.split(n)[1]) + ".cfg")
            if os.path.exists(n) and os.path.exists(ncfg) :
                plugins.append((os.path.join(self.config.plugins,n), ncfg))
            else :
                syslog.syslog("Check plugin and its configuration file. In particular: " + os.path.split(n)[1])
        while True :
            results = []
            for m in plugins :
                try :
                    results.append(requestcheck(m))
                except CheckError :
                    syslog.syslog("Check " + os.path.split(m)[1] + "failed to execute." )
                    if self.config.logging :
                        logging.warning(e)
            clientconn = rpyc.connect(self.config.monmaster, 20200)
            async = rpyc.async(clientconn.modules.submitcheck((socket.gethostname(),socket.gethostbyname_ex(socket.gethostname())[2][0],results)))
            async.start()
            time.sleep(self.config.interval)

class oss_agent(Daemon) :
    def run(self):
        config = AgentConfigLoad()
        config.readconfig()
        threads = []
        try :
            th1 = oss_monagent(config)
            th2 = oss_mondCommand(conn)
        except Exception, e :
            logging.exception(e)
        logging.info("Starting main threads.")
        th1.start()
        th2.start()
        threads.append(th1)
        threads.append(th2)


if __name__ == "__main__":
    daemon = oss_agent('/var/run/oss_agent.pid')
    if len(sys.argv) == 2:
        if 'start' == sys.argv[1]:
            daemon.start()
        elif 'stop' == sys.argv[1]:
            daemon.stop()
        elif 'restart' == sys.argv[1]:
            daemon.restart()
        else:
            print "Unknown command"
            sys.exit(2)
        sys.exit(0)
    else:
        print "usage: %s start|stop|restart" % sys.argv[0]
        sys.exit(2)
