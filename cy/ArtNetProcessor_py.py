#from cpython cimport array
#import array

def pymerge( dmxold, dmxnew , matrix, hostindex):
    i = 0
    v = 0
    update_flag = 0
    dmx = [0]*512
    for i,v in enumerate(dmxnew):
        if dmxnew[i] != dmxold[i]:
            update_flag += 1
            matrix[i] = hostindex
        dmx[i] = v
    return (dmx,matrix,update_flag)
