#!/usr/bin/python

import json
import sys


def get_parameter(t, k):
    for p in t["parameters"]:
        if p["name"] == k:
            return p
    return ""


def main(jsfile, k, v):
    j = json.load(open(jsfile))
    p = get_parameter(j, k)
    p["value"] = v
    json.dump(j, open(jsfile, "w"), indent=2)


if __name__ == "__main__":
    main(*sys.argv[1:])
