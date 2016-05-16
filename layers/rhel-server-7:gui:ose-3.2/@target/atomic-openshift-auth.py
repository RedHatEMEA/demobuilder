#!/usr/bin/python

import BaseHTTPServer
import getpass
import json
import PAM
import sys


class AuthHandler(BaseHTTPServer.BaseHTTPRequestHandler):
    def auth(self, username, password):
        def pam_conversation(pam, query_list):
            rv = []

            for (query, typ) in query_list:
                if (query, typ) == ("Password: ", PAM.PAM_PROMPT_ECHO_OFF):
                    rv.append((password, 0))
                else:
                    print >>sys.stderr, "%s: unexpected query/type %s/%s" % \
                        (username, query, typ)
                    rv.append(("", 0))

            return rv

        pam = PAM.pam()
        pam.start("password-auth", username, pam_conversation)

        try:
            pam.authenticate()
            pam.acct_mgmt()
            return True

        except PAM.error as (resp, code):
            print >>sys.stderr, "%s: auth fail (%s)" % (username, resp)

        except Exception as e:
            print >>sys.stderr, "%s: error (%s)" % (username, e)

        return False

    def do_GET(self):
        auth = self.headers.getheader("Authorization")
        if auth and auth.startswith("Basic "):
            (username, password) = auth[6:].decode("base64").split(":", 1)
            if self.auth(username, password):
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps({"sub": username}))
                return

        self.send_response(401)
        self.send_header("WWW-Authenticate", "Basic")
        self.end_headers()


if __name__ == "__main__":
    BaseHTTPServer.HTTPServer(("127.0.0.1", 2305), AuthHandler).serve_forever()
