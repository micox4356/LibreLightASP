#! /usr/bin/python
# -*- coding: utf-8 -*-
#from __future__ import absolute_import, division, print_function
#from builtins import str, open, range, dict
#from builtins import *

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

import json


from collections import OrderedDict

# ============================================================   
# Text Grafik Curses =========================================   
# ============================================================   
import curses
class CursesDummy():
    def __init__(self):
        self.sel_host=Pager()
        self.sel_host.wrap=1
        self.sel_univ=Pager()
        self.sel_univ.wrap=1
        self.sel_mode=Pager()
        self.sel_mode.wrap=1
        pass
    def dir(self):
        pass
    def test(self):
        pass
    def init(self):
        pass
    def addstr(self,x,y,txt):
        pass
    def draw_lines(self,lines):
        pass
    def inp(self):
        return ""
        pass
    def read(self):
        pass
    def clear(self):
        pass
    def exit(self):
        pass


class Curses():
    def __init__(self):

        self.myscreen = curses.initscr()
        print( dir(self.myscreen))
        print( self.myscreen.getmaxyx() ) 
        self._inp=""
        self.ttime = time.time()
    def dir(self):
        return dir(self.myscreen)
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
            x,y= self.myscreen.getmaxyx()
            for i,l in enumerate(lines):
                #print(i,l)
                if i >= x-2:
                    break
                self.myscreen.addstr(i+1, 1, l ) #zeile,spalte,text

            if i >= self.myscreen.getmaxyx()[0]-2:
                self.myscreen.addstr(i+1, 1, "..." ) #zeile,spalte,text
            self.myscreen.refresh()
            self.myscreen.resize(x-1,y-1) # to prevent slowdown..
            self.myscreen.resize(x,y)

            

        except KeyboardInterrupt as e:
            self.exit()
            print("KeyboardInterrupt")
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

            if not self._inp:
                self._inp = self.myscreen.getch()
            self.myscreen.addstr(0, 1, str(self._inp) ) #zeile,spalte,text
            self.myscreen.refresh()
            return self._inp
        except:
            pass#self._inp=""

    def clear(self):
        self.myscreen.clear()
        self.myscreen.border(0)
        curses.nocbreak();
        self.myscreen.keypad(0);
        #self.read()
        curses.echo()
        curses.resetty()
        #self.myscreen.addstr(10, 2, x ) #zeile,spalte,text

    def exit(self):
        self.clear()
        curses.endwin()
        print("ENDE",self)
    def keyread(self):
        #continue
        # input command buffer
        self.read()
        inp2=self.inp()
        if "q" == inp2:
            inp2=""
            self.exit()
            sys.exit()
        elif "?" == inp2:
            self.mode = "?"
        elif "," == inp2:
            self.sel_mode.next()
            inp2=""
        elif ";" == inp2:
            self.sel_mode.prev()
            inp2=""
        elif "." == inp2:
            self.sel_univ.next()
            inp2=""
        elif ":" == inp2:
            self.sel_univ.prev()
            inp2=""
        elif "-" == inp2:
            self.sel_host.next()
            inp2=""
        elif "_" == inp2:
            self.sel_host.prev()
            inp2=""
        elif "#" == inp2:
            if "main" in self.sel_mode.data:
                x = self.sel_mode.data.index( "main")
                self.sel_mode.index = x
                self.sel_mode.check()
            inp2=""

        if inp2 == "\n":
            cmd2 = "".join( self.cmd).split()
            self.cmd=[]
            if len(cmd2) < 2:
                pass
            elif "C^" in cmd2:
                screen.exit()
                sys.exit()
            elif "univ" in cmd2 or "u" == cmd2[0]:
                x=""
                if cmd2[1] in sel_univ.data:
                    x = sel_univ.data.index( cmd2[1])
                    sel_univ.index = x
                    sel_univ.check()
            elif "mode" in cmd2 or "m" == cmd2[0]:
                if cmd2[1] in self.sel_mode.data:
                    x = self.sel_mode.data.index( cmd2[1])
                    self.sel_mode.index = x
                    self.sel_mode.check()

            elif "host" in cmd2 or "h" == cmd2[0]:
                try:
                    x=int(cmd2[1]) 
                    self.sel_host.set(x)
                except:
                    pass
        else:
            self.cmd.append(inp2)


    def loop(self):
        
        self.keyread()
        #print( "LOOP")
        host  = self.sel_host.get()
        univ2 = self.sel_univ.get()

        self.mode  = self.sel_mode.get()

        if time.time()-0.12 > self.ttime:

            lines = [ ]
            #print("cmd:",cmd)
            lines.append(" CMD:" + "".join(self.cmd) )
            if self.mode=="help" or  self.mode=="?":
                lines.append("HILFE[h]: " )
                lines.append("MODE [m]: inp, in2 in1 " )
                lines.append("UNIV [u]: 0-16  " )
                lines.append(" " )
                lines.append("HILFE " )
            elif self.mode=="dmx" or self.mode == "DMX":
                self.ttime = time.time()
                dmx=self.ohost.get(host,univ=univ2)#univ=head_uni)
                info=self.ohost.info()
                #lines.append("frame "+str(info.keys()) )

                if univ2 in info:
                    if host in info[univ2] :
                        lines.append("frame "+str(info[univ2][host]["frame"]))
                        x=""
                        for i,v in enumerate(dmx):
                            if v == 0:
                                v = "+"
                            x += str(v).rjust(4," ")
                            if (i+1) % 20 == 0:# and i:
                                lines.append(x)
                                x=""
                        if x:
                            lines.append(x)
                                
                        lines.append(" ")
                        lines.append(str(self.ttime))

                #screen.draw_lines(lines)
            elif self.mode=="mtx":
                self.ttime = time.time()
                dmx=self.ohost.get_mtx(host,univ=univ2)#univ=head_uni)
                info=self.ohost.info()
                #lines.append("frame "+str(info.keys()) )

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
                        lines.append(str(self.ttime))

                #screen.draw_lines(lines)
            elif self.mode=="ltp" or self.mode=="LTP":
                self.ttime = time.time()
                dmx=self.ohost.get(univ=univ2)#head_uni)
                #univ2=""
                host=""
                info=self.ohost.info()
                lines.append("frame "+str(info.keys()) )

                x=""
                for i,v in enumerate(dmx):
                    x += str(v).rjust(4," ")
                    if (i+1) % 20 == 0:
                        lines.append(x)
                        x=""
                if x:
                    lines.append(x)
                        
                lines.append(" ")
                lines.append(str(self.ttime))

                #screen.draw_lines(lines)
            else:
                self.ttime = time.time()
                x=self.ohost.get(univ=univ2)
                #lines = []
                host=""
                univ2=""
                info=self.ohost.info()
                jinfo = ""
                for i in info:
                    xl = json.dumps(i) + "======= "
                    lines.append( xl )
                    for j in info[i]:
                        lines.append( " " + json.dumps([j,""]) )
                        if j not in self.sel_host.data:
                            pass#sel_host.append(j)
                        for k in info[i][j]:
                            #lines.append( "   " + json.dumps( info[i][j]) )
                            lines.append( "   "+str(k).ljust(5," ")+": " + json.dumps( info[i][j][k]) )
                        
                lines.append(" ")
                lines.append(str(self.ttime))

                #screen.draw_lines(lines)
            tmp = ""
            tmp += " mode:"+(str(self.mode).ljust(10," "))
            tmp += " univ:"+str(self.sel_univ.index)+":"+(str(self.sel_univ.get()).ljust(10," "))
            tmp += " host:"+str(self.sel_host.index)+":"+(str(self.sel_host.get()).ljust(10," "))
            lines.insert(0,tmp)

            tmp = ""
            tmp += " univ:"+ (str(self.sel_univ.data))#.ljust(20," "))
            tmp += " list:"+ (str(self.sel_host.data))#.ljust(20," "))
            lines.insert(0,tmp)
            self.draw_lines(lines)



