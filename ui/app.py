#!/usr/bin/python

from bottle import *
import os
import socket
import yaml


class Layer(object):
    def __init__(self, layer):
        self.layer = layer
        self.images = []

        with open("layers/%s/metadata.yml" % self.layer) as metaf:
            self.yaml = yaml.load(metaf.read())


class Target(object):
    def __init__(self, f):
        (self.layer, self.target, self.ext) = splitname(f)

        with open("targets/%s/metadata.yml" % self.target) as metaf:
            self.yaml = yaml.load(metaf.read())

        if "description" in self.yaml:
            d = self.yaml["description"]
            d = d.replace("$IMAGE-SHORT", self.layer.rsplit(":", 1)[1])
            d = d.replace("$IMAGE", self.layer + ":" + self.target)
            d = d.replace("$URL", "http://%s/releases/%s" % (socket.gethostname(), f))
            self.yaml["description"] = d


def splitname(f):
    (fn, ext) = f.rsplit(".", 1)
    (layer, target) = fn.rsplit(":", 1)

    return (layer, target, ext)


@route("/")
@view("ui/index.html.tpl")
def root():
    layers = {}

    for f in sorted(os.listdir("releases")):
        (layer, target, ext) = splitname(f)

        if not layer in layers:
            layers[layer] = Layer(layer)

        layers[layer].images.append({"target": Target(f), "link": "releases/" + f, "size": os.stat("releases/" + f).st_size})

    return {"layers": layers}


@route("/<path:path>")
def download(path):
    return static_file(path, ".")


if __name__ == "__main__":
    run(host="0.0.0.0", port=80)
