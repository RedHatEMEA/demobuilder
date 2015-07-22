#!/usr/bin/python

import os
import socket
import yaml

HOSTNAME = socket.gethostname()
IP = socket.gethostbyname(HOSTNAME)

f = "/etc/openshift/node/node-config.yaml"
y = yaml.load(open(f, "r").read())
y["dnsIP"] = IP
open(f, "w").write(yaml.dump(y, default_flow_style=False))

os.system("oc get hostsubnet openshift.example.com -o yaml | sed -e 's/hostIP: .*/hostIP: %s/' | oc update -f -" % IP)
