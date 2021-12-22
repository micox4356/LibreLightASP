#import data_cy
#import data_py
from ArtNetProcessor_cy import *
from ArtNetProcessor_py import *
import time
number=3000
number=40000
for x in range(100):
        s=time.time()
        for i in range(10):
            dmxold = [i*10]*512
            dmxnew = [i*10]*512
            matrix = [0]*512
            dmxnew[i] = i
            x=merge(dmxold,dmxnew,matrix,i)
            #print( list(x[0]))
            #print( x )
        print("c",int( (time.time()-s)*100000)/100. )

        s=time.time()
        for i in range(10):
            dmxold = [i*10]*512
            dmxnew = [i*10]*512
            matrix = [0]*512
            dmxnew[i] = i
            x=pymerge(dmxold,dmxnew,matrix,i)
            #print( list(x[0]))
            #print( x )
        print(int( (time.time()-s)*100000)/100. )
        time.sleep(.1)
