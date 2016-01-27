#!/usr/bin/python -u

import os
import Queue
import subprocess
import sys
import threading


class Job(object):
    def __init__(self, name=None):
        self.name = name
        self.children = {}

    def add(self, path):
        if path[0] not in self.children:
            if self.name:
                childname = self.name + ":" + path[0]
            else:
                childname = path[0]

            self.children[path[0]] = Job(childname)

        if path[1:]:
            self.children[path[0]].add(path[1:])

    def build(self, q):
        if self.name:
            p = subprocess.Popen(["utils/build.sh", self.name], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            while True:
                line = p.stdout.readline()
                if line == "":
                    break
                print "%-25s: %s" % (self.name, line),

            rv = p.wait()
            if rv:
                global success
                success = False

                print "%-25s: FAILED(%d)" % (self.name, rv)
                return

        for child in self.children.values():
            q.put([child.build, q])


def worker(q):
    while True:
        item = q.get()
        try:
            item[0](*item[1:])
        finally:
            q.task_done()


def build(*args):
    global success
    success = True

    q = Queue.Queue()

    root = Job()
    for arg in args:
        root.add(arg.split(":"))
    root.build(q)

    for i in range(4):
        t = threading.Thread(target=worker, args=(q, ))
        t.daemon = True
        t.start()

    q.join()

    return success


def usage():
    print "Usage: %s layer[:target]..." % sys.argv[0]
    print
    print "Valid layers:"
    print "\n".join(sorted(["  " + x for x in os.listdir("layers") if x[0] != "@"]))
    print
    print "Valid targets:"
    print "\n".join(["  " + x for x in sorted(os.listdir("targets"))])
    print


def main(*args):
    subprocess.check_call("utils/init.sh")

    if not args:
        return usage()

    if build(*args):
        return 0
    else:
        return 1

if __name__ == "__main__":
    sys.exit(main(*sys.argv[1:]))
