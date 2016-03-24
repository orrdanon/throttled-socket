'''
Created on Mar 23, 2016

@author: Orr Danon
'''

import socket
import time
import random

class ThrottledSocket(object):
    '''
    classdocs
    '''

    def __init__(self, *args, **kwargs):
        '''
        Constructor
        '''
        self._rate_limit = kwargs.pop("rate_limit", False)
        self._last_time = time.time() 
        self._debt = 0
        
        self._sock = socket.socket(*args, **kwargs)
    
    
    def __getattr__(self, attr):
        return getattr(self._sock, attr)
    
    
    def sendto(self, string, *args, **kwargs):
        if self._rate_limit:
            current_time = time.time()
            time_delta = current_time - self._last_time
            self._last_time = current_time
            
            self._debt = max(self._debt-time_delta*self._rate_limit, 0)
            
            if self._debt == 0:
                nbytes = self._sock.sendto(string, *args, **kwargs)
                self._debt += nbytes
                return nbytes
            else:
                time.sleep(self._debt/self._rate_limit)
                return self.sendto(string, *args, **kwargs)
        

if __name__ == "__main__":
    PORT = 11111
    s1 = ThrottledSocket(socket.AF_INET, socket.SOCK_DGRAM, rate_limit = 10000)
    s2 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    
    s2.bind(("127.0.0.1", PORT))

    for j in xrange(1000):
        s1.sendto("1"*random.randint(1, 1024), ("127.0.0.1", 11111))
        time.sleep(random.random()/20)
        s2.recv(1024)