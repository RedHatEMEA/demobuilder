#!/usr/bin/python -u

import k8s
import os
import re
import subprocess
import sys
import time


def get_service_endpoint(url):
    s = api.get(url)
    return "%s:%u" % (s.spec.portalIP, s.spec.ports[0].port)


def resolve_values(t, x):
    def resolve(x):
        if isinstance(x, list):
            return [resolve(v) for v in x]

        elif isinstance(x, dict):
            return k8s.AttrDict({k: resolve(x[k]) for k in x})

        elif isinstance(x, bool):
            return x

        return re.sub("\${([^}]+)}", lambda m: parameters[m.group(1)], x)

    parameters = {p.name: p.get("value", None) for p in t.parameters}
    return resolve(x)


def get_parameter(t, k):
    for p in t.parameters:
        if p.name == k:
            return p.get("value", "")
    return ""


def set_parameter(t, k, v):
    for p in t.parameters:
        if p.name == k:
            p.value = v
            break
    else:
        t.parameters.append({"name": k, "value": v})


def system(cmd, retry=1, **kwargs):
    print >>sys.stderr, "+ " + cmd
    if retry:
        for i in range(1, retry + 1):
            try:
                subprocess.check_call(cmd, shell=True, **kwargs)
                break
            except subprocess.CalledProcessError:
                print >>sys.stderr, "[failed, retry %u/%u]" % (i, retry)
                if i == retry:
                    raise
                else:
                    time.sleep(10)
    else:
        subprocess.call(cmd, shell=True, **kwargs)


def build_wait(b):
    while True:
        b = oapi.get("/namespaces/demo/builds/" + b.metadata.name)
        if b.status.phase not in ["New", "Pending", "Running"]:
            print >>sys.stderr, oapi.get("/namespaces/demo/builds/" + b.metadata.name + "/log", True)
            if b.status.phase == "Complete":
                return
            print >>sys.stderr, b.status.phase
            raise Exception

        time.sleep(1)


def do_build(bc):
    oapi.post("/namespaces/demo/buildconfigs", bc)

    br = k8s.API.decode({"kind": "BuildRequest",
                         "apiVersion": "v1",
                         "metadata": {"name": bc.metadata.name},
                         "from": {"kind": "BuildConfig",
                                  "name": bc.metadata.name}})

    for i in range(1, 30 + 1):
        try:
            b = oapi.post("/namespaces/demo/buildconfigs/" + bc.metadata.name + "/instantiate", br)
            break
        except Exception:
            print >>sys.stderr, "[bc instantiate failed, retry %u/%u]" % (i, 30)
            if i == 30:
                raise
            else:
                time.sleep(10)

    build_wait(b)

    oapi.delete("/namespaces/demo/builds/" + b.metadata.name)
    oapi.delete("/namespaces/demo/buildconfigs/" + bc.metadata.name)


pullcache = set()
removeset = set()
def copy_image(repo, i):
    if i.count("/") == 1:
        i = "docker.io/" + i

    newi = repo + "/" + i.split("/", 1)[1]

    if i in pullcache:
        return newi
    pullcache.add(i)

    if i != newi:
        if os.path.exists(i.split(":")[0]):
            dockerfile = open(i.split(":")[0] + "/Dockerfile").read()
            dockerfile = re.sub("FROM .*$", "FROM " + i, dockerfile, 1, re.M)
            open(i.split(":")[0] + "/Dockerfile", "w").write(dockerfile)

            system("docker build -t " + newi + " " + i.split(":")[0])
            system("docker push " + newi, 5)
            removeset.add(newi)
            removeset.add(i)
        else:
            system("docker pull " + i)
            system("docker tag " + i + " " + newi)
            system("docker push " + newi, 5)
            removeset.add(newi)
            removeset.add(i)

    return newi

def remove_images():
    for i in removeset:
        system("docker rmi " + i, 0)
    removeset.clear()

def copy_git_repo(uri):
    if uri.startswith("git://openshift.example.com/"):
        return uri

    urigit = uri
    if not urigit.endswith(".git"):
        urigit += ".git"

    root = "/var/lib/git/" + urigit.split("://", 1)[1]
    if not os.path.exists(root):
        system("git clone --bare " + uri + " " + root)
        system("chown -R nobody:nobody " + root)

    return "git://openshift.example.com/" + urigit.split("://", 1)[1]


def download_template_images(step, steps, repo):
    ts = oapi.get("/namespaces/openshift/templates")._items
    for i, t in enumerate(ts, 1):
        print >>sys.stderr, "STATUS: %d/%d: %d/%d" % (step, steps, i, len(ts))
        for o in t.objects:
            if o.kind == "DeploymentConfig":
                # return container image names, unless triggered by imageChange
                for c in o.spec.template.spec.containers:
                    for tr in o.spec.triggers:
                        if "imageChangeParams" in tr and \
                           c.name in tr.imageChangeParams.containerNames:
                            break
                    else:
                        m = re.match("^\${([^}]+)}$", c.image)
                        if not m:
                            raise Exception

                        img = get_parameter(t, m.group(1))
                        set_parameter(t, m.group(1), copy_image(repo, img))
                        c.imagePullPolicy = "IfNotPresent"

        t.kind = "Template"
        t.apiVersion = "v1"
        oapi.put("/namespaces/openshift/templates/" + t.metadata.name, t)
    remove_images()

