#!/usr/bin/python -u

import argparse
import httplib
import os
import socket
import tempfile
import threading
import urlparse
import SocketServer


class EOFException(Exception):
    pass


class NotInCacheException(Exception):
    pass


class Headers(object):
    def __init__(self, f):
        self.headers = []
        while True:
            line = f.readline()
            if line == "":
                break

            self.headers.append(tuple(map(str.strip, line.split(":", 1))))

    def get(self, key, default=None):
        for h in self.headers:
            if h[0].lower() == key.lower():
                return h[1]

        return default

    def __str__(self):
        return "\r\n".join(["%s: %s" % h for h in self.headers]) + "\r\n\r\n"


class IO(object):
    def readline(self):
        l = self.f.readline()
        return l.strip()

    def read(self, n):
        s = self.f.read(n)
        return s

    def write(self, s):
        if self.f:
            self.f.write(s)

    def flush(self):
        self.f.flush()

    def writestream(self, src, n, extra=None):
        while n > 0:
            data = src.read(min(n, 4096))
            if data == "":
                raise EOFException()

            self.write(data)
            if extra:
                extra.write(data)

            n -= len(data)

    def writechunked(self, src, extra=None):
        while True:
            n = int(src.readline(), 16)
            self.write("%x\r\n" % n)

            data = src.read(n)
            src.read(2)
            self.write(data + "\r\n")

            if extra:
                extra.write(data)

            if n == 0:
                break


class Request(IO):
    def __init__(self, f):
        self.f = f

        l = self.readline()
        if l == "":
            raise EOFException()

        self.headers = Headers(self)
        (self.verb, self.url, self.http) = l.split(" ", 2)

        self.urlx = urlparse.urlparse(self.url)

    def path(self):
        url = list(self.urlx)
        url[0] = url[1] = None
        return urlparse.urlunparse(url)


class UncachedResponse(IO):
    def __init__(self, _req):
        self.req = _req

        self.s = socket.socket()
        self.s.connect(netlocparse(self.req.urlx.netloc))
        self.f = self.s.makefile()

        self.write("%s %s %s\r\n" % (self.req.verb, self.req.path(),
                                     self.req.http))
        self.write(self.req.headers)

        l = int(self.req.headers.get("Content-Length", 0))
        self.writestream(self.req, l)

        self.flush()

    def serve(self):
        (self.http, self.code, self.other) = self.readline().split(" ", 2)
        self.code = int(self.code)
        self.headers = Headers(self)

        self.req.write("%s %u %s\r\n" % (self.http, self.code, self.other))
        self.req.write(self.headers)

        if self.req.verb == "GET":
            l = self.headers.get("Content-Length")
            if l is not None:
                l = int(l)
                try:
                    cw = CacheWriter(self)
                except NotInCacheException:
                    cw = None

                self.req.writestream(self, l, cw)

                if cw:
                    cw.persist(Cache.filename(self.req.urlx))

            elif self.headers.get("Transfer-Encoding", "").lower() == "chunked":
                try:
                    cw = CacheWriter(self)
                except NotInCacheException:
                    cw = None

                self.req.writechunked(self, cw)

                if cw:
                    cw.persist(Cache.filename(self.req.urlx))

            else:
                while True:
                    data = self.read(4096)
                    if data == "":
                        break

                    self.req.write(data)

        self.req.flush()
        self.f.close()
        self.s.close()


class Cache(object):
    @staticmethod
    def filename(urlx):
        url = list(urlx)
        url[0] = None
        return "cache/" + urlparse.urlunparse(url)


class CacheWriter(IO):
    def __init__(self, _resp):
        self.resp = _resp

        if self.resp.req.verb != "GET":
            raise NotInCacheException()

        if self.resp.code != 200:
            raise NotInCacheException()

        if self.resp.headers.get("Content-Range"):
            raise NotInCacheException()

        (self.f, self.fname) = tempfile.mkstemp(dir="cache")
        self.f = os.fdopen(self.f, "w")

    def persist(self, filename):
        st = os.fstat(self.f.fileno())

        self.f.close()

        try:
            os.makedirs(os.path.split(filename)[0])
        except OSError:
            pass

        try:
            os.link(self.fname, filename)
        except OSError:
            # lost the race
            return
        finally:
            os.unlink(self.fname)


class CachedResponse(object):
    def __init__(self, _req):
        self.req = _req

        if self.req.headers.get("Range"):
            raise NotInCacheException()

        try:
            self.f = open(Cache.filename(self.req.urlx), "r")
        except IOError:
            raise NotInCacheException()

    def serve(self):
        self.req.write("HTTP/1.1 200 OK\r\n")

        st = os.fstat(self.f.fileno())
        self.req.write("Content-Length: %u\r\n" % st.st_size)
        self.req.write("Connection: close\r\n")
        self.req.write("\r\n")
        self.req.writestream(self.f, st.st_size)

        self.req.flush()


class ThreadedTCPRequestHandler(SocketServer.BaseRequestHandler):
    def handle(self):
        f = self.request.makefile()

        try:
            req = Request(f)
        except EOFException:
            return

        try:
            resp = CachedResponse(req)

        except NotInCacheException:
            resp = UncachedResponse(req)

        resp.serve()

        f.close()


class ThreadedTCPServer(SocketServer.ThreadingMixIn, SocketServer.TCPServer):
    allow_reuse_address = True
    request_queue_size = 128


def parse_args():
    parser = argparse.ArgumentParser()

    parser.add_argument("ip", nargs="?", help="IP to serve on",
                        default="0.0.0.0")

    return parser.parse_args()


def netlocparse(netloc, default=80):
    if ":" in netloc:
        (host, port) = netloc.split(":", 1)
        return (host, int(port))
    else:
        return (netloc, default)


def main():
    try:
        os.mkdir("cache")
    except OSError:
        pass

    for port in range(1024, 65536):
        try:
            handler = ThreadedTCPRequestHandler
            server = ThreadedTCPServer((args.ip, port), handler)
            break

        except socket.error:
            pass

    pid = os.fork()
    if not pid:
        os.closerange(0, 3)
        os.open("/dev/null", os.O_RDONLY)
        os.open("/dev/null", os.O_WRONLY)
        os.open("/dev/null", os.O_WRONLY)
        server.serve_forever()

    else:
        print "PROXYLISTENER=%s:%u" % (args.ip, port)
        print "PROXYPID=%u" % pid


if __name__ == "__main__":
    args = parse_args()
    main()
