# -*- coding: UTF-8 -*-
import os
import fcntl
import time
import socket
import struct
import random

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

        
class Socket():
    def __init__(self,bind='',port=6454):
        self.__port =port
        self.__bind =bind
        self.__poll = 0
        self.__data = []
        self.__addr = "NONE"
        #self.__hosts = {"host":{"9":[0]*512}}
        self.__hosts = {}
        self.hosts = self.__hosts
        self.open()
        self._poll_clean_time = time.time()
        self._poll_clean_count = 0
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
    def poll_clean(self):
        if self._poll_clean_time+(1/25.) <= time.time():
            self._poll_clean_time = time.time()
            self._poll_clean()
            x = self._poll_clean_count 
            self._poll_clean_count = 0
            return x
    def _poll_clean(self):
        while 1:
            try:
                self.__data, self.__addr = self.sock.recvfrom(self.__port)
                self._poll_clean_count += 1
                #return 1
            except socket.timeout as e:
                err = e.args[0]
                if err == 'timed out':
                    time.sleep(1)
                    print('recv timed out, retry later')
                else:
                    print(e)
                break
            except socket.error as e:
                break
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
                try:
                    self.head = struct.unpack("!8sHBBBBHBB" , head )
                except Exception as e:
                    pass#print( "======E09823" , e)
                univ = self.head[6]/255 # /512  # * 512
                self.univ = int(univ)

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
                
                addr = str(addr)
                univ = str(univ)
                if self.__poll:
                    if addr not in self.__hosts:
                        self.__hosts[addr] = {}
                    if univ not in self.__hosts[addr]:
                        self.__hosts[addr][univ] = {}
			
                    self.__hosts[addr][univ] = {"head":head,"addr":addr,"univ":univ,"dmx":rawdmx}
                    self.hosts = self.__hosts

            except socket.timeout as e:
                err = e.args[0]
                if err == 'timed out':
                    time.sleep(1)
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
    

import pygame
import pygame.gfxdraw
pygame.init()

screen = pygame.display.set_mode((780, 610))




pygame.display.set_caption("pygame: DMX OSZI")
pygame.mouse.set_visible(1)
pygame.key.set_repeat(1, 30)
clock = pygame.time.Clock()

pygame.init() 

x=0
y=0
running = True
xsocket = Socket()

class Trans():
    def __init__(self,y=150):
        self.y = 150
        self.s = 0.25
    def get_y(self,y):
        return int((y*self.s)+(self.y*self.s))*-1


import copy
import _thread as thread


class E():
    def __init__(self):
        self.sdata = {}
        self.lock = thread.allocate_lock()
    def loop(self):
        sdata = {}
        print("loop")
        while 1:
            flag = 0
            while xsocket.poll():
                xx = xsocket.recive()
                k = xx["host"] +":"+ str(xx["head"][6])
                sdata[k] = xx
                flag = 1

            if flag:
                try:
                    self.lock.acquire()
                    self.sdata = copy.deepcopy(sdata)
                finally:
                    self.lock.release()
            time.sleep(0.001)
    def get(self):
        
        try:
            self.lock.acquire()
            x = self.sdata #= copy.deepcopy(asdata)
            self.sdata = {}
            return x
        finally:
            self.lock.release()
e = E()
thread.start_new_thread(e.loop,())
T = Trans()
import sys
font = pygame.font.SysFont("FreeSans", 12) #,color=(255,0,0))

_x=0
sdata={}
grid_timer = time.time()
lz = time.time()
while running:
    x=int(_x)
    clock.tick(15)
    #clock.tick(225)

    sdata = e.get()
    if 0:
        poll_flag = 1
        xx = xsocket.recive()
        k = xx["host"] +":"+ str(xx["head"][6])
        sdata[k] = xx
        #print(xx)
        flag = 1
    xsdata = copy.deepcopy(sdata)
    data = []
    if int(time.time()*10) % 20 == 0:
        for k in sdata:
            print(k)
    for k in sdata:
        xx = sdata[k]
        #if xx["host"] == '10.10.10.88' and xx["head"][6]==0:
        univ = xx["head"][6] /256
        print(univ,"---...---")
        if xx["host"] == '2.0.0.88' and univ == 1:# xx["head"][6]==0:
            y = xx["dmx"][2-1]
            y = xx["dmx"][21-1]
            data.append(y)
            y = xx["dmx"][3-1]
            y = xx["dmx"][31-1]
            y = xx["dmx"][142-1]
            data.append(y)
            y = xx["dmx"][261-1]
            data.append(y)
            y = xx["dmx"][263-1]
            data.append(y)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:
            print(event.type)
            if event.key == pygame.K_ESCAPE:
                pygame.event.post(pygame.event.Event(pygame.QUIT))

    if time.time() > lz:
        lz = time.time()+6
        _x=0
        x=0
        rec = pygame.Rect(x+1,T.get_y(10),30,245) # clear balken
        pygame.draw.rect(screen,(10,10,0),rec)

    T.y=-260
    c=0
    for d in data:
        y=d
        pygame.gfxdraw.pixel(screen,x,T.get_y(255),(255,0,0))
        pygame.gfxdraw.pixel(screen,x,T.get_y(0),(10,10,25))

        rec = pygame.Rect(x+4,T.get_y(0),20,-80) # clear balken
        pygame.draw.rect(screen,(c,210,110),rec)
        rec = pygame.Rect(x+2,T.get_y(0),30,-80) # clear balken
        pygame.draw.rect(screen,(c,10,110),rec)
        text = font.render( str(y), True, (0,0,0))

        pygame.draw.circle(screen,(255,155,0),(x,T.get_y(y)),2)
        c+=50
        if c >255:
            c=255
        T.y-=275

    if grid_timer < time.time():
        grid_timer=time.time()+.0215
        for d in xsdata:
            xx=sdata[d]
            univ = xx["head"][6] //256 #/ 255

            if xx["host"].startswith('2.0.0.'):
                if univ == 0:
                    rx=308
                    ry=10 
                    rec = pygame.Rect(rx,ry,600,600) # clear balken
                    pygame.draw.rect(screen,(20,20,20),rec)
                    text = font.render( str(univ).rjust(3," "), True, (255,255,255))
                    screen.blit(text, ( rx-10, ry ) )
                    line = []
                    for i,dmx in enumerate(xx["dmx"]):
                        text = font.render( str(dmx).rjust(3," "), True, (255,255,255))
                        screen.blit(text, ( rx+10, ry+10 ) )

                        rx+=29

                        if  (i+1) % 20 == 0:
                            rx=308
                            ry+=11

                elif univ == 1:
                    rx=8
                    ry=310
                    rec = pygame.Rect(rx,ry,600,600) # clear balken
                    pygame.draw.rect(screen,(10,30,10),rec)
                    text = font.render( str(univ).rjust(3," "), True, (255,255,255))
                    screen.blit(text, ( rx-10, ry ) )
                    line = []
                    for i,dmx in enumerate(xx["dmx"]):
                        text = font.render( str(dmx).rjust(3," "), True, (255,200,255))
                        screen.blit(text, ( rx+10, ry+10 ) )

                        rx+=29

                        if  (i+1) % 20 == 0:
                            rx=8
                            ry+=11
                        
    pygame.display.flip()
    #_x+=3.5*2
    _x+=1.5*2


