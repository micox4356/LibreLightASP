from cpython cimport array
import array

def merge( dmxold, dmxnew , matrix, hostindex):
    cdef int i = 0
    cdef int v = 0
    cdef int update_flag = 0
    #cdef int dmx = [0]*512
    cdef array.array a = array.array('i', [0]*512)
    cdef int[:] dmx = a
    for i,v in enumerate(dmxnew):
        if dmxnew[i] != dmxold[i]:
            update_flag += 1
            matrix[i] = hostindex
        dmx[i] = v
    return (dmx,matrix,update_flag)
