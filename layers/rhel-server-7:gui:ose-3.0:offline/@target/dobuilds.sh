#!/bin/bash -e

oc project demo &>/dev/null
for template in $(oc get templates -n openshift | sed 1d | awk '{print $1;}'); do
  echo $template
  if oc process -n openshift $template | oc create -f - &>/dev/null; then
    for bc in $(oc get bc | sed 1d | awk '{print $1;}'); do
      oc start-build --follow $bc
    done
  fi
  oc delete all --all &>/dev/null
done
oc project default &>/dev/null
