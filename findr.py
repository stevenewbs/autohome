#!/usr/bin/env python3
import subprocess
from time import sleep
import re
import datetime
import pickle
import argparse
import os
import sys
from actions import WakeOnLan

class Device(object):
    def __init__(self, name, mac):
        self.name = name
        self.mac = mac
        self.home = False
        self.changed = False
        self.found = False
        self.hactions = []
        self.aactions = []

    def isHome(self):
        return self.home

    def setHome(self, h):
        self.home = h

    def isChanged(self):
        return self.changed

    def setChanged(self, c):
        self.changed = c

    def isFound(self):
        return self.found

    def setFound(self, f):
        self.found = f

    def getMac(self):
        return self.mac

    def addAction(self, when, a):
        if when == "home":
            self.hactions.append(a)
        else:
            self.aactions.append(a)
        return True

    def __str__(self):
        s = "< DEVICE: Name: %s, Mac: %s, Home: %s\n" % (self.name, self.mac, self.home)
        i = 1
        for a in self.hactions:
            s += " * Home Action %s: %s\n" % (i, a)
            i += 1
        i = 1
        for a in self.aactions:
            s += " * Home Action %s: %s\n" % (i, a)
            i += 1
        s += " >\n"

        return str(s)

    def __repr__(self):
        return "<Device instance - Values %s >" % self.__str__()

def addToPickle(key, mac):
    if not os.path.isfile(MACS):
        devs = {}
        devs[key] = Device(key, mac)
    else :
        with open(MACS, 'rb') as p:
            devs = pickle.load(p)
            if key not in devs:
                n = Device(key, mac)
                devs[key] = n
    win = key in devs
    with open(MACS, 'wb') as p:
        pickle.dump(devs, p, pickle.HIGHEST_PROTOCOL)
    return win

def addActionToPickle(name, action):
    if not os.path.isfile(MACS):
        print("No devices present - please add a device first")
    else :
        with open(MACS, 'rb') as p:
            devs = pickle.load(p)
            if name not in devs:
                print("Device not found")
                return False
            else :
                d = devs[name]
                if action[0] == "WakeOnLan":
                    if len(action) < 3:
                        print("Invalid arguments for WakeOnLan")
                        return False
                    w = WakeOnLan.WakeOnLan(name, "python", target=action[1])
                    d.addAction(action[2], w)
                else:
                    print("Unknown Action")
                    return False
    with open(MACS, 'wb') as p:
        pickle.dump(devs, p, pickle.HIGHEST_PROTOCOL)
    return True

def printPickle():
    with open(MACS, 'rb') as p:
        devs = pickle.load(p)
        print("Search Addresses:")
        if len(devs) < 1:
            print("Mac address database is empty - please add at least one mac address")
            return False
        for (k,i) in devs.items():
            print(i)
    return True

def home():
    log("Someone is home")

def notHome():
    log("Nobody home")

def log(s):
    n = datetime.datetime.now()
    print("%s : %s" % (n, s))

def nmapScan(devs):
    # run an nmap scan
    # must be run as route or use sudo to get mac addresses ...?
    x = 0
    loops = 3
    for (k, i) in devs.items():
        i.setFound(False)
    while x < loops: # run it a few times - not always that reliable
        s = subprocess.Popen("sudo nmap -T5 --min-parallelism 5 -sn 192.168.186.* | grep MAC", shell=True, stdout=subprocess.PIPE)
        for x in s.stdout:
            for (k, i) in devs.items():
                if not i.isFound():
                    if re.search(i.getMac(), str(x)):
                        print("FOUND")
                        i.setFound(True)
                        if not i.isHome():
                            i.setChanged(True)
                            i.setHome(True)
                        else:
                            i.setChanged(False)
        i += 1
    for (k, i) in devs.items():
        if not i.isFound():
            if i.isHome():
                i.setChanged(True)
            else:
                i.setChanged(False)
            i.setHome(False)
    return

def main():
    if not printPickle():
        return
    with open(MACS, 'rb') as p:
        devs = pickle.load(p)
        nmapScan(devs)
        for (k, i) in devs:
            if i.isChanged():
                if i.isHome():
                    home()
                else:
                    notHome()
    print(devs)
    with open(MACS, 'wb') as p:
        pickle.dump(devs, p, pickle.HIGHEST_PROTOCOL)


MACS = "./macs.pickle"
parser = argparse.ArgumentParser()
parser.add_argument('-c', '--command', required=True, choices= {'Add', 'Remove', 'AddAction', 'RemoveAction', 'Run'}, help="Select a command")
parser.add_argument('-d', '--who', default=None, help="Device/person friendly name")
parser.add_argument('-m', '--mac', default=None, help="Mac address")
parser.add_argument('-a', '--action', nargs="*", default=None, help="Action details to add to selected device")
args = parser.parse_args()

if __name__ == "__main__":
    if args.command == "Add":
        if args.who != None:
            if args.mac != None:
                addToPickle(args.who, args.mac)
                printPickle()
            else:
                print("Mac address is required to add a new device")
                sys.exit(1)
        else:
            print("Name is required to add a new device")
            sys.exit(1)
    elif args.command == "AddAction":
        if args.who != None:
            if args.action != None:
                print(args.action)
                addActionToPickle(args.who, args.action)
                printPickle()
            else:
                print("Action is required to add an action")
                sys.exit(1)
        else:
            print("Who is required to add an action")
            sys.exit(1)
    elif args.command == "Run":
        main()
