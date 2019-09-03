#!/usr/bin/env bash

# Note: env QUAY_NAMESPACE, QUAY_ACCESS_TOKEN, and OMPS_HOST are required by
# integration tests.

TOXENV=py37 tox -e integration

# TODO: create Subscription for OLM to pull and run.
