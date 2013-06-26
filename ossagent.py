#! /usr/bin/python
# -*- coding: utf-8 -*-

# Author: HC

#Proj: OneSystemShop
#Local Monitoring daemon
"""

OSS Agent

Handles Check requests.
Handles Configuration deploy,
Handles Trending requests.

"""

__version__ = "0.0.1"


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
from daemon import Daemon
import cfgloader #import AgentConfigLoad
from rpyc.utils.server import ThreadPoolServer
from signal import SIGTERM

def startlog(level) :
    logging.basicConfig(filename="/var/log/oss_agent.log", format='%(asctime)s - %(name)s - %(levelname)s: %(message)s', level=level)
    logging.info("Starting logging facilities.")
    return logging
    
def executecheck(check, checkconf) :
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

    
class OSSMonAgent(threading.Thread) :
    """Agent which processes monitoring requests."""
    
    def __init__(self, config) :
        threading.Thread.__init__(self)
        self.config = config
    
    def run(self) :
        logging.info("Adding " + self.config["plugins"] + " to working directory sert.")
        try :
            sys.path.append(self.config["plugins"])
        except :
            logging.fatal("Could not append plugin directory to working set.")
            os.sys.exit(1)
        plugins = []
        logging.info("MonAgent run")
        for n in os.listdir(self.config["plugins"]) :
            ncfg = os.path.join(self.config["pluginsconf"], os.splitext(os.path.split(n)[1]) + ".cfg")
            if os.path.exists(n) and os.path.exists(ncfg) :
                plugins.append((os.path.join(self.config.plugins,n), ncfg))
            else :
                logging.info("Check plugin and its configuration file. In particular: " + os.path.split(n)[1])
        while True :
            results = []
            for m in plugins :
                try :
                    results.append(executecheck(m))
                except CheckError :
                    syslog.syslog("Check " + os.path.split(m)[1] + "failed to execute." )
                    if self.config.logging :
                        logging.warning(e)
            try :
                clientconn = rpyc.connect(self.config["monmaster"], 20200)
                try :
                    async = rpyc.async(clientconn.modules.submitcheck((socket.gethostname(),socket.gethostbyname_ex(socket.gethostname())[2][0],results)))
                    async.start()
                except :
                    #Call couldn't be done...
                    ### To-Do, extend error output
                    pass
            except :
                logging.info("Failed to contact master server. Sleepting...")
                time.sleep(5)
            time.sleep(self.config['interval'])

class listen(rpyc.Service) :
    
    def on_connect(self):
        
        if config['allowed_hosts'].count(self._conn._channel.stream.sock.getpeername()[0]) > 0:
            pass
        else :
            raise ValueError("Not in allowed host list.")
        # code that runs when the connection has already closed
        # (to finalize the service, if needed)
        

    def on_disconnect(self):
        # code that runs when the connection has already closed
        # (to finalize the service, if needed)
        pass
        
    def exposed_tada(self):
        return self._conn._channel.stream.sock.getpeername()[0]

class OSSAgent(Daemon) :
    """Starts the Agent Daemon and its threads."""
    
    def run(self):
        global config
        global logging
        cfg = cfgloader.AgentConfigLoad()
        cfg.setCFG("/etc/oss/oss_agent.cfg")
        try :
            cfg.readconfig()
        except Exception, e :
            syslog.syslog(str(e))
        config = cfg.getconfig()
        if config == None :
            syslog.syslog("Failed to read configuration file. Exiting...")
            os.sys.exit(1)
        startlog(config['loglevel'])
        threads = []
        th1 = OSSMonAgent(config)
        th2 = ThreadPoolServer(listen, port = config['port'], nbThreads = 10)
        
        logging.info("Starting main threads.")
        th1.start()
        th2.start()
        threads.append(th1)
        threads.append(th2)


if __name__ == "__main__":
    daemon = OSSAgent('/var/run/oss_agent.pid', stderr="/var/log/oss_agent.log")
    if len(sys.argv) == 2:
        if 'start' == sys.argv[1]:
            syslog.syslog('OSS_Agent Starting.')
            try :
                daemon.start()
            except Exception, e:
                syslog.syslog(str(e))
        elif 'stop' == sys.argv[1]:
            syslog.syslog('OSS_Agent stopping.')
            logging.info("OSS Agent shutting down.")
            daemon.stop()
        elif 'restart' == sys.argv[1]:
            syslog.syslog('OSS_Agent restarting.')
            daemon.restart()
        else:
            print "Unknown command"
            sys.exit(2)
        sys.exit(0)
    else:
        print "usage: %s start|stop|restart" % sys.argv[0]
        sys.exit(2)
