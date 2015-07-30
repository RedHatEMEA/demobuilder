#!/bin/bash -ex

mkdir -m 0700 .ssh
ssh-keygen -f .ssh/id_rsa -N ""

cat >.ssh/config <<EOF
Host *.example.com
  StrictHostKeyChecking no
  UserKnownHostsFile /dev/null
  StrictHostKeyChecking no
  LogLevel QUIET
EOF
chmod 0600 .ssh/config

mkdir .openshift
cat >.openshift/express.conf <<EOF
default_rhlogin=demo
use_authorization_tokens=true
libra_server=$CONF_BROKER_HOSTNAME
ssl_ca_file=/etc/pki/CA/certs/ca.crt
EOF

rhc sshkey add -p $CONF_OPENSHIFT_PASSWORD1 default .ssh/id_rsa.pub
