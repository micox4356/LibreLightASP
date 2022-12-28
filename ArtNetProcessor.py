#! /usr/bin/env python3
# -*- coding: utf-8 -*-
#from __future__ import absolute_import, division, print_function
#from builtins import str, open, range, dict
#from builtins import *

"""
This file is part of librelight.

librelight is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, version 2 of the License.

librelight is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with librelight.  If not, see <http://www.gnu.org/licenses/>.

(c) 2012 micha@uxsrv.de
"""

import sys
if sys.version_info.major <= 2:
    print("exit Python3 is needet")
    sys.exit()

fn ="xx"
sys.stdout.write("\x1b]2;"+str(fn)+"\x07") # terminal title
if "__file__" in dir():
    fn = __file__
    if "/" in fn:
        fn = fn.split("/")[-1]

    sys.stdout.write("\x1b]2;"+str(fn)+" Beta 22.01"+"\x07") # terminal title
else:
    sys.stdout.write("\x1b]2;"+str("__file__")+"\x07") # terminal title

import string
import time
import os

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
cython = 0
if cython:
    if " arm" in os.popen("uname -a").read():
        import cy.ArtNetProcessor_cy_pi as cy
    else:
        import cy.ArtNetProcessor_cy as cy

from collections import OrderedDict

#print(dir())
#input()
# ============================================================   
# memcach =========================================   
# ============================================================   
mc = None
try:
    import memcache
    mc = memcache.Client(['127.0.0.1:11211'], debug=0)
    mc.set("dmx-1", [1]*512)
except Exception as e:
    print("Exception",e)

def memcachd_index_clear():
    _index = {}
    try:
        mc.set("index",_index)
    except Exception as e:
        print("memcach exception",e)

memcachd_index_clear()

def memcachd_index(key,val=""):
    try:
        _index =  mc.get("index")
        #print("A",_index)
        if type(_index) is type(None):
            _index = {}
        #print("A",_index)

        if key in _index:
            _index[key] += 1
        else:
            _index[key] = 1
        mc.set("index",_index)
    except Exception as e:
        print("memcach exception",e)




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





