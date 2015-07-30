#!/usr/bin/python

from bottle import *
import glob
import os


def make_table(targets, images, root):
    table = []
    for i in images:
        row = [i]
        for t in targets:
            x = glob.glob("%s/%s/%s.*" % (root, t, i))
            if x:
                row.append((x[0], os.stat(x[0]).st_size))
            else:
                row.append(None)
        table.append(row)

    return table


@route("/")
@view("ui/index.html.tpl")
def root():
    targets = sorted({os.path.basename(x[:-1])
                      for x in glob.glob("build/*/") + glob.glob("releases/*/")})

    build = sorted({os.path.basename(x).rsplit(".", 1)[0]: ""
                    for x in glob.glob("build/*/*")})
    build_table = make_table(targets, build, "build")

    releases = sorted({os.path.basename(x).rsplit(".", 1)[0]: ""
                       for x in glob.glob("releases/*/*")})
    releases_table = make_table(targets, releases, "releases")

    return {"targets": targets, "build_table": build_table,
            "releases_table": releases_table}


@route("/<path:path>")
def download(path):
    return static_file(path, ".")


if __name__ == "__main__":
    run(host="0.0.0.0", port=80)
