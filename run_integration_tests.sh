#!/usr/bin/env bash

echo "Running integration tests triggered by $TRAVIS_EVENT_TYPE..."

pytest tests/integration/test_verify.py

# only runs if the Travis build is triggered by a cronjob, or
# $QUAY_NAMESPACE and $QUAY_ACCESS_TOKEN is set locally
if [[ $TRAVIS_EVENT_TYPE == 'cron' ]] || (! [[ -z $QUAY_NAMESPACE ]] && ! [[ -z $QUAY_ACCESS_TOKEN ]]); then
  pytest tests/integration/test_push.py
fi
