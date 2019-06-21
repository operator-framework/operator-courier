#!/usr/bin/env bash

echo "Running integration tests triggered by $TRAVIS_EVENT_TYPE..."

pytest tests/integration/test_verify.py