class Manager():
    def __init__(self):

        self.myscreen = curses.initscr()
        print( dir(self.myscreen))
        print( self.myscreen.getmaxyx() ) 
        self._inp=""
        self.cmd = []
        self.mode="ltp"
        self.sel_host=Pager()
        self.sel_host.wrap=1
        self.sel_univ=Pager()
        self.sel_univ.wrap=1
        self.sel_mode=Pager()
        self.sel_mode.wrap=1
        self.sel_mode.data = ["ltp","dmx","mtx","main"] # mtx = matrix
        self.sel_mode.maxindex = len( self.sel_mode.data )-1
        self.ttime = time.time()
        self.univ2 = 0
        self.host =""
        self.ohost = HostBuffer() # as default
    def dir(self):
        return dir(self.myscreen)
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
            x,y= self.myscreen.getmaxyx()
            for i,l in enumerate(lines):
                #print(i,l)
                if i >= x-2:
                    break
                self.myscreen.addstr(i+1, 1, l ) #zeile,spalte,text

            if i >= self.myscreen.getmaxyx()[0]-2:
                self.myscreen.addstr(i+1, 1, "..." ) #zeile,spalte,text
            self.myscreen.refresh()
            self.myscreen.resize(x-1,y-1) # to prevent slowdown..
            self.myscreen.resize(x,y)

            

        except KeyboardInterrupt as e:
            self.exit()
            print("KeyboardInterrupt")
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

            if not self._inp:
                self._inp = self.myscreen.getch()
            self.myscreen.addstr(0, 1, str(self._inp) ) #zeile,spalte,text
            self.myscreen.refresh()
            return self._inp
        except:
            pass#self._inp=""

    def clear(self):
        self.myscreen.clear()
        self.myscreen.border(0)
        curses.nocbreak();
        self.myscreen.keypad(0);
        #self.read()
        curses.echo()
        curses.resetty()
        #self.myscreen.addstr(10, 2, x ) #zeile,spalte,text

    def exit(self):
        self.clear()
        curses.endwin()
        print("ENDE",self)
    def keyread(self):
        #continue
        # input command buffer
        self.read()
        inp2=self.inp()
        if "q" == inp2:
            inp2=""
            self.exit()
            sys.exit()
        elif "?" == inp2:
            self.mode = "?"
        elif "," == inp2:
            self.sel_mode.next()
            inp2=""
        elif ";" == inp2:
            self.sel_mode.prev()
            inp2=""
        elif "." == inp2:
            self.sel_univ.next()
            inp2=""
        elif ":" == inp2:
            self.sel_univ.prev()
            inp2=""
        elif "-" == inp2:
            self.sel_host.next()
            inp2=""
        elif "_" == inp2:
            self.sel_host.prev()
            inp2=""
        elif "#" == inp2:
            if "main" in self.sel_mode.data:
                x = self.sel_mode.data.index( "main")
                self.sel_mode.index = x
                self.sel_mode.check()
            inp2=""

        if inp2 == "\n":
            cmd2 = "".join( self.cmd).split()
            self.cmd=[]
            if len(cmd2) < 2:
                pass
            elif "C^" in cmd2:
                screen.exit()
                sys.exit()
            elif "univ" in cmd2 or "u" == cmd2[0]:
                x=""
                if cmd2[1] in sel_univ.data:
                    x = sel_univ.data.index( cmd2[1])
                    sel_univ.index = x
                    sel_univ.check()
            elif "mode" in cmd2 or "m" == cmd2[0]:
                if cmd2[1] in self.sel_mode.data:
                    x = self.sel_mode.data.index( cmd2[1])
                    self.sel_mode.index = x
                    self.sel_mode.check()

            elif "host" in cmd2 or "h" == cmd2[0]:
                try:
                    x=int(cmd2[1]) 
                    self.sel_host.set(x)
                except:
                    pass
        else:
            self.cmd.append(inp2)


    def loop(self):
        
        self.keyread()
        #print( "LOOP")
        host  = self.sel_host.get()
        univ2 = self.sel_univ.get()

        self.mode  = self.sel_mode.get()

        if time.time()-0.12 > self.ttime:

            lines = [ ]
            #print("cmd:",cmd)
            lines.append(" CMD:" + "".join(self.cmd) )
            if self.mode=="help" or  self.mode=="?":
                lines.append("HILFE[h]: " )
                lines.append("MODE [m]: inp, in2 in1 " )
                lines.append("UNIV [u]: 0-16  " )
                lines.append(" " )
                lines.append("HILFE " )
            elif self.mode=="dmx" or self.mode == "DMX":
                self.ttime = time.time()
                dmx=self.ohost.get(host,univ=univ2)#univ=head_uni)
                info=self.ohost.info()
                #lines.append("frame "+str(info.keys()) )

                if univ2 in info:
                    if host in info[univ2] :
                        lines.append("frame "+str(info[univ2][host]["frame"]))
                        x=""
                        for i,v in enumerate(dmx):
                            if v == 0:
                                v = "+"
                            x += str(v).rjust(4," ")
                            if (i+1) % 20 == 0:# and i:
                                lines.append(x)
                                x=""
                        if x:
                            lines.append(x)
                                
                        lines.append(" ")
                        lines.append(str(self.ttime))

                #screen.draw_lines(lines)
            elif self.mode=="mtx":
                self.ttime = time.time()
                dmx=self.ohost.get_mtx(host,univ=univ2)#univ=head_uni)
                info=self.ohost.info()
                #lines.append("frame "+str(info.keys()) )

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
                        lines.append(str(self.ttime))

                #screen.draw_lines(lines)
            elif self.mode=="ltp" or self.mode=="LTP":
                self.ttime = time.time()
                dmx=self.ohost.get(univ=univ2)#head_uni)
                #univ2=""
                host=""
                info=self.ohost.info()
                lines.append("frame "+str(info.keys()) )

                x=""
                for i,v in enumerate(dmx):
                    x += str(v).rjust(4," ")
                    if (i+1) % 20 == 0:
                        lines.append(x)
                        x=""
                if x:
                    lines.append(x)
                        
                lines.append(" ")
                lines.append(str(self.ttime))

                #screen.draw_lines(lines)
            else:
                self.ttime = time.time()
                x=self.ohost.get(univ=univ2)
                #lines = []
                host=""
                univ2=""
                info=self.ohost.info()
                jinfo = ""
                for i in info:
                    xl = json.dumps(i) + "======= "
                    lines.append( xl )
                    for j in info[i]:
                        lines.append( " " + json.dumps([j,""]) )
                        if j not in self.sel_host.data:
                            pass#sel_host.append(j)
                        for k in info[i][j]:
                            #lines.append( "   " + json.dumps( info[i][j]) )
                            lines.append( "   "+str(k).ljust(5," ")+": " + json.dumps( info[i][j][k]) )
                        
                lines.append(" ")
                lines.append(str(self.ttime))

                #screen.draw_lines(lines)
            tmp = ""
            tmp += " mode:"+(str(self.mode).ljust(10," "))
            tmp += " univ:"+str(self.sel_univ.index)+":"+(str(self.sel_univ.get()).ljust(10," "))
            tmp += " host:"+str(self.sel_host.index)+":"+(str(self.sel_host.get()).ljust(10," "))
            lines.insert(0,tmp)

            tmp = ""
            tmp += " univ:"+ (str(self.sel_univ.data))#.ljust(20," "))
            tmp += " list:"+ (str(self.sel_host.data))#.ljust(20," "))
            lines.insert(0,tmp)
            self.draw_lines(lines)



