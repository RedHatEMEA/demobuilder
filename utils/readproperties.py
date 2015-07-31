#!/bin/python

import argparse

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

def read_properties(layer):
    properties = {}

    try:
        for l in open(layer + "/properties"):
            if l[0] in ["#", "\n"]: continue
            (k, v) = l.strip().split("=", 1)
            if v and v[0] in ["'", '"'] and v[-1] == v[0]:
                v = v[1:-1]
            properties[k] = v
    except IOError:
        pass

    return properties

def main():
    args = parse_args()
    properties = read_properties(".")
    for layer in layers(args.layer, args.target):
        properties.update(read_properties(layer))

    for k in sorted(properties):
        print "export %s='%s'" % (k, properties[k])


if __name__ == "__main__":
    main()
