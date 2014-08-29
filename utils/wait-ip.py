#!/usr/bin/python

import asyncore
import json
import socket
import sys
import time


class VirtioDispatcher(asyncore.dispatcher):
    def __init__(self, sock):
        asyncore.dispatcher.__init__(self)
        self.create_socket(socket.AF_UNIX, socket.SOCK_STREAM)
        while True:
            try:
                self.connect(sock)
                break

            except socket.error:
                time.sleep(1)
        self.buf = ""

    def writable(self):
        return (len(self.buf) > 0)

    def handle_write(self):
        sent = self.send(self.buf)
        self.buf = self.buf[sent:]


class RHEVAgent(VirtioDispatcher):
    def handle_read(self):
        global ip

        r = self.recv(4096)
        if not r: return

        r = json.loads(r)
        if r["__name__"] == "network-interfaces":
            ip = r["interfaces"][0]["inet"][0]
            asyncore.close_all()


class QEmuAgent(VirtioDispatcher):
    def __init__(self, sock):
        VirtioDispatcher.__init__(self, sock)
        self.buf = json.dumps({"execute": "guest-network-get-interfaces"})

    def handle_read(self):
        global ip

        r = self.recv(4096)
        if not r: return

        r = json.loads(r)
        eth = [eth for eth in r["return"] if eth["name"] == "eth0"][0]
        ip = [ip for ip in eth["ip-addresses"]
              if ip["ip-address-type"] == "ipv4"][0]

        ip = ip["ip-address"]
        asyncore.close_all()


def main():
    rhev = RHEVAgent("%s/rhev.sock" % sys.argv[1])
    qemu = QEmuAgent("%s/qemu.sock" % sys.argv[1])
    asyncore.loop()

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    while True:
        try:
            sock.connect((ip, 22))
            break

        except socket.error:
            time.sleep(1)

    print "IP=%s" % ip

if __name__ == "__main__":
    main()
