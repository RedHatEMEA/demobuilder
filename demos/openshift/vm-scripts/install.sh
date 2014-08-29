#!/bin/bash

. vm-functions

ose_install() {
  curl -so /tmp/openshift.sh https://raw.githubusercontent.com/openshift/openshift-extras/enterprise-2.1/enterprise/install-scripts/generic/openshift.sh
  chmod 0755 /tmp/openshift.sh

  /tmp/openshift.sh
}

enable_admin_console() {
  sed -i -e '/ProxyPassReverse \/console/ a\
  ProxyPass /admin-console http://127.0.0.1:8080/admin-console' /etc/httpd/conf.d/000002_openshift_origin_broker_proxy.conf
  sed -i -e '/ProxyPassReverse \/console/ a\
  ProxyPass /assets http://127.0.0.1:8080/assets' /etc/httpd/conf.d/000002_openshift_origin_broker_proxy.conf

  service httpd reload
}

ose_node_configure() {
  sed -i -e 's/^cpu_cfs_quota_us=.*/cpu_cfs_quota_us=-1/' /etc/openshift/resource_limits.conf
  service ruby193-mcollective restart
}

export CONF_NO_SCRAMBLE=true
export CONF_OPENSHIFT_PASSWORD1=redhat

register_channels jbappplatform-6-x86_64-server-6-rpm jb-ews-2-x86_64-server-6-rpm rhel-x86_64-server-6 rhel-x86_64-server-6-rhscl-1 rhel-x86_64-server-6-ose-2.1-infrastructure rhel-x86_64-server-6-ose-2.1-jbosseap rhel-x86_64-server-6-ose-2.1-node rhel-x86_64-server-6-ose-2.1-rhc

ose_install
enable_admin_console
ose_node_configure

curl -so /tmp/jbdevstudio.jar http://download.eng.rdu2.redhat.com/released/jbdevstudio/7.1.1/jbdevstudio-product-universal-7.1.1.GA-v20140314-2145-B688.jar
java -jar /tmp/jbdevstudio.jar jbds.xml

# nexus
# add apps

cleanup
poweroff