class Window():
    def __init__(self):
        self.myscreen = curses.initscr()
        #print( dir(self.myscreen))
        #print( self.myscreen.getmaxyx() ) 
        self._inp=""
        self.cmd = []
        self.sel_host=Pager()
        self.sel_host.wrap=1
        self.sel_univ=Pager()
        self.sel_univ.wrap=1
        self.sel_mode=Pager()
        self.sel_mode.wrap=1

        self.mode="dmx"
        if options.sendto:
            self.sel_mode.data = ["stop","stop","ltp","dmx","mtx","main"] # mtx = matrix
            self.sel_mode.maxindex = len( self.sel_mode.data )-1
            self.mode="stop"
            #self.sel_mode.set(1) #stop
            #self.sel_mode.prev() #stop
            #self.sel_mode.prev() #stop
            #self.sel_mode.prev() #stop
            self.sel_mode.prev() #stop
        else:
            self.sel_mode.data = ["dmx","mtx","main"] # mtx = matrix
            self.sel_mode.maxindex = len( self.sel_mode.data )-1


        self.mode = self.sel_mode.get()

        self.ttime = time.time()
        self.univ2 = 0
        self.host =""
        self.ohost = HostBuffer() # as default
        self.ohost.update(host="Win-"+str(options.sendto),univ=0,dmxframe=[0]*512) # dummy input

        self.__reinit_time = time.time()
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
    def reinit(self):
        self.exit()
        print( "reinit",time.time())
        self.myscreen = curses.initscr()
        #time.sleep(5)
        #self.__init()
        self.init()
        self.__reinit_time = time.time()
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

            if self.__reinit_time+60 < time.time():
                self.reinit()

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
        x=""
        if "q" == inp2:
            inp2=""
            self.exit()
            sys.exit()
        elif "?" == inp2:
            self.mode = "?"
        elif "," == inp2:
            x=self.sel_mode.next()
            self.ttime = time.time()-2
            inp2=""
        elif ";" == inp2:
            x=self.sel_mode.prev()
            self.ttime = time.time()-2
            inp2=""
        elif "." == inp2:
            x=self.sel_univ.next()
            self.ttime = time.time()-2
            inp2=""
        elif ":" == inp2:
            x=self.sel_univ.prev()
            self.ttime = time.time()-2
            inp2=""
        elif "-" == inp2:
            x=self.sel_host.next()
            self.ttime = time.time()-2
            inp2=""
        elif "_" == inp2:
            x=self.sel_host.prev()
            self.ttime = time.time()-2
            inp2=""
        elif "#" == inp2:
            if "main" in self.sel_mode.data:
                x = self.sel_mode.data.index( "main")
                self.sel_mode.index = x
                self.sel_mode.check()
                self.ttime = time.time()-2
            inp2=""
        if x:
             self.myscreen.addstr(0, 6,str(x) )
        
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
        #if type(univ2) is list:
        #    univ2.sort()

        self.mode  = self.sel_mode.get()
        if self.mode == "stop":
            if self.ttime+5 < time.time():
                self.ttime = time.time()
                self.draw_lines( ["STOP",str(time.time())] )
                #self.exit()
                #print( ["STOP",str(time.time())] )
            return

        if time.time()-0.12 > self.ttime:
            #if 1:

            lines = [ ]
            #print("cmd:",cmd)
            lines.append(" host:"+ hostname +":"+netns+" CMD:" + "".join(self.cmd) )
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
                            #if (i+1) % 21 == 0:# and i:
                            if (i+1) % 20 == 0:# and i:
                                lines.append(x)
                                x=""
                        if x:
                            lines.append(x)
                                
                        lines.append(" ")
                        lines.append(str(self.ttime))

                #screen.draw_lines(lines)
            elif self.mode=="stop":
                return 0
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
                    xl = json.dumps(i) + "=======X " # live
                    lines.append( xl )
                    for j in info[i]:
                        lines2=[]
                        lines.append( " " + json.dumps([j,""]) )

                        for k in info[i][j]:
                            if k in ["fpsx","uni","flag"]:
                                lines2.append( "   "+str(k).ljust(5," ")+": " + json.dumps( info[i][j][k]) )
                            else:
                                lines.append( "   "+str(k).ljust(5," ")+": " + json.dumps( info[i][j][k]) )

                        lines2 = "".join(lines2)
                        lines.append(lines2)
                        lines.append( " " + json.dumps([j,""]) )
                        
                lines.append(" ")
                lines.append(str(self.ttime))

                #screen.draw_lines(lines)
            tmp = ""
            tmp += " mode:"+(str(self.mode).ljust(10," "))
            tmp += " univ:"+str(self.sel_univ.index)+":"+(str(self.sel_univ.get()).ljust(8," "))
            tmp += " host:"+str(self.sel_host.index)+":"+(str(self.sel_host.get()).ljust(8," "))
            tmp += " --recive:"+str(options.recive)
            tmp += " --sendto:"+str(options.sendto)
            lines.insert(0,tmp)

            tmp = ""
            sel_univ_data = self.sel_univ.data
            #sel_univ_data.sort()
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

        #if len(dmxframe) <= 512: #len(dmxframe_old):
        if cython:# "cython":
            if len(dmxframe) <= 512: #len(dmxframe_old):
                dmxnew = dmxframe
                dmxold = dmxframe_old
                matrix = self.__universes_matrix
                hostid = self.__hosts.index(host)
                x= cy.merge(dmxold,dmxnew,matrix,hostid)
                dmx = list(x[0])
                self.__universes_matrix = list(x[1])
                update_flag = x[2]

        else:
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
        dmxframe[15] = -6
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
hostname = socket.gethostname()
netns = "none"
x = os.popen("ip netns identify $$")
xx = x.read()
if xx:
    netns = xx.strip()
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
    
