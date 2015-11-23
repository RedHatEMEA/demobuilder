#!/usr/bin/python

import os
import socket
import yaml

HOSTNAME = socket.gethostname()
IP = socket.gethostbyname(HOSTNAME)

f = "/etc/origin/node/node-config.yaml"
y = yaml.load(open(f, "r").read())
y["nodeIP"] = IP
open(f, "w").write(yaml.dump(y, default_flow_style=False))

os.system("oc delete node %s" % HOSTNAME)
os.system("oc get hostsubnet %s -o yaml | sed -e 's/hostIP: .*/hostIP: %s/' | oc update -f -" % (HOSTNAME, IP))
