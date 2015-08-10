#!/bin/python

import argparse
import yaml

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("layer", nargs="?")
    parser.add_argument("target", nargs="?")

    return parser.parse_args()

def layers(layer, target):
    if layer:
        layers = layer.split(":")
        for i in range(len(layers)):
            yield "layers/" + ":".join(layers[:i + 1])

    if target:
        yield "targets/" + target

def read_config(layer):
    try:
        return yaml.load(open(layer + "/config.yml").read())
    except IOError:
        return {}

def update(dst, src):
    for (k, v) in src.items():
        if isinstance(v, dict):
            dst[k] = dst.get(k, {})
            update(dst[k], src[k])
        else:
            dst[k] = src[k]

def main():
    args = parse_args()
    config = read_config(".")
    for layer in layers(args.layer, args.target):
        update(config, read_config(layer))

    for k in config["config"]:
        print "%s='%s'" % (k.upper(), config["config"][k])

    for k in ["build", "layer"]:
        for kk in config[k]:
            print "export %s_%s='%s'" % (k.upper(), kk.upper(), config[k][kk])

if __name__ == "__main__":
    main()
