#!/bin/python

import argparse
import os
import SimpleHTTPServer
import SocketServer
import socket


def parse_args():
    parser = argparse.ArgumentParser()

    parser.add_argument("ip", nargs="?", help="IP to serve on",
                        default="0.0.0.0")

    return parser.parse_args()


def main():
    for port in range(1024, 65536):
        try:
            handler = SimpleHTTPServer.SimpleHTTPRequestHandler
            httpd = SocketServer.TCPServer((args.ip, port), handler)
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
        print "HTTPLISTENER=%s:%u" % (args.ip, port)
        print "HTTPPID=%u" % pid

if __name__ == "__main__":
    args = parse_args()
    main()