class UniversBuffer():
    def __init__(self,univers_nr=0):
        """buffer and merge a universe from multiple sender/hosts/ip's
        """
        self.__hosts = []
        self.__universes_dmx = {}
        self.__universes_fps = {}
        self.__universes_frames = {}
        self.__universes_flag = {}
        self.__universes_x_frames = {}
        self.__universes_x_time = {}
        self.__universes_count = {}
        self.__universes_timer = {} 
        self.__universes_matrix = ["."]*512 
        self.__universes_info = {}
        self.__univers_nr = univers_nr   
        self.__frame = 0
    def _add(self,host):
        if host not in self.__hosts:
            self.__hosts.append(host) #re-order hosts list for LTP
            #print( "ADDING HOST:",host,"UNIV:",self.__univers_nr)
            self.__universes_dmx[host] = [0]*512
            self.__universes_frames[host] = 0
            self.__universes_x_frames[host] = 0
            self.__universes_fps[host] = [""]*20
            self.__universes_flag[host] = [0]*20
            self.__universes_x_time[host] = time.time()
            self.__universes_timer[host] = [0]*512 
            self.__universes_info[host] = {} 

    def _next_frame(self,host):
        self.__frame += 1
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
        
    def update(self,host,dmxframe):
        if type(dmxframe) != list:
            #print( "update ERROR dmxframe is not a list", host )
            return 

        self._add(host)

        update_matrix = [0]*512
        dmx=[0]*512
        update_flag = 0
        dmxframe_old = self.__universes_dmx[host]

        self._next_frame(host)

        if len(dmxframe) <= 512: #len(dmxframe_old):
            for i,v in enumerate(dmxframe):
                if dmxframe[i] != dmxframe_old[i]:
                    update_flag += 1
                    self.__universes_matrix[i] = self.__hosts.index(host)
                dmx[i] = v
        
        self.__universes_flag[host].pop(0)
        self.__universes_flag[host].append( update_flag )
        
        tmp = {}
        tmp["flag"] =update_flag
        tmp["flagx"] = self.__universes_flag[host] 
        tmp["fpsx"] = int(self.__universes_x_frames[host] / (time.time()-self.__universes_x_time[host]))
        tmp["frame"] = self.__frame
        #tmp["hosts"] = self.__hosts
        tmp["uni"] = self.__univers_nr 
        tmp["fps"] = self.__universes_fps[host]
        self.__universes_info[host] = tmp
        if update_flag:
            #print( "UPDATE HOST:",host, update_flag,"UNIV:",self.__univers_nr)
            self.__universes_dmx[host] = dmx # dmxframe
            self.__universes_timer[host] = update_matrix

    def get(self,host=""):

        if host and host in self.__hosts:
            return self.__universes_dmx[host]

            
        dmx = [":"]*512
        for i,v in enumerate(self.__universes_matrix):
            if type(v) is int:
                host = self.__hosts[v]
                v = self.__universes_dmx[host][i]
                dmx[i] = v
        return dmx
    def get_mtx(self,host=""):
        return self.__universes_matrix


    def info(self):
        return self.__universes_info
    def hosts(self):
        x = self.__universes_dmx.keys()
        x=list(x)
        x.sort()
        return x


