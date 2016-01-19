#!/bin/bash -e

. utils/functions

sqlite3 webproxycache.db <<'EOF'
PRAGMA foreign_keys = ON;

-- Yum repodata
DELETE FROM cache WHERE url LIKE "%/repodata/%";

-- Red Hat Docker registry
DELETE FROM cache WHERE url LIKE "https://registry.access.redhat.com:443/v1/repositories/%";

-- DockerHub
DELETE FROM cache WHERE url LIKE "https://registry-1.docker.io:443/v2/%/manifests/%";
DELETE FROM cache WHERE url LIKE "https://%:443/trust/official.json";

-- PERL CPAN
DELETE FROM cache WHERE url LIKE "http://cpanmetadb.plackperl.org/v1.0/package/%";

-- Ruby gems
DELETE FROM cache WHERE url LIKE "https://%rubygems.org:443/api/v1/dependencies%";

-- Python PyPI
DELETE FROM cache WHERE url LIKE "https://pypi.python.org:443/simple/%";

-- NodeJS NPM
DELETE FROM cache WHERE url LIKE "https://registry.npmjs.org:443/%";
EOF
