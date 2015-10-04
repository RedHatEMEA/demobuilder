#!/bin/bash -e

wait_build() {
  for ((i = 0; i < 60; i++)); do
    oc get builds | grep "$1.*Complete" && return 0
    sleep 10
  done
  oc get build "$1"
  oc build-logs "$1"
  return 1
}

oc project demo &>/dev/null
for template in $(oc get templates -n openshift | sed 1d | awk '{print $1;}'); do
  echo $template
  if oc process -n openshift $template | oc create -f - &>/dev/null; then
    for bc in $(oc get bc | sed 1d | awk '{print $1;}'); do
      wait_build "$bc-1"
      oc get build "$bc-1"
      oc build-logs "$bc-1"
    done
  fi
  oc delete all --all &>/dev/null
done
oc project default &>/dev/null

for i in $(oc get images | grep sha256 | awk '{print $1;}'); do
  oc delete image $i
done