def download_imagestream_images(step, steps, repo):
    istrs = oapi.get("/namespaces/openshift/imagestreams")._items
    for i, istr in enumerate(istrs, 1):
        print >>sys.stderr, "STATUS: %d/%d: %d/%d" % (step, steps, i, len(istrs))
        if "dockerImageRepository" in istr.spec:
            for t in istr.status.tags:
                copy_image(repo, t._items[0].dockerImageReference)
            istr.spec.dockerImageRepository = repo + "/" + istr.spec.dockerImageRepository.split("/", 1)[1]

        else:
            for t in istr.spec.tags:
                if "_from" in t and t._from.kind == "DockerImage":
                    t._from.name = copy_image(repo, t._from.name)

        istr.kind = "ImageStream"
        istr.apiVersion = "v1"
        istr.metadata = k8s.API.decode({"name": istr.metadata.name,
                                        "annotations": {"openshift.io/image.insecureRepository": "true"}})
        del istr.status

        oapi.delete("/namespaces/openshift/imagestreams/" + istr.metadata.name)
        oapi.post("/namespaces/openshift/imagestreams", istr)
    remove_images()


def download_template_git_repos(step, steps):
    ts = oapi.get("/namespaces/openshift/templates")._items
    for i, t in enumerate(ts, 1):
        print >>sys.stderr, "STATUS: %d/%d: %d/%d" % (step, steps, i, len(ts))
        for o in t.objects:
            if o.kind == "BuildConfig":
                m = re.match("^\${([^}]+)}$", o.spec.source.git.uri)
                if not m:
                    raise Exception

                uri = get_parameter(t, m.group(1))
                set_parameter(t, m.group(1), copy_git_repo(uri))

        t.kind = "Template"
        t.apiVersion = "v1"
        oapi.put("/namespaces/openshift/templates/" + t.metadata.name, t)


def download_imagestream_git_repos(step, steps):
    istrs = oapi.get("/namespaces/openshift/imagestreams")._items
    for i, istr in enumerate(istrs, 1):
        print >>sys.stderr, "STATUS: %d/%d: %d/%d" % (step, steps, i, len(istrs))
        for t in istr.spec.tags:
            if "annotations" in t and "sampleRepo" in t.annotations:
                t.annotations.sampleRepo = copy_git_repo(t.annotations.sampleRepo)

        istr.kind = "ImageStream"
        istr.apiVersion = "v1"
        istr.metadata = k8s.API.decode({"name": istr.metadata.name,
                                        "annotations": {"openshift.io/image.insecureRepository": "true"}})
        del istr.status

        oapi.delete("/namespaces/openshift/imagestreams/" + istr.metadata.name)
        oapi.post("/namespaces/openshift/imagestreams", istr)


def do_template_builds(step, steps):
    ts = oapi.get("/namespaces/openshift/templates")._items
    for i, t in enumerate(ts, 1):
        print >>sys.stderr, "STATUS: %d/%d: %d/%d" % (step, steps, i, len(ts))
        for o in t.objects:
            if o.kind == "BuildConfig":
                print >>sys.stderr, t.metadata.name

                o.metadata = k8s.API.decode({"name": "build"})
                o.spec = k8s.API.decode({"source": o.spec.source,
                                         "strategy": o.spec.strategy})
                o = resolve_values(t, o)

                do_build(o)


def do_imagestream_builds(step, steps):
    istrs = oapi.get("/namespaces/openshift/imagestreams")._items
    for i, istr in enumerate(istrs, 1):
        print >>sys.stderr, "STATUS: %d/%d: %d/%d" % (step, steps, i, len(istrs))
        for t in istr.spec.tags:
            if "annotations" in t and "sampleRepo" in t.annotations:
                print >>sys.stderr, istr.metadata.name + ":" + t.name

                bc = k8s.API.decode({"apiVersion": "v1",
                                     "kind": "BuildConfig",
                                     "metadata": {"name": "build"},
                                     "spec": {
                                       "source": {
                                         "git": {"uri": t.annotations.get("sampleRepo", ""),
                                                 "ref": t.annotations.get("sampleRef", "")},
                                         "contextDir": t.annotations.get("sampleContextDir", ""),
                                         "type": "Git"},
                                       "strategy": {
                                         "sourceStrategy": {
                                           "from": {"kind": "ImageStreamTag",
                                                    "name": istr.metadata.name + ":" + t.name,
                                                    "namespace": "openshift"}},
                                         "type": "Source"}}})

                do_build(bc)

def main():
    url = "https://openshift.example.com:8443"
    cert = ("/etc/origin/master/openshift-master.crt",
            "/etc/origin/master/openshift-master.key")

    global api, oapi
    api = k8s.API(url + "/api/v1", cert)
    oapi = k8s.API(url + "/oapi/v1", cert)

    ep = get_service_endpoint("/namespaces/default/services/image-registry")
    download_template_images(1, 6, ep)
    download_imagestream_images(2, 6, ep)
    download_template_git_repos(3, 6)
    download_imagestream_git_repos(4, 6)
    do_template_builds(5, 6)
    do_imagestream_builds(6, 6)

if __name__ == "__main__":
    main()
