#!/usr/bin/python

from bottle import *
import glob
import os

@route("/")
@view("ui/index.html.tpl")
def root():
    targets = [os.path.basename(x[:-1]) for x in glob.glob("build/*/")]
    images = {os.path.basename(x).rsplit(".")[0]: "" for x in glob.glob("build/*/*")}

    table = []
    for i in images:
        row = [i]
        for t in targets:
            x = glob.glob("build/%s/%s.*" % (t, i))
            if x:
                row.append(x[0])
            else:
                row.append(None)
        table.append(row)

    return {"targets": targets, "table": table}

@route("/<path:path>")
def download(path):
    return static_file(path, ".")

if __name__ == "__main__":
    run(host="0.0.0.0", port=80)
