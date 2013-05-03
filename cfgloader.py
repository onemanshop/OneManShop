#! /usr/bin/python
# -*- coding: utf-8 -*-

# Author: HC

#Proj: OneSystemShock
#CFG Loader

import ConfigParser
import os

class DBCFGLoader :
    
    """
    Provide central and uniform facility for 
    configuration retrieval across all daemons
    """

    def __init__(self, MainCFG=None) :
        self.__config = ConfigParser.SafeConfigParser()
        self.MainCFG = MainCFG
        self.dbdict = {}
    
    def readDBconfig(self) :
        hostname = ""
        port = 5432
        user = ""
        password = ""
        db = ""
        
        if self.MainCFG == None :
            self.MainCFG = "/etc/oss/oss.cfg"
        
        try :
            os.stat(self.MainCFG)
        except :
            print "Could not read main configuration file."
            os.sys.exit(2)
        
        self.__config.read(self.MainCFG)
        self.__config.read(self.__config.get("ConfFiles", 'db'))
        
        try :
            self.__config.read(self.__config.get("ConfFiles", 'db'))
            hostname = self.__config.get('postgres','hostname')
            user = self.__config.get('postgres','user')
            port = self.__config.get('postgres','port')
            password = self.__config.get('postgres','password')
            db = self.__config.get('postgres','db')
        except NoSectionError, ParsingError: 
            print "Could not read DB configuration file."
            os.sys.exit(2)
        self.dbdict = {'hostname' : hostname, 'port' : port, 'user' : user, 'password' : password, 'db' : db}

    def getDBconfig(self) :
        return self.dbdict
    
class ReadMONConfig :
    def __init__(self, MainCFG=None) :
        self.__config = ConfigParser.SafeConfigParser()
        self.MainCFG = MainCFG
        self.monport = 20200
        self.monhost = ''
        self.monpidfile = ''
        self.loglevel = ''
        self.logfile = ''
        
    def readconfig(self) :
        if self.MainCFG == None :
            self.MainCFG = "/etc/oss/oss.cfg"
        try :
            os.stat(self.MainCFG)
        except :
            print "Could not read main configuration file."
            os.sys.exit(2)
        
        self.__config.read(self.MainCFG)
        
        try :
            self.__config.read(self.__config.get("ConfFiles", 'oss_mon'))
            self.monport = self.__config.get('oss_mon', 'port')
            self.monhost = self.__config.get('oss_mon', 'host')
            self.monpidfile = self.__config.get('oss_mon', 'pidfile')
            self.loglevel = self.__config.get('oss_mon', 'loglevel')
            self.logfile = self.__config.get('oss_mon', 'logfile')
        except :
            print "Could not read MONd configuration file."
            os.sys.exit(2)
    
    def getMONbind(self) :
        return {'bind': self.monhost + ":" + self.monport}
    
    def getMONlog(self) :
        return {'loglevel': self.loglevel, "logfile" : self.logfile}
    
    
class AgentConfigLoad :
    def __init__(self, MainCFG=None) :
        self.__config = ConfigParser.SafeConfigParser()
        self.MainCFG = MainCFG
        self.path = ""
        self.port = int()
        self.plugins = ""
        self.pluginsconf = ""
        self.interval = int()
        self.logging = False
    
    def readconfig() :
        if self.MainCFG == None :
            self.MainCFG = "/etc/oss/oss_agent.cfg"
        
        try :
            os.stat(self.MainCFG)
        except :
            syslog.syslog("Could not read main configuration file.")
            os.sys.exit(2)
        
        self.__config.read(self.MainCFG)
        
        try :
            self.port = self.__config.get("agent", 'port')
        except :
            #Defaulting port
            self.port = 20220
        try :
            self.logging = self.__config.get("agent", 'logging_level')
        except :
            pass
        
        if self.logging :
            startlog(self.logging)
        
        try :
            self.plugins = self.__config.get("agent", 'plugin_path')
            self.pluginsconf = self.__config.get("agent", 'plugin_config_path')
            self.interval = self.__config.get("agent", 'pooling_interval')
        except Execption, e :
            if self.logging :
                logging.exception("Failed to load configuration file: " + e)
            syslog.syslog("Failed to load configuration file.")
            os.sys.exit(2)


        