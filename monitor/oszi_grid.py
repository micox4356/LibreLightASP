# -*- coding: UTF-8 -*-
import os
import fcntl
import time
import socket
import struct
import random
import json

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

#screen = pygame.display.set_mode((780, 610))
screen = pygame.display.set_mode((560, 610))


pygame.display.set_caption("pygame: DMX OSZI 2024-05")
pygame.mouse.set_visible(1)
pygame.key.set_repeat(1, 30)
clock = pygame.time.Clock()

pygame.init() 



import copy
import _thread as thread

import sys
font = pygame.font.SysFont("FreeSans", 12) #,color=(255,0,0))


NR = 0
NR2 =0
def read_event():
    global NR,NR2
    running = True
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:
            print(event.type)
            if event.key == pygame.K_ESCAPE:
                pygame.event.post(pygame.event.Event(pygame.QUIT))


        try:
            print(event.dict ) #event.button)
            if event.type == 5:
                if "button" in event.dict and event.dict["button"] == 3:  #event.button)
                    NR += 1
                    if NR > 8:
                        NR = 0
                if "button" in event.dict and event.dict["button"] == 1:  #event.button)
                    NR -= 1
                    if NR < 0:
                        NR = 8

                if "button" in event.dict and event.dict["button"] == 4:  #event.button)
                    NR2 += 1
                    if NR2 > 512-1:
                        NR2 = 0
                if "button" in event.dict and event.dict["button"] == 5:  #event.button)
                    NR2 -= 1
                    if NR2 < 0:
                        NR2 = 512-1

        except Exception as e:
            print(e)

    return running 


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

    def draw_graph(self,screen,oszi_data,univ=0,NR2=0,label="ABCDEFGHIJK"):
        x=int(self._x)

        if time.time() > self.lz:
            self.lz = time.time()+6
            self._x=0
            x=0

            rec = pygame.Rect(x+1,T.get_y(10),30,245) # clear balken
            pygame.draw.rect(screen,(10,10,0),rec)


        T.y=-260
        c=0
        i = 0
        for d in oszi_data:
            y=d
            pygame.gfxdraw.pixel(screen,x,T.get_y(255),(255,0,0))
            pygame.gfxdraw.pixel(screen,x,T.get_y(0),(10,10,25))

            rec = pygame.Rect(x+4,T.get_y(0),20,-80) # clear balken
            pygame.draw.rect(screen,(c,210,110),rec)
            rec = pygame.Rect(x+2,T.get_y(0),30,-80) # clear balken
            pygame.draw.rect(screen,(c,10,110),rec)
            text = font.render( str(y), True, (0,0,0))

            pygame.draw.circle(screen,(255,155,0),(x,T.get_y(y)),1)

            try:
                rec = pygame.Rect(0,T.get_y(-20) ,50,12) 
                pygame.draw.rect(screen,(20,20,20),rec)
                text = font.render( "DMX:{}".format(int(NR2+i)+1), True, (255,255,255))
                screen.blit(text, ( 0,T.get_y(-20) ) )
            except:
                pass
            
            c+=50
            if c >255:
                c=255
            T.y-=275
            i+=1
        self._x+=1.5 #*2




class GRID():
    def __init__(self):
        self.grid_timer = time.time()


    def draw_hosts(self,screen,hosts,x=0,y=0):
        rx = x
        ry = y
        grid_timer = self.grid_timer

        if grid_timer > time.time():
            return 


        x2 = 350
        y2 = 5
        rec = pygame.Rect(x2,y2,200,450) # clear balken
        pygame.draw.rect(screen,(20,40,20),rec)

        for h,d in hosts.items():
            text = font.render( "HOST: {}".format(h), True, (255,255,255))
            screen.blit(text, ( x2+10, y2+10 ) )

            text = font.render( ": {}".format(d["uni"]), True, (255,255,255))
            screen.blit(text, ( x2+165, y2+10 ) )

            y2 += 14

    def draw_dmx(self,screen,dmx,highlight=0,title="title",x=0,y=250):
        rx = x
        ry = y
        grid_timer = self.grid_timer

        if grid_timer > time.time():
            return 


        x2 = 310
        y2 = 10


        rec = pygame.Rect(rx,ry,600,600) # clear balken
        pygame.draw.rect(screen,(20,20,20),rec)

        text = font.render( "{}".format(title), True, (255,255,255))
        screen.blit(text, ( rx+20, ry+10 ) )
        ry+=22

        grid_timer=time.time()+.0215


        rec = pygame.Rect(rx,ry,600,600) # clear balken
        pygame.draw.rect(screen,(20,20,20),rec)
        for i,v in enumerate(dmx):
            fg = (255,255,255)
            if v > 127:
                fg = (0,0,0)
            bg = (v,v,v)

            pygame.draw.rect(screen,bg, (rx+9,ry+10,23,11))

            if i >= highlight and i <= highlight+2:
                pygame.draw.rect(screen,(255,0,0), (rx+9,ry+9,23,13))


            text = font.render( str(v).rjust(3," "), True, fg) # (255,255,255))
            screen.blit(text, ( rx+10, ry+10 ) )

            rx+=29

            if  (i+1) % 20 == 0:
                rx=x
                ry+=12

                            

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





if __name__ == "__main__":

    grid_a = GRID()
    oszi_a = OSZI()

    import artnet_read 
    mc = None
    try:
        import memcache
        mc = memcache.Client(['127.0.0.1:11211'], debug=0)
    except Exception as e:
        print("err",e)


    ARead = artnet_read.ArtNetRead()
    thread.start_new_thread(ARead.loop,())

    while running:

        sdata = ARead.get()
        print_ips(sdata)
        source="ARTNET:netns"
        xsdata = copy.deepcopy(sdata)
        for h,d in xsdata.items():
            xsdata[h]["uni"] = d["head"][6] // 256 

        sdata = None

        if mc is not None:
            keys=mc.get("index")
            if keys:
                source="memcached"
                xsdata = {}
                for k in keys:
                    tdata ={"host":k,"dmx":[2]*20,"uni":-1}

                    uni = int(k.split(":")[-1])
                    tdata["uni"] = uni

                    dmx = mc.get(k)
                    tdata["dmx"] = dmx

                    xsdata[k] = tdata


        running = read_event()

        dmx = []
        oszi_data = []
        hosts = {}

        for h,xx in xsdata.items():
            uni = xx["uni"] #["head"][6] // 256 
            tmp_h = {}
            tmp_h["uni"] = uni
            tmp_h["host"] = h
            hosts[h] = tmp_h

        hosts2 = {}
        h2 = list(hosts.keys())
        h2.sort()
        for h in h2[::-1]:
            hosts2[h] = hosts[h]
        hosts = hosts2 #[::-1]


        for h,xx in xsdata.items():
            #print(h,xx)
            uni = xx["uni"]
            if NR != uni:
                continue
            if h.startswith('2.0.0.') or h.startswith('10.10.10.'):
                pass
            else:
                continue

            dmx = xx["dmx"]
            if len(dmx) > NR2+2:
                oszi_data = [dmx[NR2],dmx[NR2+1],dmx[NR2+2]]

            break


        oszi_a.draw_graph(screen, oszi_data,NR2=NR2) #,label=_filter) 
        grid_a.draw_hosts(screen,hosts,x=0,y=0)

        info ="-----    HELP:CLICK MOUSE R or L, or SCROLL >> source:"+source
        grid_a.draw_dmx(screen,dmx,title="UNI:{:03} CH:{:03}  {}".format(NR,NR2,info),highlight=NR2,y=230)

        pygame.display.flip()

        clock.tick(35)
