#!/bin/bash -ex

oadm new-project logging
oc project logging

openshift admin ca create-server-cert --key=kibana.key --cert=kibana.crt --hostnames=kibana,kibana.example.com,kibana-ops.example.com --signer-cert=/etc/origin/master/ca.crt --signer-key=/etc/origin/master/ca.key --signer-serial=/etc/origin/master/ca.serial.txt
oc secrets new logging-deployer kibana.crt=kibana.crt kibana.key=kibana.key kibana-ops.crt=kibana.crt kibana-ops.key=kibana.key server-tls.json=server-tls.json ca.crt=/etc/origin/master/ca.crt ca.key=/etc/origin/master/ca.key

oc create -f - <<EOF
apiVersion: v1
kind: ServiceAccount
metadata:
  name: logging-deployer
secrets:
- name: logging-deployer
EOF

oc policy add-role-to-user edit system:serviceaccount:logging:logging-deployer

(oc get -o yaml scc privileged; echo - system:serviceaccount:logging:aggregated-logging-fluentd) | oc replace scc privileged -f -
oadm policy add-cluster-role-to-user cluster-reader system:serviceaccount:logging:aggregated-logging-fluentd

POD=$(oc process logging-deployer-template -n openshift -v KIBANA_HOSTNAME=kibana.example.com,ES_CLUSTER_SIZE=1,PUBLIC_MASTER_URL=https://openshift.example.com:8443 | oc create -f - | cut -d '"' -f2)
while [ "$(oc get pod $POD -o template --template='{{.status.phase}}')" != "Succeeded" ]; do
  sleep 1
done

oc process logging-support-template | oc create -f -

while [ "$(oc get dc logging-fluentd -n logging -o template --template '{{.status.latestVersion}}')" != "1" ]; do
  sleep 1
done
oc scale dc/logging-fluentd --replicas=1

sleep 60
oc get dc -o yaml | sed -e 's/imagePullPolicy: .*/imagePullPolicy: IfNotPresent/' | oc replace -f -

oc delete sa/logging-deployer secret/logging-deployer

sed -i -e '/^assetConfig:/ a \
  loggingPublicURL: "https://kibana.example.com/"' /etc/origin/master/master-config.yaml
service atomic-openshift-master restart

oc project default
