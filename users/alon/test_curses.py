#!/usr/bin/python

import curses
stdscr=curses.initscr()
#curses.noecho()
#curses.cbreak()
#begin_x = 20 ; begin_y = 7
#height = 5 ; width = 40
#win = curses.newwin(height, width, begin_y, begin_x)
from random import randint
while True:
    x, y = randint(1, 79), randint(1, 20)
    try:
        stdscr.addstr(y, x, "*") #, cucrses.A_CHARTEXT)
        stdscr.refresh()
    except:
        pass
