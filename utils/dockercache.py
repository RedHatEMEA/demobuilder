#!/bin/python

import argparse
import BaseHTTPServer
import os
import SimpleHTTPServer
import socket
import tempfile

class ServerHandler(SimpleHTTPServer.SimpleHTTPRequestHandler):
    def do_POST(self):
        with tempfile.NamedTemporaryFile(dir=".") as f:
            copy(self.rfile, f, int(self.headers["Content-Length"]))
            if not os.path.isdir(os.path.dirname("." + self.path)):
                os.makedirs(os.path.dirname("." + self.path))
            os.rename(f.name, "." + self.path)
            f.delete = False

        self.send_response(201, "Created")
        self.send_header("Location", self.path)
        self.end_headers()

def copy(src, dst, n):
    while n > 0:
        d = src.read(min(n, 4096))
        if d == "":
            raise Exception()

        dst.write(d)
        n -= len(d)

def parse_args():
    parser = argparse.ArgumentParser()

    parser.add_argument("ip", nargs="?", help="IP to serve on",
                        default="0.0.0.0")

    return parser.parse_args()


def main():
    for port in range(1024, 65536):
        try:
            httpd = BaseHTTPServer.HTTPServer((args.ip, port), ServerHandler)
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
        print "DCLISTENER=%s:%u" % (args.ip, port)
        print "DCPID=%u" % pid

if __name__ == "__main__":
    args = parse_args()
    main()
