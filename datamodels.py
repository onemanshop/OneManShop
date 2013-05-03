#! /usr/bin/python
# -*- coding: utf-8 -*-

# Author: HC

#Proj: OneSystemShock
#Data Models/Objects

import ipaddr

class DataMon() :
    def __init__() :
        self.hostname = ""
        self.ip = ipaddr.IPAddress
        self.checks = []
    
    def __init__(hostname, ip, checks) :
        self.hostname = hostname
        self.ip = ip
        self.checks = []
        for n in checks:
            self.checks.append(DataCheck(n))
    
    def getIP(self) :
        return self.ip
    
    def getHostname(self) :
        return self.hostname
    
    def getChecks(self) :
        return self.checks
    
    def setHostname(self, hostname) :
        self.hostname = hostname
    
    def setIP(self, ip) :
        self.ip = ip
    
    def addChecks(self, checks) :
        for key, value in checks :
            self.checks[key] = value
    
    def lenchecks(self) :
        return len(self.checks)
    
    def getlistdata(self) :
        return [ {'hostname': self.hostname, 'ip': self.ip, 'check_name': x.getname(), 'check_status': x.getstatus(), 'check_summary': x.getsummary()} for x in self.checks ]
    
class DataCheck() :
    def __init__(self, checkname = "", checkstatus = 3, checksummary = "" ) :
        self.checkname = checkname
        self.checkstatus = checkstatus
        self.checksummary = checksummary

    def setname(self, checkname) :
        self.checkname = checkname
    
    def setstatus(self, checkstatus) :
        self.checkstatus = checkstatus

    def setsummary(self, checksummary) :
        self.checksummary = checksummary
    
    def getname(self) :
        return self.checkname
    
    def getstatus(self) :
        return self.checkstatus

    def getsummary(self) :
        return self.checksummary
