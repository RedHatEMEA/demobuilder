#!/usr/bin/python -u

from bottle import *
import os
import socket
import time
import yaml


class Layer(object):
    def __init__(self, layer):
        self.layer = layer
        self.images = []

        with open("layers/%s/config.yml" % self.layer) as configf:
            self.yaml = yaml.load(configf.read())


class Target(object):
    def __init__(self, f):
        (self.layer, self.target, self.ext) = splitname(f)

        with open("targets/%s/config.yml" % self.target) as configf:
            self.yaml = yaml.load(configf.read())

        if "description" in self.yaml:
            x = self.yaml["description"]
            x = x.replace("\n", "\n  ").strip()
            self.yaml["description"] = x

        if "howto" in self.yaml:
            x = self.yaml["howto"]
            x = x.replace("$IMAGE-SHORT", self.layer.rsplit(":", 1)[1])
            x = x.replace("$IMAGE", self.layer + ":" + self.target)
            x = x.replace("$URL", "http://%s/releases/%s" % (socket.gethostname(), f))
            x = x.replace("\n", "\n  ").strip()
            self.yaml["howto"] = x


def splitname(f):
    (fn, ext) = f.rsplit(".", 1)
    (layer, target) = fn.rsplit(":", 1)

    return (layer, target, ext)


@route("/")
@view("ui/index.html.tpl")
def root():
    layers = {}

    for f in sorted(os.listdir("releases")):
        if f[0] == ".":
            continue

        (layer, target, ext) = splitname(f)

        if not layer in layers:
            layers[layer] = Layer(layer)

        st = os.stat("releases/" + f)

        layers[layer].images.append({"target": Target(f),
                                     "link": "releases/" + f,
                                     "size": "built %s, size %0.2fGB" %
                                     (time.strftime("%d/%m/%Y %H:%M:%S UTC", time.gmtime(st.st_mtime)),
                                      st.st_size / 1e9),
                                     "docs": "layers/%s/@docs/index.html" % f.rsplit(":", 1)[0]})

    return {"layers": layers}


@route("/contrib/strapdown/<path:path>")
def download(path):
    return static_file(path, "contrib/strapdown")


@route("/layers/<path:path>")
def download(path):
    return static_file(path, "layers")


@route("/misc/<path:path>")
def download(path):
    return static_file(path, "misc")


@route("/releases/<path:path>")
def download(path):
    return static_file(path, "releases")


@hook('after_request')
def log_after_request():
    print '%s - - [%s] "%s %s %s" %s' % (request.environ.get("REMOTE_ADDR"),
                                         time.strftime("%d/%b/%Y %H:%M:%S %z", time.gmtime()),
                                         request.environ.get("REQUEST_METHOD"),
                                         request.environ.get("REQUEST_URI"),
                                         request.environ.get("SERVER_PROTOCOL"),
                                         response.status_code)

if __name__ == "__main__":
    run(host="0.0.0.0", port=80, server="cherrypy")
