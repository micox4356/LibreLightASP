#! /usr/bin/python
# -*- coding: utf-8 -*-

"""
This file is part of librelight.

librelight is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 2 of the License, or
(at your option) any later version.

librelight is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with librelight.  If not, see <http://www.gnu.org/licenses/>.

(c) 2012 micha.rathfelder@gmail.com
"""

import sys
sys.stdout.write("\x1b]2;DMX-SHEET 5\x07") # terminal title

import string
import time
import os

import socket, struct
import fcntl  #socket control
import errno
import json

import curses

class Curses():
    def __init__(self):


        self.myscreen = curses.initscr()
        print( dir(self.myscreen))
        print( self.myscreen.getmaxyx() ) 
        self._inp=""

    def test(self):
        self.init()
        #self.loop()
        self.draw_lines(["a","b","c"])
        try:
            time.sleep(10)
        finally:
            self.exit()

    def init(self):
        curses.savetty()
        curses.noecho()
        curses.cbreak() 
        curses.noqiflush() #?
        curses.noraw() #?
        self.clear()
        curses.beep()

        frame = 10
        i = 0
    def addstr(self,x,y,txt):
        self.myscreen.addstr(x, y, txt ) #zeile,spalte,text
    
    def draw_lines(self,lines):
        
        self.clear()
        try:
            for i,l in enumerate(lines):
                #print(i,l)
                if i >= self.myscreen.getmaxyx()[0]-3:
                    continue
                self.myscreen.addstr(i+1, 1, l ) #zeile,spalte,text
            self.myscreen.refresh()

        except KeyboardInterrupt as e:
            self.exit()
            print "KeyboardInterrupt"
            raise e
        #except Exception as e:
        #    self.exit()
        #    raise e
    def inp(self):
        x= self._inp
        self._inp=""
        return x
    def read(self):
        self.myscreen.nodelay(1)

        try:
            self._inp=self.myscreen.getkey()
            self.myscreen.addstr(0, 1, str(self._inp) ) #zeile,spalte,text
            self.myscreen.refresh()
            return self._inp
        except:
            pass#self._inp=""

    def clear(self):
        self.myscreen.clear()
        self.myscreen.border(0)
        curses.nocbreak();
        #self.myscreen.keypad(0);
        self.read()
        curses.echo()
        curses.resetty()
        #self.myscreen.addstr(10, 2, x ) #zeile,spalte,text

    def exit(self):
        self.clear()
        curses.endwin()
        print("ENDE")



class xUniversum():
    def __init__(self,univers_nr=0):
        self.__hosts = []
        self.__universes_dmx = {}
        self.__universes_fps = {}
        self.__universes_frames = {}
        self.__universes_flag = {}
        self.__universes_x_frames = {}
        self.__universes_x_time = {}
        self.__universes_count = {}
        self.__universes_timer = {} 
        self.__universes_info = {}
        self.__univers_nr = univers_nr   
        self.__frame = 0
    def update(self,host,dmxframe):
        if type(dmxframe) != list:
            #print( "update ERROR dmxframe is not a list", host )
            return 
        if host not in self.__hosts:
            #print( "ADDING HOST:",host,"UNIV:",self.__univers_nr)
            self.__universes_dmx[host] = [0]*512
            self.__universes_frames[host] = 0
            self.__universes_x_frames[host] = 0
            self.__universes_fps[host] = [99]*20
            self.__universes_flag[host] = [0]*20
            self.__universes_x_time[host] = time.time()
            self.__universes_timer[host] = [0]*512 
            self.__universes_info[host] = {} 
        
        while host in self.__hosts:
            self.__hosts.remove(host)
        self.__hosts.append(host) #re-order hosts list for LTP
        #print("U",host,self.__hosts)
        #print( len(dmxframe),len([0]*512), dmxframe[:10] )

        self.__frame += 1
        update_matrix = [0]*512
        dmx=[0]*512
        update_flag = 0
        dmxframe_old = self.__universes_dmx[host]

        self.__universes_frames[host] += 1
        self.__universes_x_frames[host] += 1
        if self.__universes_x_time[host]+10 < time.time():
            sec = time.time()-self.__universes_x_time[host] 
            fps = self.__universes_x_frames[host] /sec
            #fps = round(fps,1)
            fps = int(fps)
            self.__universes_fps[host].pop(0)
            self.__universes_fps[host].append(fps)
            self.__universes_x_time[host] = time.time()
            self.__universes_x_frames[host] = 0

        if len(dmxframe) <= len(dmxframe_old):
            for i,v in enumerate(dmxframe):
                if dmxframe[i] != dmxframe_old[i]:
                    #print( i,v, self.__frame)
                    update_matrix[i] = self.__frame #LTP timing
                    update_flag += 1
                    dmx[i] = v
        
        self.__universes_flag[host].pop(0)
        self.__universes_flag[host].append( update_flag )
        
        if update_flag:
            tmp = {}
            tmp["flag"] =update_flag
            tmp["flagx"] = self.__universes_flag[host] 
            tmp["fpsx"] = int(self.__universes_x_frames[host] / (time.time()-self.__universes_x_time[host]))
            tmp["frame"] = self.__frame
            #tmp["hosts"] = self.__hosts
            tmp["uni"] = self.__univers_nr 
            tmp["fps"] = self.__universes_fps[host]
            self.__universes_info[host] = tmp

            #print( "UPDATE HOST:",host, update_flag,"UNIV:",self.__univers_nr)
            self.__universes_dmx[host] = dmxframe
            self.__universes_timer[host] = update_matrix

    def get(self,host=""):

        dmx = [-1]*512
        timer = [0]*512
        #print( "H",self.__hosts,self.__univers_nr )
        if host and host in self.__hosts:
            return self.__universes_dmx[host]

        for host in self.__hosts:
            #print( host )
            dmxA   = self.__universes_dmx[host]
            timerA = self.__universes_timer[host]
            for i,t in enumerate(timerA):
                if timer[i] < t:
                    timer[i] = timerA[i]
                    dmx[i] = dmxA[i]
        return dmx
    def info(self):
        return self.__universes_info
        


