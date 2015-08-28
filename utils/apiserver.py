#!/bin/python

import argparse
import bottle
import gitstamp
import os
import socket
import sys
import tempfile
import threading
import wsgiref.simple_server
import yaml

sys.path.append("contrib")
import webproxycache


class WSGIRefServer(bottle.ServerAdapter):
    def __init__(self, host="127.0.0.1", port=8080, **options):
        super(WSGIRefServer, self).__init__(host, port, **options)

        class FixedHandler(wsgiref.simple_server.WSGIRequestHandler):
            def address_string(self):
                return self.client_address[0]

            def log_request(*args, **kwargs):
                if not self.quiet:
                    return wsgiref.simple_server.WSGIRequestHandler.log_request(*args, **kwargs)

        self.server = wsgiref.simple_server.WSGIServer((self.host, self.port), wsgiref.simple_server.WSGIRequestHandler)

    def run(self, app):
        self.server.set_app(app)
        self.server.serve_forever()


class App(bottle.Bottle):
    def default_error_handler(self, res):
        return ""

app = App()


@app.get("/static/<path:path>")
def static(path):
    return bottle.static_file(path, ".", "application/octet-stream")


@app.post("/static/<path:path>")
def static(path):
    def copy(src, dst, n):
        while n > 0:
            d = src.read(min(n, 4096))
            if d == "":
                raise Exception()

            dst.write(d)
            n -= len(d)

    length = int(bottle.request.headers.get("Content-Length", "0"))
    if length <= 0 or bottle.request.headers.get("Content-Type", "") != "application/octet-stream":
        bottle.abort(400)

    path = "./" + path.strip("/")
    if os.path.dirname(path) and not os.path.isdir(os.path.dirname(path)):
        os.makedirs(os.path.dirname(path))

    with tempfile.NamedTemporaryFile(dir=os.path.dirname(path)) as f:
        copy(bottle.request["wsgi.input"], f, length)
        os.rename(f.name, path)
        f.delete = False

    return bottle.HTTPResponse(status=201, headers={"Location": path[2:]})


@app.get("/gitstamp")
def _gitstamp():
    return gitstamp.gitstamp(bottle.request.query.msg)


@app.get("/cache")
def cache():
    return "http://%s:%u/" % (args.ip, cacheport)


@app.get("/config")
def config():
    config = yaml.load(open("config.yml").read())
    return ["%s='%s'\n" % (k.upper(), config["config"][k]) for k in config["config"] if config["config"][k]]


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("ip", nargs="?", default="0.0.0.0")
    parser.add_argument("--debug", action="store_true")

    return parser.parse_args()


def main():
    global args
    global cacheport

    args = parse_args()

    for apiport in range(1024, 65536):
        try:
            apiserver = WSGIRefServer(args.ip, apiport)
            break

        except socket.error:
            pass

    for cacheport in range(apiport + 1, 65536):
        try:
            cacheserver = webproxycache.make_server(args.ip, cacheport)
            break

        except socket.error:
            pass

    if args.debug:
        t = threading.Thread(target=cacheserver.serve_forever)
        t.daemon = True
        t.start()

        app.run(server=apiserver)

    else:
        pid = os.fork()
        if not pid:
            os.closerange(0, 3)
            os.open("/dev/null", os.O_RDONLY)
            os.open("log", os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0666)
            os.open("log", os.O_WRONLY)

            t = threading.Thread(target=cacheserver.serve_forever)
            t.daemon = True
            t.start()

            app.run(server=apiserver)

        else:
            print "APILISTENER=%s:%u" % (args.ip, apiport)
            print "APIPID=%u" % pid

if __name__ == "__main__":
    main()
