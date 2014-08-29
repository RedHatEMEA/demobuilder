#!/bin/python

import fcntl
import optparse
import os
import SimpleHTTPServer
import SocketServer
import socket
import struct


def parse_args():
    parser = optparse.OptionParser()

    parser.add_option("-r", "--root",
                      help="root directory to serve", metavar="DIR")
    parser.add_option("-i", "--interface",
                      help="interface to serve on")

    return parser.parse_args()


def get_ip(interface):
    if not interface: return "0.0.0.0"

    SIOCGIFADDR = 0x8915
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    ip = fcntl.ioctl(s.fileno(), SIOCGIFADDR,
                     struct.pack('256s', interface[:15]))[20:24]
    return socket.inet_ntoa(ip)


def main():
    if args.root:
        os.chdir(args.root)

    ip = get_ip(args.interface)
    for port in range(1024, 65536):
        try:
            handler = SimpleHTTPServer.SimpleHTTPRequestHandler
            httpd = SocketServer.TCPServer((ip, port), handler)
            break

        except socket.error:
            pass

    pid = os.fork()
    if not pid:
        os.closerange(0, 3)
        os.open("/dev/null", os.O_RDONLY)
        os.open("/dev/null", os.O_WRONLY)
        os.open("/dev/null", os.O_WRONLY)
        httpd.serve_forever()

    else:
        print "LISTENER=%s:%u" % (ip, port)
        print "HTTPSERVERPID=%u" % pid

if __name__ == "__main__":
    args = parse_args()[0]
    main()
