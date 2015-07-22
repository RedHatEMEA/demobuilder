#!/usr/bin/python

import socket
import yaml

HOSTNAME = socket.gethostname()
IP = socket.gethostbyname(HOSTNAME)

f = "/etc/openshift/master/master-config.yaml"
y = yaml.load(open(f, "r").read())
y["corsAllowedOrigins"] = ["127.0.0.1", "localhost", HOSTNAME, IP]
open(f, "w").write(yaml.dump(y, default_flow_style=False))
