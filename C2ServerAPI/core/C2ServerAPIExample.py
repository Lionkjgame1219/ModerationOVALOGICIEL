from time import sleep
import sys
import os

from .guiServer import Chivalry

class GameChivalry():
    def __init__(self):
        self.game = Chivalry()

    def ListPlayers(self):
        self.game.openConsole()
        self.game.consoleSend("listplayers")
        self.game.closeConsole()

    def banbyid(self, id, time, reason):
        self.game.openConsole()
        self.game.consoleSend(f'banbyid {id} {time} "{reason}"')
        self.game.closeConsole()

    def kickbyid(self, id, reason):
        self.game.openConsole()
        self.game.consoleSend(f'kickbyid {id} "{reason}"')
        self.game.closeConsole()

    def AddTime(self, time):
        self.game.openConsole()
        self.game.consoleSend(f'tbsaddstagetime {time}')
        self.game.closeConsole()

    def AdminSay(self, text):
        self.game.openConsole()
        self.game.consoleSend(f'adminsay "{text}"')
        self.game.closeConsole()
    
    def ServerSay(self, text):
        self.game.openConsole()
        self.game.consoleSend(f'serversay \"{text}\"')
        self.game.closeConsole()