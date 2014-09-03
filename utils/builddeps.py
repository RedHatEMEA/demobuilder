#!/usr/bin/python

import sys

for line in sys.stdin:
    line = line.strip()
    if line == "" or line[0] == "#":
        continue

    l = line.split(":")
    for i in range(len(l)):
        print l[i], "-".join(l[:i])
