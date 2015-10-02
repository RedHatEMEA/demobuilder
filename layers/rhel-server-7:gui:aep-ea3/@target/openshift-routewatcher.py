#!/usr/bin/python

import argparse
import json
import os
import re
import requests
import socket
import sys
import tempfile
import time


class RouteWatcher(object):
    """
    RouteWatcher notifies a helper object every time a route is added or
    deleted in OSE3.
    """
    def __init__(self, args, o):
        self.s = requests.Session()
        self.url = "https://%s:%s" % (args.host, args.port)
        self.cert = (args.cert, args.key)
        self.ca = args.ca
        self.m = {}
        self.o = o

    def get(self, url, **kwargs):
        return self.s.get(self.url + url, cert=self.cert, verify=self.ca,
                          **kwargs)

    def get_routes(self):
        """
        Notify helper object for every route that exists now.  Called at
        startup.  Store resourceVersion for subsequent delta requests.
        """
        j = self.get("/osapi/v1beta3/routes").json()

        self.o.clear()
        for i in j["items"]:
            self.m[i["metadata"]["uid"]] = i["spec"]["host"]
            self.o.add(i["spec"]["host"])

        self.o.commit()

        self.resourceVersion = j["metadata"]["resourceVersion"]

    def watch_routes(self):
        """
        Notify helper object for every route that is added or deleted.
        """
        while True:
            try:
                self.get_routes()

                r = self.get("/osapi/v1beta3/watch/routes?resourceVersion=%s" %
                             self.resourceVersion, stream=True)

                for l in read_chunked(r.raw):
                    j = json.loads(l)

                    if j["type"] == "ADDED":
                        self.m[j["object"]["metadata"]["uid"]] = j["object"]["spec"]["host"]
                        self.o.add(j["object"]["spec"]["host"])
                        self.o.commit()

                    if j["type"] == "MODIFIED":
                        self.o.delete(self.m[j["object"]["metadata"]["uid"]])
                        self.m[j["object"]["metadata"]["uid"]] = j["object"]["spec"]["host"]
                        self.o.add(j["object"]["spec"]["host"])
                        self.o.commit()

                    elif j["type"] == "DELETED":
                        del self.m[j["object"]["metadata"]["uid"]]
                        self.o.delete(j["object"]["spec"]["host"])
                        self.o.commit()

            except Exception as e:
                print >>sys.stderr, e
                time.sleep(5)


class Hosts(object):
    def __init__(self, args):
        self.h = {}
        self.ip = socket.gethostbyname(args.host)

    def commit(self):
        with open("/etc/hosts", "r") as f:
            hosts = f.read()

        hosts = re.sub("\n# openshift-routewatcher begin\n.*# openshift-routewatcher end\n", "\n",
                       hosts, flags=re.S)

        f = tempfile.NamedTemporaryFile(dir="/etc", prefix="hosts.",
                                        delete=False)
        f.write(hosts)
        if self.h:
            f.write("# openshift-routewatcher begin\n")
            f.write("".join(["%-13s %s\n" % (self.ip, h) for h in self.h]))
            f.write("# openshift-routewatcher end\n")
        f.close()

        os.chmod(f.name, 0644)
        os.rename(f.name, "/etc/hosts")
        os.system("restorecon /etc/hosts")

    def add(self, x):
        print >>sys.stderr, "add %s" % x
        if x not in self.h:
            self.h[x] = 0
        self.h[x] += 1

    def delete(self, x):
        print >>sys.stderr, "delete %s" % x
        self.h[x] -= 1
        if self.h[x] == 0:
            del self.h[x]

    def clear(self):
        self.h.clear()


# Python Requests doesn't seem to have chunked transfer-encoding support, at
# least on RHEL 7.1.

def read_line(raw):
    rv = ""
    while rv == "" or rv[-1] != "\n":
        rv += read_n(raw, 1)
    return rv


def read_n(raw, n):
    rv = ""
    while len(rv) < n:
        x = raw.read(n - len(rv))
        rv += x
        if x == "":
            raise Exception("short read")
    return rv


def read_chunked(raw):
    while True:
        l = int(read_line(raw), 16)
        yield read_n(raw, l)
        read_n(raw, 2)


def parse_args():
    oseroot = "/etc/origin/master"

    ap = argparse.ArgumentParser()
    ap.add_argument("host", nargs="?", default=socket.gethostname())
    ap.add_argument("port", nargs="?", default="8443")
    ap.add_argument("ca", nargs="?", default=oseroot + "/ca.crt")
    ap.add_argument("cert", nargs="?", default=oseroot + "/admin.crt")
    ap.add_argument("key", nargs="?", default=oseroot + "/admin.key")
    return ap.parse_args()


def main():
    args = parse_args()
    h = Hosts(args)

    try:
        RouteWatcher(args, h).watch_routes()

    except KeyboardInterrupt:
        h.clear()
        h.commit()


if __name__ == "__main__":
    main()
