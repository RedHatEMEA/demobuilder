#!/bin/bash -ex

oc project openshift-infra

oc create -f - <<EOF
apiVersion: v1
kind: ServiceAccount
metadata:
  name: metrics-deployer
secrets:
- name: metrics-deployer
EOF

oadm policy add-role-to-user edit system:serviceaccount:openshift-infra:metrics-deployer
oadm policy add-cluster-role-to-user cluster-reader system:serviceaccount:openshift-infra:heapster

openshift admin ca create-server-cert --key=hawkular-metrics.key --cert=hawkular-metrics.crt --hostnames=hawkular-metrics,hawkular-metrics.example.com --signer-cert=/etc/origin/master/ca.crt --signer-key=/etc/origin/master/ca.key --signer-serial=/etc/origin/master/ca.serial.txt
cat hawkular-metrics.key hawkular-metrics.crt >hawkular-metrics.pem

oc secrets new metrics-deployer hawkular-metrics.pem=hawkular-metrics.pem hawkular-metrics-ca.cert=/etc/origin/master/ca.crt

POD=$(oc process metrics-deployer-template -n openshift -v HAWKULAR_METRICS_HOSTNAME=hawkular-metrics.example.com,USE_PERSISTENT_STORAGE=false,IMAGE_PREFIX=openshift3/,IMAGE_VERSION=latest  | oc create -f - | cut -d '"' -f2)
while [ "$(oc get pod $POD -o template --template='{{.status.phase}}')" != "Succeeded" ]; do
  sleep 1
done

oc get rc -o yaml | sed -e 's/imagePullPolicy: .*/imagePullPolicy: IfNotPresent/' | oc replace -f -
oc delete pods --all

sed -i -e '/^assetConfig:/ a \
  metricsPublicURL: "https://hawkular-metrics.example.com/hawkular/metrics"' /etc/origin/master/master-config.yaml
service atomic-openshift-master restart

oc project default
