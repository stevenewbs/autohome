#!/usr/bin/env python3
import subprocess
from time import sleep
import re
import datetime
import pickle
import argparse
import os

MACS = "./macs.pickle"
parser = argparse.ArgumentParser()
parser.add_argument('-a', '--add', help="Add a device's Mac address to the database\n -a Name MacAddress", nargs=2)
args = parser.parse_args()

class Device(object):
    def __init__(self, name, mac):
        self.name = name
        self.mac = mac
        self.home = False
        self.changed = False
        self.found = False

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

    def __str__(self):
        return str("%s, %s, %s" % (self.mac, self.home, self.found))

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

def printPickle():
    with open(MACS, 'rb') as p:
        devs = pickle.load(p)
        print("Search Addresses:")
        if len(devs) < 1:
            print("Mac address database is empty - please add at least one mac address")
            return False
        for (k,i) in devs.items():
            print(k, " > ", i)
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
    i = 0
    loops = 3
    for (k, i) in devs.items():
        i.setFound(False)
    while i < loops: # run it a few times - not always that reliable
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

if __name__ == "__main__":
    if args.add:
        if addToPickle(args.add[0], args.add[1]) :
            print("Added %s : %s" % (args.add[0], args.add[1]))
        printPickle()
    else :
        main()
