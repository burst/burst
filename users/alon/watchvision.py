"""
Test script - looks for all the ALMemory exported variables (see
nao-man/Man.cpp, down below) and prints them nicely (sortof).
"""

import time
import pynaoqi

def main():
    con=pynaoqi.NaoQiConnection()
    mylist = [x for x in con.ALMemory.getDataListName() if x[0] == '/']
    short = [x[-15:] for x in mylist]
    while True:
        res = con.ALMemory.getListData(mylist)
        for i in range(0,len(res) - 2,2):
            print '%s: %15s, %s: %15s' % (short[i], res[i], short[i+1], res[i+1])
        if len(res) % 2 == 0:
            print '%s: %15s, %s: %15s' % (short[i], res[i], short[i+1], res[i+1])
        else:
            print '%s: %15s' % (short[i], res[i])

        time.sleep(0.5)

if __name__ == '__main__':
    main()

