#!/bin/python

import dnslib.intercept
import dnslib.server
import os
import signal
import socket
import sys


def handler(signum, frame):
    os.system("iptables -w -t nat -D PREROUTING -i tun0 -d %s -p udp --dport 53 -j REDIRECT --to-port 153" % IP)
    sys.exit(0)


for sig in [signal.SIGTERM, signal.SIGINT]:
    signal.signal(sig, handler)

HOSTNAME = socket.gethostname()
IP = socket.gethostbyname(HOSTNAME)

os.system("iptables -w -t nat -I PREROUTING -i tun0 -d %s -p udp --dport 53 -j REDIRECT --to-port 153" % IP)

resolver = dnslib.intercept.InterceptResolver(IP, 53, "60s", ["%s 60 IN A %s" % (HOSTNAME, IP)], [], [])
udp_server = dnslib.server.DNSServer(resolver, port=153)
udp_server.start()
