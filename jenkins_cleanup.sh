#!/bin/sh
mkdir -p /home/mohan/to_deploy/${JOB_NAME}/
rm -f /home/mohan/to_deploy/${JOB_NAME}/*.rpm
cp target/rpm/**/RPMS/noarch/*.rpm /home/mohan/to_deploy/${JOB_NAME}