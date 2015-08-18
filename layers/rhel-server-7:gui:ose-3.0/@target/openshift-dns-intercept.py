#!/bin/python

import dnslib.intercept
import dnslib.server
import os
import re
import signal
import socket
import sys


def handler(signum, frame):
    os.system("iptables -w -t nat -D PREROUTING -i tun0 -d %s -p udp --dport 53 -j REDIRECT --to-port 153" % NSIP)
    sys.exit(0)


for sig in [signal.SIGTERM, signal.SIGINT]:
    signal.signal(sig, handler)

HOSTNAME = socket.gethostname()
IP = socket.gethostbyname(HOSTNAME)

m = re.search("nameserver ([0-9.]+)", open("/etc/resolv.conf").read(), re.M)
NSIP = m.group(1)

os.system("iptables -w -t nat -I PREROUTING -i tun0 -d %s -p udp --dport 53 -j REDIRECT --to-port 153" % NSIP)

resolver = dnslib.intercept.InterceptResolver(NSIP, 53, "60s", ["%s 60 IN A %s" % (HOSTNAME, IP)], [], [])
udp_server = dnslib.server.DNSServer(resolver, port=153)
udp_server.start()