# ============================================================   
# miniartnet4.py =============================================   
# ============================================================   


import time
import socket
import struct
import random

class ArtNetNode():
    """simple Object to generate raw ArtNet like Network packages 
       works in Python2 and Python3  2021-12-05
       (only basic implementation)

       "Art-Net™ Designed by and Copyright Artistic Licence Holdings Ltd"
       https://art-net.org.uk/
    """
    def __init__(self, to="10.10.10.255",univ=7,port=6454):
        try: 
            univ = int(univ)
        except:
            print("errror univ",univ ,"is not int ... set to 7")
            univ = 7
        self.univ=univ
        self.sendto = to
        self.portto = port
        self.s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        self.s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.stamp = time.time()
        self.test_stamp = time.time()
        self.dmx=[33]*512
        self.v=0
        self.d=1

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

    def send(self,dmx=None,port=''):
        if dmx is None:
            dmx = self.dmx
        else:
            self.dmx = dmx
        self.head()
        c=[self._header]

        c.append( struct.pack('>H', len(dmx) ) )
        #print([c])

        dmx_count = 0
        for v in dmx:
            if type(v) is not int:
                v=0
            elif v > 255: # max dmx value 255
                v = 255
            elif v < 0: # min dmx value 0
                v = 0
            dmx_count += 1
            c.append(struct.pack("B",v))
        c = b"".join(c)
        if port:
            self.s.sendto(c, (self.sendto, port)) # default 6454
        else:
            self.s.sendto(c, (self.sendto, self.portto)) # default 6454
        return c
    def _test_frame(self):
        if self.test_stamp+0.1 > time.time():
            return 0
        self.test_stamp = time.time()
        dmx = [0]*512
        dmx[420] = self.v
        self.dmx = dmx
        self.next()
        #self.send(dmx)
        #print( [x] )
        if self.v >= 255:
            self.d=0
        elif self.v <=0:
            self.d=1

        if self.d:
            self.v+=1
        else:
            self.v-=1

        #time.sleep(1/30.)
    def next(self):
        if self.stamp + (1/60) <= time.time():
            self.send()

def artnet_test():
    artnet = ArtNetNode()
    artnet._tes_frame()

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
        self.data.sort()
        if self.data:
             return self.data[self.index]

    def next(self):
        self.index += 1
        self.check(flag=1)
        return self.get()

    def prev(self):
        self.index -= 1
        self.check(flag=1)
        return self.get()

    def check(self,flag=0):
        if flag:
            if self.maxindex and self.maxindex <= len(self.data):
                _max = self.maxindex
            else:
                _max = len(self.data)
        else:
            _max = len(self.data)
        #_max = self.maxindex
        self.maxindex = _max


        if self.wrap:
            if self.index >= _max:
                self.index = 0
            elif self.index < 0:
                self.index = _max-1
        else:
            if self.index >= _max:
                self.index = _max-1
            elif self.index < 0:
                self.index = 0

class Timer():
    def __init__(self,sec=1,start=None):
        if start is None:
            self.last = time.time()
        else:
            self.last = start
        self.sec = sec
        print( self,"init")
    def reset(self):
        self.last = time.time()
    def check(self):
        if self.last+self.sec < time.time():
            #print(self,"chk",time.time()+self.sec-time.time())
            self.reset()
            return 1

