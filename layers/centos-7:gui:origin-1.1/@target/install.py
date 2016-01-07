#!/usr/bin/python

import yaml

f = "/etc/origin/master/master-config.yaml"
y = yaml.load(open(f, "r").read())
y["oauthConfig"]["identityProviders"] = [{
    "challenge": True,
    "login": True,
    "name": "basicauthpassword",
    "provider": {
        "apiVersion": "v1",
        "kind": "BasicAuthPasswordIdentityProvider",
        "url": "http://localhost:2305/"
    }
}]
open(f, "w").write(yaml.dump(y, default_flow_style=False))
