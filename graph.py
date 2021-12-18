
import os
import sys
import fcntl  #socket control
import socket
import time



from optparse import OptionParser
parser = OptionParser()
parser.add_option("-r", "--recive", dest="recive",
                  help="set recive ip like --recive 10.")
parser.add_option("-s", "--sendto", dest="sendto",
                  help="set sender ip like --sendto 2.255.255.255")
parser.add_option("-t", "--test", dest="testuniv",
                  help="set test univers like --test [0-16]")
parser.add_option("", "--inmap", dest="inmap",
                  help="set test univers like --test [0-16]")
#parser.add_option("-q", "--quiet",
#                  action="store_false", dest="verbose", default=True,
#                  help="don't print status messages to stdout")

(options, args) = parser.parse_args()
print("option",options)
print(options.sendto)


from collections import OrderedDict

def unpack_art_dmx(data):
    dmx = []
    for i in range(len(data[18:]) ):
        x=data[18+i]
        #print("x",x)
        #print( "data",b'!B', data[18+i])
        #x=struct.unpack( b'!B',data[18+i])
        #print( "data",b'!B', data[18+i],x)
        #x=x[0]
        dmx += [x]
    return dmx

import struct
class Socket():
    def __init__(self,bind='',port=6454):
        self.__port =port
        self.__bind =bind
        self.__poll = 0
        self.__data = []
        self.__addr = "NONE"
        self.head = [-1]*18 # /255 # /512  # * 512
        self.open()
        self._head_error = 0
    def open(self):
        try:
            print("connecting to ArtNet bind:",self.__bind,"Port",self.__port)
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            
            self.sock.bind((self.__bind, self.__port))
            fcntl.fcntl(self.sock, fcntl.F_SETFL, os.O_NONBLOCK)
            #self.sock.setblocking(0)
            
        except socket.error as e:
            print("Socket ",self.__bind,self.__port, "ERR: {0} ".format(e.args))
            #raw_input()
            #sys.exit()
    def __del__(self):
        print( self,"head_error",self._head_error)
    def poll(self):
        if not self.__poll:
            try:
                self.__data, self.__addr = self.sock.recvfrom(self.__port)


                data, addr = (self.__data,self.__addr)
                self.host = addr[0]
                head    = data[:18]
                rawdmx  = data[18:]
                #print([head],addr)
                self.univ = -1
                #print( struct.unpack("B",head) )
                #print(type(head),[head],len(head))
                if len(head) != 18:
                    self._head_error += 1
                    return 0
                self.head = struct.unpack("!8sHBBBBHBB" , head )
                #try:
                #    self.head = struct.unpack("!8sHBBBBHBB" , head )
                #except Exception as e:
                #    pass#print( "======E09823" , e)
                univ = self.head[6]/255 # /512  # * 512
                self.univ = int(univ)
                #print(univ)

                if self.host.startswith("127."): #allways recive localhost on port 
                    self.__poll = 1
                    return 1
                elif not options.recive:
                    self.__poll = 1
                    return 1
                elif self.host.startswith(options.recive): 
                    self.__poll = 1
                    return 1
                else:
                    self.__poll = 0

            except socket.timeout as e:
                err = e.args[0]
                if err == 'timed out':
                    sleep(1)
                    print('recv timed out, retry later')
                else:
                    print(e)
            except socket.error as e:
                pass
    
    def recive(self):
        if self.__poll:
            self.__poll = 0

            data, addr = (self.__data,self.__addr)
            #print( self.univ,self.head)

            self.dmx  = unpack_art_dmx(data)

            return { "host":self.host,"dmx":self.dmx,"univ":self.univ,"head":self.head,"data":data,"addr":addr}
        

if __name__ == "__main__":
    x = Socket()
    print(x)
    sstamp = time.time()
    xstamp = 0
    xxstamp = 0
    while 1:
        if x.poll():
            estamp = time.time()
            xstamp = estamp-sstamp
            xstamp = int(xstamp*10000)
            r=x.recive()
            #print( r["host"])
            #print(r.keys(),r["addr"],r["univ"],r["head"])
            flag=0
            #if "2.0.0.14" == r["host"] and r["univ"] == 7:flag=1 
            #if "2.0.0.1"   == r["host"] and r["univ"] == 0:flag=1
            if r["host"].startswith("2.0.0.") and r["univ"] == 0:flag=1
            #if r["host"].startswith("10.0.25.") :flag=1# and r["univ"] != 0:flag=1 #:flag=1

            if flag:
                string = ""
                string += "{: 6}".format(xstamp)
                string += "{: 6}".format(int(xstamp-xxstamp))
                string += "{}".format(r["host"].rjust(12) )
                string += "{: 6}".format(r["univ"])
                string += "{:}".format(str(r["dmx"][200:221]))
                #print("{: 6} {: 10} {} {} {}".format(xstamp,int(xstamp-xxstamp),r["host"].ljust(" ",10),r["univ"], r["dmx"][200:221] ) )
                print(string)
            xxstamp=xstamp
        time.sleep(0.001)

