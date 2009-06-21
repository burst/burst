#!/usr/bin/python

import player_init

from burst.player import Player

class Template(Player):
    
    def onStart(self):
        pass

if __name__ == '__main__':
    from burst.eventmanager import MainLoop
    MainLoop(Template).run()

