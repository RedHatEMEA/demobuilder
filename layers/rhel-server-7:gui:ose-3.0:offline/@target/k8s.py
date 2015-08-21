#!/usr/bin/python

import json
import requests


class AttrDict(dict):
    def __init__(self, *args, **kwargs):
        super(AttrDict, self).__init__(*args, **kwargs)
        self.__dict__ = self


class API(object):
    reserved = ["from", "items"]

    def __init__(self, _url, _cert):
        (self.url, self.cert) = (_url, _cert)

    @staticmethod
    def decode(o):
        if isinstance(o, list):
            o = [API.decode(v) for v in o]

        elif isinstance(o, dict):
            o = AttrDict({k: API.decode(o[k]) for k in o})

            for r in API.reserved:
                if r in o:
                    o["_" + r] = o[r]
                    del o[r]

        return o

    @staticmethod
    def encode(o):
        if isinstance(o, list):
            o = [API.encode(v) for v in o]

        elif isinstance(o, dict):
            o = AttrDict({k: API.encode(o[k]) for k in o})

            for r in API.reserved:
                if "_" + r in o:
                    o[r] = o["_" + r]
                    del o["_" + r]

        return o

    def request(self, method, url, **kwargs):
        if "data" in kwargs:
            kwargs["data"] = json.dumps(API.encode(kwargs["data"]))

        r = requests.request(method, self.url + url, cert=self.cert, **kwargs)
        if r.status_code / 100 != 2:
            raise Exception(r.text)

        return API.decode(json.loads(r.text))

    def delete(self, url):
        return self.request("DELETE", url)

    def get(self, url):
        return self.request("GET", url)

    def post(self, url, data):
        return self.request("POST", url, data=data)

    def put(self, url, data):
        return self.request("PUT", url, data=data)
