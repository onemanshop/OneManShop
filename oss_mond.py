#! /usr/bin/python
# -*- coding: utf-8 -*-

# Author: HC

#Proj: OneSystemShock
#Monitoring daemon

import sys
import time
import threading
import datamodels
import rpyc
import logging
from Daemon import Daemon
from CFGLoader import DBCFGLoader, readMONconfig
from pyPgSQL import PgSQL

global conn

def startlog(MONconfig) :
    logging.basicConfig(filename=MONconfig.getMONlog()['logfile'], format='%(asctime)s - %(name)s - %(levelname)s: %(message)s', level=MONconfig.getMONlog()['loglevel'])
    logging.info("Starting logging facilities.")
    
def startDBcon() :
    global conn
    
    try :
        conninfo = DBCFGLoader()
        conninfo.readDBconfig()
        conninfo = conninfo.getDBconfig()
        conn = PgSQL.connect(host=conninfo['hostname'], user=conninfo['user'], password=conninfo['password'], database=conninfo['db'])
        return conn
    except Exception, e :
        logging.fatal(e)

class AsyncInsert(threading.Thread) :
    def __init__(self,conn,incomingdata) :
        self.cur = conn.cursor()
        self.data = incomingdata
    
    def run(self) :
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

##def incomdata() :
##    conninfo = DBCFGLoader()
##    host, port = conninfo.readMONconfig()
##    incomingdata = datamodels.DataMon()
    
class oss_rpc(rpyc.Service) :
    global conn
    
    def on_connect(self):
        # code that runs when a connection is created
        # (to init the serivce, if needed)
        pass

    def on_disconnect(self):
        # code that runs when the connection has already closed
        # (to finalize the service, if needed)
        pass
    
    def submitcheck(self, hostname, ip, checks) :
        #To be changed, local daemon should be aware of the object itself and no
        # need to instantiate a new object, it should provide a proper DataMon object
        incomingdata = datamodels.DataMon(hostname, ip, checks)
        AsyncInsert(conn, incomingdata)
        
def sendCommand(conn) :
    import rpyc
    logging.info("Starting thread to send commands.")
    while True :
        try :
            cur = conn.cursor()
            logging.info("Checking for commands to execute.")
            cur = conn.cursor()
            cur.execute("select * from mon.mon_commands;")
            commandlist = cur.fetchall()
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
                            #Just do it, we don't care when is finished
                            #To-Do: add debug information to logging
                            AsyncInsert(conn,bgthreads[n].value).start()
                            bgthreads[n].stop()
                            del(bgthreads[n])
                        elif bgthreads[n].error :
                            #To-Do: move this to logging
                            logging.warning("Error processing: " + bgthreads[n].value)
                            del(bgthreads[n])
                #sleeping for a moment waiting for more threads to finish
                cur.close()
                time.sleep(5)
            #Let's wait until restarting the process
            #To-Do: have a configuration parameter for this
            time.sleep(30)
        except Exception, all :
            logging.exception(all)
            logging.fatal("Secondary thread failed due to: " + all)

class oss_mondThread(threading.Thread) :
    
    def __init__(self, conn) :
        threading.Thread.__init__(self)
        self.conn = conn
    
    def run(self) :
        #To-Do: Might be meaningful to have debug info for start
        logging.debug("Invoking main thread.")
        from rpyc.utils.server import ThreadedServer
        thmain = ThreadedServer(oss_rpc, port = 20200)
        thmain.start()
    
class oss_mondCommand(threading.Thread) :
    
    def __init__(self, conn) :
        threading.Thread.__init__(self)
        self.conn = conn
    
    def run(self) :
        #To-Do: Might be meaningful to have debug info for start
        logging.debug("Invoking secondary thread.")
        sendCommand(self.conn)
        
class oss_mond(Daemon) :
    def run(self):
        global conn
        conn = startDBcon()
        threads = []
        try :
            th1 = oss_mondThread(conn)
            th2 = oss_mondCommand(conn)
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
    MONconfig = readMONconfig()
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