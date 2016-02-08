#!/usr/bin/python

import OpenSSL.crypto
import os
import socket
import yaml


def sn():
    try:
        sn = int(open("/etc/origin/master/ca.serial.txt").read(), 16)
    except IOError:
        sn = 1

    sntext = "%X" % (sn + 1)
    if len(sntext) % 2:
        sntext = "0" + sntext

    open("/etc/origin/master/ca.serial.txt", "w").write(sntext)
    return sn


def make_cert(fn):
    ca_cert = OpenSSL.crypto.load_certificate(OpenSSL.crypto.FILETYPE_PEM,
                                              open("/etc/origin/master/ca.crt").read())
    ca_key = OpenSSL.crypto.load_privatekey(OpenSSL.crypto.FILETYPE_PEM,
                                            open("/etc/origin/master/ca.key").read())

    key = OpenSSL.crypto.PKey()
    key.generate_key(OpenSSL.crypto.TYPE_RSA, 2048)

    cert = OpenSSL.crypto.X509()
    cert.set_version(2)
    cert.set_serial_number(sn())
    cert.get_subject().CN = "172.30.0.1"
    cert.gmtime_adj_notBefore(-60 * 60)
    cert.gmtime_adj_notAfter((2 * 365 * 24 - 1) * 60 * 60)
    cert.set_issuer(ca_cert.get_subject())
    cert.set_pubkey(key)
    cert.add_extensions([
        OpenSSL.crypto.X509Extension("keyUsage", True, "digitalSignature, keyEncipherment"),
        OpenSSL.crypto.X509Extension("extendedKeyUsage", False, "serverAuth"),
        OpenSSL.crypto.X509Extension("basicConstraints", True, "CA:FALSE"),
        OpenSSL.crypto.X509Extension("subjectAltName", False, "DNS:kubernetes, DNS:kubernetes.default, DNS:kubernetes.default.svc, DNS:kubernetes.default.svc.cluster.local, DNS:openshift, DNS:openshift.default, DNS:openshift.default.svc, DNS:openshift.default.svc.cluster.local, DNS:openshift.example.com, DNS:172.30.0.1, DNS:" + IP + ", IP:172.30.0.1, IP:" + IP)
    ])
    cert.sign(ca_key, "sha256")

    with os.fdopen(os.open("%s.key" % fn, os.O_WRONLY | os.O_CREAT, 0600),
                           "w") as f:
        f.write(OpenSSL.crypto.dump_privatekey(OpenSSL.crypto.FILETYPE_PEM,
                                               key))
    with open("%s.crt" % fn, "w") as f:
        f.write(OpenSSL.crypto.dump_certificate(OpenSSL.crypto.FILETYPE_PEM,
                                                cert))

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

make_cert("/etc/origin/master/etcd.server")
make_cert("/etc/origin/master/master.server")
make_cert("/etc/origin/node/server")