class HostBuffer(): 
    def __init__(self):
        """buffer hosts and route data into universes
        """
        self.__hosts = [] # LTP order
        self.__universes = OrderedDict() # {} # 192.168.0.1 = [0]*512
        #self.update(host="localhost",univ=0,dmxframe=[6]*512)
        dmxframe = [0]*512
        dmxframe[15] = 6
        #self.update(host="333.333.333.333",univ=8,dmxframe=dmxframe)

    def get_mtx(self,host="", univ=""):
        return self.__universes[str(univ)].get_mtx(host)
    def get(self,host="", univ=""):
        if str(univ) in self.__universes:
             return self.__universes[str(univ)].get(host)
        else:
             return [-8]*512
    def hosts(self):
        hosts = []
        for univ in  self.__universes:
            x=self.__universes[univ].hosts()
            for y in x:
                #x=univ.hosts()
                if y not in hosts:
                    hosts.append(y)
        hosts.sort()
        return hosts
    def univs(self):
        x=self.__universes.keys()
        x=list(x)
        #x.sort()
        return x

    def update(self,host,univ, dmxframe):
        #print( "update", host )
    
        if str(univ) not in self.__universes: 
            self.__universes[str(univ)] = UniversBuffer(str(univ))

        self.__universes[str(univ)].update(host,dmxframe)
    def info(self,univ=0):
        out = {}
        #print self.__universes.keys()
        for univ in self.__universes.keys():
            #print("INFO:",univ)
            x=self.__universes[univ]
            out[univ] = x.info()
        return out 

