#! /usr/bin/python
# -*- coding: utf-8 -*-

# Author: HC

#Proj: OneSystemShop
#CFG Loader

import ConfigParser
import os
import syslog

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
        self.MainCFG = None
        self.path = ""
        self.port = int()
        self.plugins = ""
        self.pluginsconf = ""
        self.loglevel = 'INFO'
        self.allowed_hosts = []
    
    def readconfig(self) :
        syslog.syslog("Loading configuration file.")
        if self.MainCFG == None :
            self.MainCFG = "/etc/oss/oss_agent.cfg"
        
        try :
            os.stat(self.MainCFG)
        except Exception, e :
            syslog.syslog("Failed to load configuration file. " + str(e))
            return None
        
        self.__config.read(self.MainCFG)
        
        try :
            self.port = self.__config.get("oss_agent", 'port')
        except :
            #Defaulting port
            self.port = 20220

        try :
            self.loglevel = self.__config.get("oss_agent", 'loglevel')
        except Exception, e :
            syslog.syslog("Failed to get log level from configuration file. " + str(e))
            return None
        try :
            self.port = int(self.__config.get("oss_agent", 'port'))
        except Exception, e :
            syslog.syslog("Failed to get port information from configuration file. " + str(e))
            return None
        try :
            self.plugins = self.__config.get("oss_agent", 'plugin_path')
        except Exception, e :
            syslog.syslog("Failed to get plugin_path from configuration file. " + str(e))
            return None
        try:
            self.pluginsconf = self.__config.get("oss_agent", 'plugin_config_path')
        except Exception, e :
            syslog.syslog("Failed to get plugin_config_path from configuration file. " + str(e))
            return None
        try :
            self.allowed_hosts = [x.strip(' ') for x in self.__config.get("oss_agent", 'allowed_hosts').split(",") ]
        except Exception, e :
            syslog.syslog("Failed to get the allowed_hosts from configuration file. " + str(e))
            return None
        try :
            self.monmaster = self.__config.get("oss_agent", 'monmaster')
        except Exception, e :
            syslog.syslog("Failed to get the master info from configuration file. " + str(e))
            return None
        try :
            self.interval = self.__config.get("oss_agent", 'interval')
        except Exception, e :
            syslog.syslog("Failed to get the interval from configuration file. " + str(e))
            return 10
        
        if not os.path.exists(self.pluginsconf) :
            syslog.syslog("Plugin configuration file does not exist.")
            os.sys.exit(1)
            
        if not os.path.exists(self.plugins) :
            syslog.syslog("Plugin location does not exist.")
            os.sys.exit(1)

    def setCFG(self, cfg) :
        self.MainCFG = cfg
    
    def getconfig(self) :
        return {'path': self.path, 'loglevel': self.loglevel, 'port': self.port, 'allowed_hosts': self.allowed_hosts, 'plugins': self.plugins, 'pluginsconf': self.pluginsconf, 'monmaster' : self.monmaster, 'interval': int(self.interval)}
