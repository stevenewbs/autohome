#!/usr/bin/env python3

# WakeOnLan.py - Steve Newbury 2015
#
# Wake on Lan action class for sending a WOL packet to a server5
#

import socket
import sys
from . import Action

class WakeOnLan(Action.Action):
    def __init__(self, name, actiontype, target = None):
        super(WakeOnLan, self).__init__(name, actiontype)
        self.target = None
        if target:
            self.target = target
        else :
            self.target = input("Please enter the target machine's Mac address: ")

    def doAction(self):
        if self.target == None:
            return False
        return self.sendWol(self.target)

    def makeMagicPacket(self):
        # https://en.wikipedia.org/wiki/Wake-on-LAN
        # 6 bytes of 255 (0xFF)
        # followed by 16 repetitions of the target host's mac address
        mac = self.target
        if len(mac) != 17:
            return False
        if mac[2] != ":":
            return False
        macparts = mac.split(":")
        #print(macparts)
        x = 0
        packet = []
        while x < 102:
            if x < 6:
                packet.append('FF')
                x += 1
            else:
                packet.extend(macparts)
                x += 6
        p = bytearray(''.join(packet).encode())
        #print(p)
        return p

    def sendWol(self, mac):
        # send to broadcast address on port 0, 7 or 9 - python doesnt like port 0
        p = self.makeMagicPacket()
        if not p:
            return False
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        try:
            sock.sendto(p, ("255.255.255.255", 9))
            sock.close()
        except socket.error as e:
            print(e)
            return False
        return True

if __name__ == "__main__":
    w = WakeOnLan("test", "python")#, "48:5A:3F:89:19:33")
    print(w.doAction())
