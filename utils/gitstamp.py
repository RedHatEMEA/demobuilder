#!/bin/python

import socket
import subprocess
import sys
import time


def resolve_head():
    with open(".git/HEAD") as f:
        head = f.read().strip()

    if head.startswith("ref: "):
        with open(".git/%s" % head[5:]) as f:
            head = f.read().strip()

    return head[:8]


def is_clean():
    status = subprocess.check_output(["git", "status", "--porcelain"])
    return status == ""


def gitstamp(msg=""):
    clean = "unclean"
    if is_clean():
        clean = "clean"

    if msg:
        msg += ", "

    return "%sbuilt from commit %s (%s repo) on %s at %s UTC.\n" % (msg, resolve_head(), clean, socket.gethostname(), time.asctime(time.gmtime()))


def main():
    msg = ""
    if len(sys.argv) > 1:
        msg = sys.argv[1]

    sys.stdout.write(gitstamp(msg))

if __name__ == "__main__":
    main()