class Hosts():
    def __init__(self):
        self.__hosts = [] # LTP order
        self.__universes = {} # 192.168.0.1 = [0]*512
        #self.update(host="localhost",univ=0,dmxframe=[6]*512)
        #dmxframe = [0]*512
        #dmxframe[15] = 6
        #self.update(host="333.333.333.333",univ=8,dmxframe=dmxframe)

    def get(self,host="", univ=0):
        return self.__universes[str(univ)].get(host)

    def update(self,host,univ, dmxframe):
        #print( "update", host )
    
        if str(univ) not in self.__universes: 
            self.__universes[str(univ)] = xUniversum(str(univ))

        self.__universes[str(univ)].update(host,dmxframe)
    def info(self,univ=0):
        out = {}
        #print self.__universes.keys()
        for univ in self.__universes.keys():
            #print("INFO:",univ)
            x=self.__universes[univ]
            out[univ] = x.info()
        return out 

    
def toPrintable(nonprintable):
    out = ""
    
    for i in str(nonprintable):
        printable = string.ascii_letters + string.digits +"/()=?{[]}\;:,.-_ "
        if str(i) in printable :
            out += str(i)
    return out

        
class Xsocket():
    def __init__(self):
        self.__poll = 0
        self.__data = []
        self.__addr = "NONE"
        pass
    def poll(self):
        if not self.__poll:
            try:
                self.__data, self.__addr = sock.recvfrom(6454)
                self.__poll = 1
                return 1

            except socket.timeout, e:
                err = e.args[0]
                if err == 'timed out':
                    sleep(1)
                    print 'recv timed out, retry later'
                else:
                    print e
            except socket.error, e:
                pass
    
    def recive(self):
        if self.__poll:
            self.__poll = 0
            return (self.__data,self.__addr)
        
def unpack_art_dmx(data):
    dmx = []
    for i in range(len(data[18:]) ):
        #try:
        dmx += [struct.unpack('!B',data[18+i])[0]]
        #except:
        #    pass
    return dmx




