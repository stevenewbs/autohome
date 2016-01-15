#!/usr/bin/env python3

# Action.py - Steve Newbury 2015
#
# Base action class for other actions to inherit
#

actiontypes = ["command", "python"]
class Action:
    def __init__(self, name, actiontype):
        self.name = name
        self.type = actiontype
        self.action = None

    def doAction(self):
        if self.action != None:
            return self.action()

    def setAction(self, f):
        self.action = f

    def __str__(self):
        s = "< %s, Name: %s, Type: %s >" % (type(self), self.name, self.type)
        return str(s)

    def __repr__(self):
        return "<Action: %s >" % self.__str__()

if __name__ == "__main__":
    a = Action("Dave", "python")
    a.setAction((lambda x: print(x))("Hi"))
    a.doAction()
