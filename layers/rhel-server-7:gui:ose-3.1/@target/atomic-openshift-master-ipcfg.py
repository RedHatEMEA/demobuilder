#!/usr/bin/python

import socket
import yaml

HOSTNAME = socket.gethostname()
IP = socket.gethostbyname(HOSTNAME)

f = "/etc/origin/master/master-config.yaml"
y = yaml.load(open(f, "r").read())
y["corsAllowedOrigins"] = ["127.0.0.1",
                           "172.30.0.1",
                           IP,
                           "kubernetes",
                           "kubernetes.default",
                           "kubernetes.default.svc",
                           "kubernetes.default.svc.cluster.local",
                           "localhost",
                           "openshift",
                           "openshift.default",
                           "openshift.default.svc",
                           "openshift.default.svc.cluster.local",
                           HOSTNAME
                           ]
y["kubernetesMasterConfig"]["masterIP"] = IP
open(f, "w").write(yaml.dump(y, default_flow_style=False))