if __name__ == "__main__":
    frames = [0]*10000
    print frames
    ohost = Hosts()
    try:
        print "connecting to ArtNet Port 6454"
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        
        sock.bind(('', 6454))
        fcntl.fcntl(sock, fcntl.F_SETFL, os.O_NONBLOCK)
        
    except socket.error as e:
        print "Socket 6454 ", "ERR: {0} ".format(e.args)
        #raw_input()
        #sys.exit()

    univers = None
    if len(sys.argv) >= 2+1 and sys.argv[1] == "-u":
       univers = sys.argv[2]
    
    inp = "q"
    univ2= "8"
    univers = 0# inp.read(univers)
    debug   = 0# inp.debug()
    
    packets = 0

    #self.__myscreen.getch()
    dmx = [0] * 512

    fps = 0
    fpsi = 0
    fpst =int(time.time())
    head= "XXX"
    
    
    
    screen=Curses()
    screen.init()

    if 0: #testunivers
        while 1:
            
            screen.draw("head",list(range(1,512+1)))
            time.sleep(1)
            screen.draw("head",[0]*512)
            time.sleep(1)
            
    frame = 0
    xsocket = Xsocket()
    univ_dmx = [ ["x"]*512 ]*16
    univ_heads = [ ["none"]*2 ]*16
    ttime = time.time()
    counter = 0
    oohosts=[]
    oshost="xxx"
    try:
        while 1:
            dmx = univ_dmx[univers]
            headlines = univ_heads[univers]
            dmx = []
            text = ""
            if xsocket.poll():
                data, addr = xsocket.recive()
                head = [data[:18]]
                dmx = data[18:]
                try:
                    head = struct.unpack("!8sHBBBBHBB" , head[0] )
                except:                    
                    continue
                
                head_uni = head[6]/255 # /512  # * 512
                if head_uni < len(frames):# and len(data) == 530:
                    frames[head_uni] += 1 
                host = addr[0]
                dmx = unpack_art_dmx(data)

                ohost.update(host,head_uni,dmx)     


                
            if time.time()-0.2 > ttime:
                inp2=screen.inp()
                if inp2 in "0123456789" and inp2:
                    univ2 = str(inp2)
                if inp2 in "asdfghjkl" and inp2:
                    oshost = "asdfghjkl".index(inp2)
                    if len(oohosts) > oshost:
                        oshost = oohosts[oshost]
                elif inp2:
                    inp=inp2

                lines = ["MENUE:"+str(inp)+" univ:"+str(univ2)+ " host:"+str(oshost)]
                a=inp
                if a=="q":
                    ttime = time.time()
                    x=ohost.get(univ=head_uni)
                    #lines = []
                    info=ohost.info()
                    jinfo = ""
                    for i in info:
                        xl = json.dumps(i) + "======= "
                        lines.append( xl )
                        for j in info[i]:
                            lines.append( " " + json.dumps([j,""]) )
                            if j not in oohosts:
                                oohosts.append(j)
                            for k in info[i][j]:
                                #lines.append( "   " + json.dumps( info[i][j]) )
                                lines.append( "   "+str(k).ljust(5," ")+": " + json.dumps( info[i][j][k]) )
                            
                    lines.append(" ")
                    lines.append(str(ttime))

                    screen.draw_lines(lines)
                elif a=="w":
                    ttime = time.time()
                    host = oshost
                    dmx=ohost.get(host,univ=head_uni)
                    #lines = []
                    info=ohost.info()
                    lines.append("frame "+str(info.keys()) )
                    # print( str(info.keys() )) 

                    if univ2 in info:
                        if host in info[univ2] :
                            lines.append("frame "+str(info[univ2][host]["frame"]))
                            x=""
                            for i,v in enumerate(dmx):
                                x += str(v).rjust(4," ")
                                if (i+1) % 20 == 0:# and i:
                                    lines.append(x)
                                    x=""
                            if x:
                                lines.append(x)
                                    
                            lines.append(" ")
                            lines.append(str(ttime))

                    screen.draw_lines(lines)
                elif a=="e":
                    ttime = time.time()
                    host = "10.10.10.5"
                    dmx=ohost.get(host,univ=head_uni)
                    #lines = []
                    info=ohost.info()
                    lines.append("frame "+str(info.keys()) )
                    #print( str(info.keys() )) 

                    if univ2 in info:
                        if host in info[univ2] :
                            lines.append("frame "+str(info[univ2][host]["frame"]))
                            x=""
                            for i,v in enumerate(dmx):
                                x += str(v).rjust(4," ")
                                if (i+1) % 20 == 0:# and i:
                                    lines.append(x)
                                    x=""
                            if x:
                                lines.append(x)
                                    
                            lines.append(" ")
                            lines.append(str(ttime))

                    screen.draw_lines(lines)
                elif a=="r":
                    ttime = time.time()
                    host = "10.10.10.3"
                    dmx=ohost.get(univ=head_uni)
                    #lines = []
                    info=ohost.info()
                    lines.append("+++")
                    lines.append("frame "+str(info.keys()) )
                    #print( str(info.keys() )) 


                    if univ2 in info:
                        if host in info[univ2] :
                            lines.append("frame "+str(info[univ2][host]["frame"]))
                            x=""
                            for i,v in enumerate(dmx):
                                x += str(v).rjust(4," ")
                                if (i+1) % 20 == 0:
                                    lines.append(x)
                                    x=""
                            if x:
                                lines.append(x)
                                    
                            lines.append(" ")
                            lines.append(str(ttime))

                    screen.draw_lines(lines)
                else:
                    #lines = []
                    lines.append(" NO MENUE SELECTED CHOOS 1-9  " )
                    lines.append("time "+str(time.time() ) )
                    screen.draw_lines(lines)
                    time.sleep(.1)
            time.sleep(.001)
    finally:
        screen.exit()




