from twisted.internet.protocol import Protocol
from twisted.internet.protocol import Factory
from twisted.internet import reactor

from Utilities import UserProcess, TimeExpiredDict, Cryptography

from datetime import datetime

import os, sys, subprocess

class Impersonate(Protocol):
    
    def __init__(self, factory):
        self.factory = factory
        
    
    def authenticate(self, username, password):
        #TODO: improve authentication security
        return username == "asdf" and password == "1234"
    
    
    def connectionMade(self):
        print "Connection established..."
        

    def connectionLost(self, reason):
        print "Connection lost..."
    
    
    def dataReceived(self, data):
        
        print "Data received. Decrypting..."
        data = data.strip('\r').strip('\n').strip('\r')
        
        #Decrypt data
        #data_arr = data.split(" ")
        #data = Cryptography.Decrypt(self.factory.key, data_arr[1], data_arr[0])
        
        #Parse data
        data_arr = data.split(" ")
        credentials = data_arr[0].split(":")
        command = data_arr[1]
        
        #Authenticate
        print "Authenticating..."
        
        if self.authenticate(credentials[0], credentials[1]):
            print "Permission granted"
            
            command = 'su %s -c "%s"' % ("david", command)
            print "Running: %s" % command
            
            process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            out, nothing = process.communicate()
            
            print out
            
            #return the result
            self.transport.write(out)
        else:
            print "Permission denied"
            self.transport.write("Permission denied")



 
class ImpersonateFactory(Factory):
    
    def __init__(self, venv=None):
        self.key = "cL7eNdb3yJCkw1zlvizrZuUdbplTmsFD"
    
    
    def buildProtocol(self, addr):
        return Impersonate(self)




reactor.listenTCP(8123, ImpersonateFactory(sys.argv[1]))
reactor.run()