# ============================================================   
# main =======================================================   
# ============================================================   
class Main():
    def __init__(self):
        pass
    def loop(self):
        ohost = HostBuffer()
        
        screen=Window()
        screen.exit()
        screen.ohost = ohost
                
        #artnet_out = ArtNetNode(to="10.0.25.255")
        artnet_out = ArtNetNode(to=options.sendto)

        ohost.update(host="Main-"+str(options.sendto),univ=0,dmxframe=[0]*512) # dummy input
        #artnet_out._test_frame()
        if options.testuniv:
            artnet = ArtNetNode(univ=options.testuniv)
            artnet._test_frame()

        #ysocket = Socket(bind='127.0.0.1' ,port=6555)
        xsocket = Socket()

        xt = time.time()
        ohost_buf = {}
        ohost_timer = Timer(1/30.,start=0) # 0.03333
        send_timer = Timer(1/30.) # 0.03333
        try:
            screen.exit()
            while 1:
                poll_flag = 0
                if options.testuniv:
                    artnet._test_frame()
                #artnet_out._test_frame()
                #if xsocket.poll():
                while xsocket.poll():
                    xt = time.time()
                    poll_flag = 1
                    x = xsocket.recive()
                    if x["host"] == options.recive:
                        try:
                            x["univ"] = int(options.inmap )
                        except TypeError:
                            pass
                    if x["host"] not in ohost_buf:
                        ohost_buf[x["host"]] = {}
                    if x["univ"] not in ohost_buf[x["host"]]:
                        ohost_buf[x["host"]][x["univ"]] = {}

                    ohost_buf[x["host"]][x["univ"]] = x["dmx"] #write into buffer to prevent package latency encreasing

                    try:
                        k = "{}:{}".format(x["host"],x["univ"])
                        mc.set(k, x["dmx"])  # "dmx-{}".format(univ), ltp)
                        memcachd_index(key=k)
                    except Exception as e:
                        print("exception:",e)
                        time.sleep(.1)
                    #ohost.update(x["host"],x["univ"],x["dmx"])     

                if 0:#ysocket.poll():
                    poll_flag = 1
                    x = ysocket.recive()
                    if x["host"] == options.recive:
                        try:
                            x["univ"] = int(options.inmap )
                        except TypeError:
                            pass
                    ohost.update(host=x["host"],univ=x["univ"],dmxframe=x["dmx"])     

                screen.sel_univ.data = ohost.univs()
                screen.sel_host.data = ohost.hosts()

                #if x:
                #     #screen.exit()
                #     print( "poll_clean",x)

                if ohost_timer.check():
                    for i in ohost_buf:
                        for j in ohost_buf[i]:
                             dmx=ohost_buf[i][j]
                             ohost.update(host=i,univ=j,dmxframe=dmx) # update univ_data from input buffer    
                    ohost_buf = {} # clear package buffer

                if send_timer.check() and options.sendto:
                    #x= xsocket.poll_clean()

                    #x=ohost.get(univ=univ2)
                    info=ohost.info()
                    #print( info)
                    jinfo = ""
                    for i in info:
                        univ = i
                        #print( [ univ])
                        if str(univ) == "54":
                            break
                        xl = json.dumps(univ) + "======= " #XX
                        ltp=ohost.get(univ=i)
                        
                        #print( xl )
                        #print( len(ltp) ,ltp[:20])
                        #print( "univ", univ )
                        try:
                            k="ltp-out:{}".format(univ)
                            mc.set(k,ltp)
                            memcachd_index(key=k)
                        except Exception as e:
                            pass#
                            #print("Exception",e)

                        #ltp[511] = int(univ) # set uni nr to last dmx ... testing only
                        artnet_out.univ=int(univ)
                        artnet_out.send(ltp)
                        #for j in info[i]:
                        #    print( str(univ)+" " + json.dumps([j,""]) )
                        #    for k in info[i][j]:
                        #        print( str(univ)+ "   "+str(k).ljust(5," ")+": " + json.dumps( info[i][j][k]) )

                if not poll_flag: 
                    time.sleep(.001)
                screen.loop()
        finally:
            pass
            #screen.exit()
            #print(dir(curses))


if __name__ == "__main__":
    print("main")
    main = Main()
    print("loop")
    main.loop()


