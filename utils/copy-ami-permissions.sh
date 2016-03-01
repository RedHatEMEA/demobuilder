#!/bin/bash

if [ $# -ne 2 ]; then
    echo "Usage: $0 src-ami-[0-9a-f]{8} dst-ami-[0-9a-f]{8}"
    exit 1
fi

USERIDS=$(aws ec2 describe-image-attribute --image-id $1 --attribute launchPermission | jq -r .LaunchPermissions[].UserId | tr '\n' ' ')
aws ec2 reset-image-attribute --image-id $2 --attribute launchPermission
aws ec2 modify-image-attribute --image-id $2 --attribute launchPermission --operation-type add --user-ids $USERIDS

