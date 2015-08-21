#!/bin/bash -e

. utils/functions

sqlite3 webproxycache.db 'DELETE FROM cache WHERE url LIKE "%/repodata/%";'
sqlite3 webproxycache.db 'DELETE FROM cache WHERE url LIKE "https://registry-1.docker.io:443/v2/%/manifests/%";'
sqlite3 webproxycache.db 'DELETE FROM cache WHERE url LIKE "https://registry.access.redhat.com:443/v1/repositories/%";'
