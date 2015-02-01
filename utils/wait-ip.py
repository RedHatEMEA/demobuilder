#!/usr/bin/python

import json
import os
import Queue
import socket
import sys
import threading
import time


def connect(t, p):
    s = socket.socket(t, socket.SOCK_STREAM)
    while True:
        try:
            s.connect(p)
            return s

        except socket.error:
            time.sleep(1)


def start_thread(target, arg):
    t = threading.Thread(target=target, args=(arg, ))
    t.daemon = True
    t.start()
    return t


def pid_thread(p):
    while True:
        if not os.path.exists("/proc/%s" % p):
            q.put(None)
        
        time.sleep(1)

def rhev_thread(p):
    s = connect(socket.AF_UNIX, p)

    while True:
        r = json.loads(s.recv(4096))

        if r["__name__"] == "network-interfaces":
            q.put(r["interfaces"][0]["inet"][0])
            return


def qemu_thread(p):
    s = connect(socket.AF_UNIX, p)

    while True:
        try:
            s.sendall(json.dumps({"execute": "guest-network-get-interfaces"}))
            r = json.loads(s.recv(4096))

            eth = [eth for eth in r["return"] if eth["name"] == "eth0"][0]
            ip = [ip for ip in eth["ip-addresses"]
                  if ip["ip-address-type"] == "ipv4"][0]

            q.put(ip["ip-address"])
            return

        except (IndexError, KeyError):
            time.sleep(1)


def main():
    global q
    q = Queue.Queue()

    start_thread(rhev_thread, "%s/rhev.sock" % sys.argv[1])
    start_thread(qemu_thread, "%s/qemu.sock" % sys.argv[1])
    start_thread(pid_thread, sys.argv[2])

    while True:
        try:
            ip = q.get(False)
            break

        except Queue.Empty:
            time.sleep(1)

    if not ip:
        sys.exit(1)

    connect(socket.AF_INET, (ip, 22))
    print "IP=%s" % ip


if __name__ == "__main__":
    main()
