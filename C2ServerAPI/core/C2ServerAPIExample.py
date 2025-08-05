from time import sleep
import sys
import os

from .guiServer import Chivalry

class GameChivalry():
    def __init__(self):
        self.game = Chivalry()

    def ListPlayers(self):
        from time import sleep
        self.game.openConsole()
        self.game.consoleSend("listplayers")
        sleep(0.5)  # Wait for command execution and clipboard population

    def banbyid(self, id, time, reason):
        self.game.openConsole()
        self.game.consoleSend(f'banbyid {id} {time} "{reason}"')

    def kickbyid(self, id, reason):
        self.game.openConsole()
        self.game.consoleSend(f'kickbyid {id} "{reason}"')

    def AddTime(self, time):
        self.game.openConsole()
        self.game.consoleSend(f'tbsaddstagetime {time}')

    def AdminSay(self, text):
        self.game.openConsole()
        self.game.consoleSend(f'adminsay "{text}"')

    def ServerSay(self, text):
        self.game.openConsole()
        self.game.consoleSend(f'serversay \"{text}\"')