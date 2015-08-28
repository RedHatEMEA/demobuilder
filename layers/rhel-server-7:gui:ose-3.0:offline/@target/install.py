#!/usr/bin/python

import k8s
import os
import re
import socket
import subprocess
import sys
import tempfile


def get_service_endpoint(url):
    s = api.get(url)
    return "%s:%u" % (s.spec.portalIP, s.spec.ports[0].port)


def resolve_values(t, x):
    parameters = {p.name: p.get("value", None) for p in t.parameters}
    return re.sub("\${([^}]+)}", lambda m: parameters[m.group(1)], x)


def system(cmd, check=True, **kwargs):
    print >>sys.stderr, "+ " + cmd
    if check:
        subprocess.check_call(cmd, shell=True, **kwargs)
    else:
        subprocess.call(cmd, shell=True, **kwargs)


def download_referenced_images():
    images = set()

    for t in oapi.get("/namespaces/openshift/templates")._items:
        for o in t.objects:
            if o.kind == "DeploymentConfig":
                # return container image names, unless triggered by imageChange
                for c in o.spec.template.spec.containers:
                    for tr in o.spec.triggers:
                        if "imageChangeParams" in tr and \
                           c.name in tr.imageChangeParams.containerNames:
                            break
                    else:
                        images.add(resolve_values(t, c.image))
                        c.imagePullPolicy = "IfNotPresent"

        t.kind = "Template"
        t.apiVersion = "v1"
        oapi.put("/namespaces/openshift/templates/" + t.metadata.name, t)

    for i in images:
        system("docker pull " + i)


def download_referenced_images_imagestreams(repo):
    images = set()

    istrmap = {}
    for istr in oapi.get("/namespaces/openshift/imagestreams")._items:
        for t in istr.spec.tags:
            srctag = t.name
            if "_from" in t and t._from.kind == "ImageStreamTag":
                srctag = t._from.name

            istrmap[istr.metadata.name + ":" + t.name] = istr.spec.dockerImageRepository + ":" + srctag

    for t in oapi.get("/namespaces/openshift/templates")._items:
        for o in t.objects:
            if o.kind == "DeploymentConfig":
                # return container images triggered by imageChange, if in
                # openshift namespace
                for tr in o.spec.triggers:
                    if "imageChangeParams" in tr:
                        oo = tr.imageChangeParams._from
                        if oo.kind == "ImageStreamTag" and "namespace" in oo \
                           and oo.namespace == "openshift":
                            images.add(istrmap[resolve_values(t, oo.name)])

            elif o["kind"] == "BuildConfig":
                # return builder images in openshift namespace
                oo = o.spec.strategy.sourceStrategy._from
                if oo.kind == "ImageStreamTag" and oo.namespace == "openshift":
                    images.add(istrmap[resolve_values(t, oo.name)])

    for i in images:
        newi = repo + "/" + i.split("/", 1)[1]
        if i != newi:
            if os.path.exists(i.split("/", 1)[1].split(":")[0]):
                system("docker build -t " + newi + " " + i.split("/", 1)[1].split(":")[0])
                system("docker push " + newi)
                system("docker rmi " + newi)
                system("docker rmi " + i, False)
            else:
                system("docker pull " + i)
                system("docker tag " + i + " " + newi)
                system("docker push " + newi)
                system("docker rmi " + newi)
                system("docker rmi " + i, False)

    for im in oapi.get("/images")._items:
        oapi.delete("/images/" + im.metadata.name)

    for istr in oapi.get("/namespaces/openshift/imagestreams")._items:
        istr.kind = "ImageStream"
        istr.apiVersion = "v1"
        istr.metadata = k8s.AttrDict({"name": istr.metadata.name,
                                      "annotations": k8s.AttrDict({"openshift.io/image.insecureRepository": "true"})})
        istr.spec.dockerImageRepository = repo + "/" + istr.spec.dockerImageRepository.split("/", 1)[1]
        del istr.status

        oapi.delete("/namespaces/openshift/imagestreams/" + istr.metadata.name)
        oapi.post("/namespaces/openshift/imagestreams", istr)


def download_git_repos():
    hostname = socket.gethostname()
    uris = {}

    for t in oapi.get("/namespaces/openshift/templates")._items:
        for o in t.objects:
            if o.kind == "BuildConfig":
                uri = resolve_values(t, o.spec.source.git.uri)
                if uri and not uri.startswith("git://" + hostname):
                    uris[uri] = "git://%s/%s" % (hostname,
                                                 uri.split("://", 1)[1])

    for uri in uris:
        print uri
        root = "/var/lib/git/" + uri.split("://", 1)[1]
        if not os.path.exists(root):
            system("git clone --bare " + uri + " " + root)

    system("chown -R nobody:nobody /var/lib/git")

    for t in oapi.get("/namespaces/openshift/templates")._items:
        for o in t.objects:
            if o.kind == "BuildConfig":
                m = re.match("^\${([^}]+)}$", o.spec.source.git.uri)
                if not m:
                    raise Exception

                for p in t.parameters:
                    if p.name == m.group(1) and "value" in p and \
                       not p.value.startswith("git://" + hostname):
                        p.value = uris[p.value]

                if o.spec.strategy.type != "Source":
                    raise Exception

                env = o.spec.strategy.sourceStrategy.get("env", [])
                env = [x for x in env if x.name not in ["http_proxy", "https_proxy"]]
                env.append(k8s.AttrDict({"name": "http_proxy",
                                         "value": "http://%s:8080/" % hostname}))
                env.append(k8s.AttrDict({"name": "https_proxy",
                                         "value": "http://%s:8080/" % hostname}))

                o.spec.strategy.sourceStrategy.env = env

        t.kind = "Template"
        t.apiVersion = "v1"
        oapi.put("/namespaces/openshift/templates/" + t.metadata.name, t)


def main():
    url = "https://openshift.example.com:8443"
    cert = ("/etc/openshift/master/openshift-master.crt",
            "/etc/openshift/master/openshift-master.key")

    global api, oapi
    api = k8s.API(url + "/api/v1", cert)
    oapi = k8s.API(url + "/oapi/v1", cert)

    ep = get_service_endpoint("/namespaces/default/services/image-registry")
    download_referenced_images()
    download_referenced_images_imagestreams(ep)
    download_git_repos()

if __name__ == "__main__":
    main()