# ============================================================   
# Network ====================================================   
# ============================================================   
import socket, struct
import fcntl  #socket control
import errno
def toPrintable(nonprintable):
    out = ""
    
    for i in str(nonprintable):
        printable = string.ascii_letters + string.digits +"/()=?{[]}\;:,.-_ "
        if str(i) in printable :
            out += str(i)
    return out

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
    def __init__(self):
        self.__poll = 0
        self.__data = []
        self.__addr = "NONE"
        self.open()
    def open(self):
        try:
            print("connecting to ArtNet Port 6454")
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            
            self.sock.bind(('', 6454))
            fcntl.fcntl(self.sock, fcntl.F_SETFL, os.O_NONBLOCK)
            
        except socket.error as e:
            print("Socket 6454 ", "ERR: {0} ".format(e.args))
            #raw_input()
            #sys.exit()
    def poll(self):
        if not self.__poll:
            try:
                self.__data, self.__addr = self.sock.recvfrom(6454)
                self.__poll = 1
                return 1

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
            return (self.__data,self.__addr)

# ============================================================   
# miniartnet4.py =============================================   
# ============================================================   
import time
import socket
import struct

class ArtNetNode():
    """simple Object to generate ArtNet Network packages 
       works in Python2 and Python3  2021-12-05

    """
    def __init__(self, to="10.10.10.255",univ=7):
        self.univ=univ
        self.sendto = to
        self.s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        self.s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    def head(self):
        self._header = []
        self._header.append(b"Art-Net\x00")            # Name, 7byte + 0x00
        self._header.append(struct.pack('<H', 0x5000)) # OpCode ArtDMX -> 0x5000, Low Byte first
        self._header.append(struct.pack('>H', 14))     # Protocol Version 14, High Byte first
        self._header.append(b"\x00")                   # Order -> nope -> 0x00
        self._header.append(struct.pack('B',1))        # Eternity Port

        # Address
        #if 0 <= universe <= 15 and 0 <= net <= 127 and 0 <= subnet <= 15
        net, subnet, universe = (0,0,self.univ) #address
        self._header.append(struct.pack('<H', net << 8 | subnet << 4 | universe))

        self._header = b"".join(self._header)

    def send(self,dmx=[0]*512):
        self.head()
        c=[self._header]

        c.append( struct.pack('>H', len(dmx) ) )
        #print([c])

        dmx_count = 0
        for v in dmx:
            if v > 255: # max dmx value 255
                v = 255
            elif v < 0: # min dmx value 0
                v = 0
            dmx_count += 1
            c.append(struct.pack("B",v))
        c = b"".join(c)
        self.s.sendto(c, (self.sendto, 6454))
        return c


