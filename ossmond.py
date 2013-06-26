#! /usr/bin/python
# -*- coding: utf-8 -*-

# Author: HC

#Proj: OneSystemShop
#Monitoring daemon

"""

OSS Daemon

Processes requests to individual hosts:
  Performs monitoring requests to hosts,
  Performs trending requests to hosts,
  Performs configuration push to hosts.

"""

__version__ = "0.0.1"


import sys
import time
import threading
import datamodels
import rpyc
import logging
import pickle
from daemon import Daemon
from cfgloader import DBCFGLoader, ReadMONConfig
from pyPgSQL import PgSQL

global conn

def startlog(MONconfig) :
    """Starts logging facilities."""
    
    logging.basicConfig(filename=MONconfig.getMONlog()['logfile'], format='%(asctime)s - %(name)s - %(levelname)s: %(message)s', level=MONconfig.getMONlog()['loglevel'])
    logging.info("Starting logging facilities.")
    
def startDBcon() :
    """ Starts connection to DB."""
    
    global conn
    try :
        conninfo = DBCFGLoader()
        conninfo.readDBconfig()
        conninfo = conninfo.getDBconfig()
    except Exception, e :
        logging.fatal
        conn = PgSQL.connect(host=conninfo['hostname'], user=conninfo['user'], password=conninfo['password'], database=conninfo['db'])
        return conn
    except Exception, e :
        logging.fatal(e)
        
def submitcheck(hostname, ip, checks) :
    checks = pickle.Unpickler(checks)
    for n in checks :
        pass
    incomingdata = datamodels.DataMon(hostname, ip, checks)
    AsyncInsert(conn, incomingdata)

def AsyncInsert(conn, incomingdata) :
    """DB Insert.
    
    Handles async insterts in the DB:

    """
    
    cur = conn.cursor()
    
    for n in self.data.getlistchecks() :
        try :
        # TO-DO, move this SQL Query to a function
            self.cur.execute("UPDATE table mon_status \
                SET check_result = %(check_status)03d, check_summary = %(check_summary)s \
                WHERE host_name = %(hostname)s AND ip = %(ip)s AND check_name = %(check_name)s ;\
            INSERT INTO mon_status (host_name, ip, check_name, check_result, check_summary) \
                VALUES(%(hostname)s, %(ip)s, %(check_name)s, %(check_status)03d, %(check_summary)s);", n)
        except Exception, e :
            #log if problem happened
            logging.exception(e)

    
class OSSRpc(rpyc.Service) :
    global conn
    
    def on_connect(self):
        # code that runs when a connection is created
        # (to init the serivce, if needed)
        pass

    def on_disconnect(self):
        # code that runs when the connection has already closed
        # (to finalize the service, if needed)
        pass
        
    def exposed_submitcheck(self, hostname, ip, checks):
        submitcheck(hostname, ip, checks)
    

class OSSMondThread(threading.Thread) :
    
    def __init__(self, conn) :
        threading.Thread.__init__(self)
        self.conn = conn

    def run(self) :
        #To-Do: Might be meaningful to have debug info for start
        logging.debug("Invoking main thread.")
        from rpyc.utils.server import ThreadPoolServer
        thmain = ThreadPoolServer(OSSRpc, port = 20200, nbThreads = 100)
        thmain.start()

    
class OSSMondCommand(threading.Thread) :
    
    def __init__(self, conn) :
        threading.Thread.__init__(self)
    
    def run(self) :
        #To-Do: Might be meaningful to have debug info for start
        logging.debug("Invoking secondary thread.")
        sendCommand(self)
        
    def sendCommand(self) :
        global conn
        import rpyc
        logging.info("Starting thread to send commands.")
        
        while True :
            try :
                cur = conn.cursor()
            except Exception, e :
                logging.fatal("Connection to DB has been closed.")
                conn = startDBcon()
            logging.info("Checking for commands to execute.")
            cur = conn.cursor()
            cur.execute("select * from mon.mon_commands;")
            commandlist = cur.fetchall()
            cur.close()
            logging.debug(commandlist)
            bgthreads = []
            for n in commandlist :
                #for each host we are creating a new RPC connection
                clientconn = rpyc.connect(commandlist['hostname'], 20220)
                #and for each connection, a new async thread to handle the request
                bgthreads.append(rpyc.async(clientconn.modules.getallchecks))
            for m in bgthreads :
                bgthreads[m].start()
            while len(bgthreads) > 0 :
                for n in bgthreads :
                    # if thread is ready with result
                    if bgthreads[n].ready :
                        # and not in error
                        if not bgthreads[n].error :
                            bgthreads[n].stop()
                            del(bgthreads[n])
                        elif bgthreads[n].error :
                            logging.warning("Error processing: " + bgthreads[n].value)
                            del(bgthreads[n])
                cur.close()
                time.sleep(5)
            time.sleep(30)

class oss_mond(Daemon) :
    """Main class to spawn discrete threads."""
    
    def run(self):
        global conn
        conn = startDBcon()
        threads = []
        try :
            th1 = OSSMondThread(conn)
            th2 = OSSMondCommand(conn)
        except Exception, e :
            logging.exception(e)
        logging.info("Starting main threads.")
        th1.start()
        th2.start()
        threads.append(th1)
        threads.append(th2)
        for t in threads :
            t.join()

 
if __name__ == "__main__":
    MONconfig = ReadMONConfig()
    MONconfig.readconfig()
    daemon = oss_mond(MONconfig.monpidfile)
    if len(sys.argv) == 2:
            if 'start' == sys.argv[1]:
                    startlog(MONconfig)
                    startDBcon()
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