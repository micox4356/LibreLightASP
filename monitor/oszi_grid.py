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

x=0
y=0
running = True

import pygame
import pygame.gfxdraw
pygame.init()

screen = pygame.display.set_mode((780, 610))




pygame.display.set_caption("pygame: DMX OSZI 2.01")
pygame.mouse.set_visible(1)
pygame.key.set_repeat(1, 30)
clock = pygame.time.Clock()

pygame.init() 



import copy
import _thread as thread

import sys
font = pygame.font.SysFont("FreeSans", 12) #,color=(255,0,0))

class Trans():
    def __init__(self,y=150):
        self.y = 150
        self.s = 0.25
    def get_y(self,y):
        return int((y*self.s)+(self.y*self.s))*-1
T = Trans()

class OSZI():
    def __init__(self):
        self._x=0
        self.sdata={}
        self.lz = time.time()
        self.c=0
    def draw(self,screen,data):#,c,x,y,T):
        x=int(self._x)

        if time.time() > self.lz:
            self.lz = time.time()+6
            self._x=0
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
        #_x+=3.5*2
        self._x+=1.5*2

def read_event():
    running = True
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:
            print(event.type)
            if event.key == pygame.K_ESCAPE:
                pygame.event.post(pygame.event.Event(pygame.QUIT))
    return running 


class GRID():
    def __init__(self):
        self.grid_timer = time.time()

    def draw(self,xsdata):
        grid_timer = self.grid_timer

        if grid_timer > time.time():
            return 

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
                            

_ips = {}
def print_ips(sdata):
    if int(time.time()*10) % 20 == 0:

        for k in sdata:
            if k in _ips:
                _ips[k] += 1
            else:
                _ips[k] = 0
            print(k.ljust(15," "),_ips[k])
        print()



grid_a = GRID()
oszi_a = OSZI()

import artnet_read 


e = artnet_read.ArtNetRead()
thread.start_new_thread(e.loop,())

while running:
    clock.tick(15)
    #clock.tick(225)
    #print(dir(e),e)
    #exit()
    sdata = e.get()

    xsdata = copy.deepcopy(sdata)

    print_ips(sdata)

    data = artnet_read.get_value(sdata,univ=1,dmx=[21,142,261,263])

    running = read_event()

    oszi_a.draw(screen,data) #,c,x,y,T)

    grid_a.draw(xsdata)

    pygame.display.flip()