def artnet_test():
    import random
    artnet = ArtNetNode()
    v=0
    d=1
    while 1:
        dmx = [0]*512
        dmx[0] = v
        x=artnet.send(dmx)
        print( [x] )
        if v >= 255:
            d=0
        elif v <=0:
            d=1

        if d:
            v+=1
        else:
            v-=1

        time.sleep(1/30.)

# ============================================================   
# helper =====================================================   
# ============================================================   
        
class Pager(): #scroll thru list
    def __init__(self):
        self.data = []
        self.index = 0
        self.wrap = 0
        self.maxindex = 0 
    def append(self,val):
        self.data.append(val)
        self.check()

    def set(self,nr):
        self.index = nr
        self.check()
    def get(self):
        self.check()
        if self.data:
             return self.data[self.index]

    def next(self):
        self.index += 1
        self.check(flag=1)
    def prev(self):
        self.index -= 1
        self.check(flag=1)
    def check(self,flag=0):
        if flag:
            if self.maxindex and self.maxindex <= len(self.data):
                max = self.maxindex
            else:
                max = len(self.data)
        else:
            max = len(self.data)


        if self.wrap:
            if self.index >= max:
                self.index = 0
            elif self.index < 0:
                self.index = max-1
        else:
            if self.index >= max:
                self.index = max-1
            elif self.index < 0:
                self.index = 0


# ============================================================   
# main =======================================================   
# ============================================================   
class Main():
    def __init__(self):
        pass
    def loop(self):
        frames = [0]*10000
        print("frame",frames)
        ohost = HostBuffer()

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
        
        dmx_ch_buffer = []
        
        screen=Manager()
        #screen=CursesDummy()
        #screen.init()
        screen.exit()
        screen.ohost = ohost

        if 0: #testunivers
            while 1:
                
                screen.draw("head",list(range(1,512+1)))
                time.sleep(1)
                screen.draw("head",[0]*512)
                time.sleep(1)
                
        frame = 0
        xsocket = Socket()
        univ_dmx = [ ["x"]*512 ]*16
        univ_heads = [ ["none"]*2 ]*16
        counter = 0
        head_uni=""
        dmx = []
        headlines = ""
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
                    #print("\n=====", [addr,data],"\n======" )
                    #sys.exit()
                    
                    head_uni = head[6]/255 # /512  # * 512
                    head_uni = int(head_uni)
                    #print("head_uni", head_uni)
                    if head_uni < len(frames):# and len(data) == 530:
                        frames[head_uni] += 1 
                    host = addr[0]
                    dmx = unpack_art_dmx(data)

                    ohost.update(host,head_uni,dmx)     
                    #screen.exit()
                    if 0:# len(dmx):
                        print( host)
                        print( head_uni, data[:30] )#dmx[:10]  )    
                        print( head_uni, dmx[:10]  )    


                #screen.ohost = ohost
                screen.sel_univ.data = ohost.univs()
                #screen.sel_univ.check()
                screen.sel_host.data = ohost.hosts()
                #screen.sel_host.check()

                screen.loop()

                time.sleep(.001)
        finally:
            screen.exit()
            #print(dir(screen))
            #print("###")
            #print(screen.dir())
            #print("###")
            #print(dir(curses))
            #print( "finally",sel_host.index,sel_host.data)


if __name__ == "__main__":
    main = Main()
    main.loop()


