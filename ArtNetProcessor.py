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
                if i >= self.myscreen.getmaxyx()[0]-2:
                    break
                self.myscreen.addstr(i+1, 1, l ) #zeile,spalte,text

            if i >= self.myscreen.getmaxyx()[0]-2:
                self.myscreen.addstr(i+1, 1, "..." ) #zeile,spalte,text
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
        x.sort()
        return x


class Hosts():
    def __init__(self):
        self.__hosts = [] # LTP order
        self.__universes = {} # 192.168.0.1 = [0]*512
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
        x.sort()
        return x

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
    
    dmx_ch_buffer = []
    
    screen=Curses()
    #screen.init()
    screen.exit()
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
    cmd=[]
    mode=""
    sel_host=Pager()
    sel_host.wrap=1
    sel_univ=Pager()
    sel_univ.wrap=1
    sel_mode=Pager()
    sel_mode.wrap=1
    sel_mode.data = ["dmx","ltp","mtx","main"] # mtx = matrix
    sel_mode.maxindex = len( sel_mode.data )-1
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
                
                head_uni = head[6]/255 # /512  # * 512
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

            #continue
            # input command buffer
            screen.read()
            inp2=screen.inp()
            if "q" == inp2:
                inp2=""
                screen.exit()
                sys.exit()
            elif "?" == inp2:
                mode = "?"
            elif "," == inp2:
                sel_mode.next()
                inp2=""
            elif ";" == inp2:
                sel_mode.prev()
                inp2=""
            elif "." == inp2:
                sel_univ.next()
                inp2=""
            elif ":" == inp2:
                sel_univ.prev()
                inp2=""
            elif "-" == inp2:
                sel_host.next()
                inp2=""
            elif "_" == inp2:
                sel_host.prev()
                inp2=""
            elif "#" == inp2:
                if "main" in sel_mode.data:
                    x = sel_mode.data.index( "main")
                    sel_mode.index = x
                    sel_mode.check()
                inp2=""

            if inp2 == "\n":
                cmd2 = "".join( cmd).split()
                cmd=[]
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
                    if cmd2[1] in sel_mode.data:
                        x = sel_mode.data.index( cmd2[1])
                        sel_mode.index = x
                        sel_mode.check()

                elif "host" in cmd2 or "h" == cmd2[0]:
                    try:
                        x=int(cmd2[1]) 
                        sel_host.set(x)
                    except:
                        pass
            else:
                cmd.append(inp2)



            sel_univ.data = ohost.univs()
            sel_univ.check()
            sel_host.data = ohost.hosts()
            sel_host.check()
            host  = sel_host.get()
            univ2 = sel_univ.get()

            mode  = sel_mode.get()

            if time.time()-0.12 > ttime:

                lines = [ ]
                lines.append(" CMD:" + "".join(cmd) )
                if mode=="help" or  mode=="?":
                    lines.append("HILFE[h]: " )
                    lines.append("MODE [m]: inp, in2 in1 " )
                    lines.append("UNIV [u]: 0-16  " )
                    lines.append(" " )
                    lines.append("HILFE " )
                elif mode=="dmx" or mode == "DMX":
                    ttime = time.time()
                    dmx=ohost.get(host,univ=univ2)#univ=head_uni)
                    info=ohost.info()
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
                            lines.append(str(ttime))

                    #screen.draw_lines(lines)
                elif mode=="mtx":
                    ttime = time.time()
                    dmx=ohost.get_mtx(host,univ=univ2)#univ=head_uni)
                    info=ohost.info()
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
                            lines.append(str(ttime))

                    #screen.draw_lines(lines)
                elif mode=="ltp" or mode=="LTP":
                    ttime = time.time()
                    dmx=ohost.get(univ=univ2)#head_uni)
                    #univ2=""
                    host=""
                    info=ohost.info()
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
                    lines.append(str(ttime))

                    #screen.draw_lines(lines)
                else:
                    ttime = time.time()
                    x=ohost.get(univ=head_uni)
                    #lines = []
                    host=""
                    univ2=""
                    info=ohost.info()
                    jinfo = ""
                    for i in info:
                        xl = json.dumps(i) + "======= "
                        lines.append( xl )
                        for j in info[i]:
                            lines.append( " " + json.dumps([j,""]) )
                            if j not in sel_host.data:
                                pass#sel_host.append(j)
                            for k in info[i][j]:
                                #lines.append( "   " + json.dumps( info[i][j]) )
                                lines.append( "   "+str(k).ljust(5," ")+": " + json.dumps( info[i][j][k]) )
                            
                    lines.append(" ")
                    lines.append(str(ttime))

                    #screen.draw_lines(lines)
                tmp = ""
                tmp += " mode:"+(str(mode).ljust(10," "))
                tmp += " univ:"+str(sel_univ.index)+":"+(str(univ2).ljust(10," "))
                tmp += " host:"+str(sel_host.index)+":"+(str(host).ljust(10," "))
                lines.insert(0,tmp)

                tmp = ""
                tmp += " univ:"+ (str(sel_univ.data))#.ljust(20," "))
                tmp += " list:"+ (str(sel_host.data))#.ljust(20," "))
                lines.insert(0,tmp)
                screen.draw_lines(lines)
            time.sleep(.001)
    finally:
        screen.exit()
        print( sel_host.index,sel_host.data)




