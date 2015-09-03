#!/bin/bash -e

. utils/functions

sqlite3 webproxycache.db 'PRAGMA foreign_keys = ON; DELETE FROM cache WHERE url LIKE "%/repodata/%";'
sqlite3 webproxycache.db 'PRAGMA foreign_keys = ON; DELETE FROM cache WHERE url LIKE "https://registry-1.docker.io:443/v2/%/manifests/%";'
sqlite3 webproxycache.db 'PRAGMA foreign_keys = ON; DELETE FROM cache WHERE url LIKE "https://registry.access.redhat.com:443/v1/repositories/%";'
sqlite3 webproxycache.db 'PRAGMA foreign_keys = ON; DELETE FROM cache WHERE url LIKE "https://auth.docker.io:443/%";'
