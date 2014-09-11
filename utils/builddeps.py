#!/usr/bin/python

import sys

l = sys.argv[1].split(":")
for i in range(len(l)):
    print l[i], ":".join(l[:i])
