#!/usr/bin/env bash

# Note: env QUAY_NAMESPACE, QUAY_ACCESS_TOKEN, and OMPS_HOST, or their
# argument equivalents, are required by integration tests.

function parse_docker_quay_auth() {
  python3 -c "import sys, json; \
  print(json.load(sys.stdin)['auths']['quay.io']['auth'])"
}

function parse_args() {
  while (( "$#" )); do
    case "$1" in
      --quay-namespace)
        export QUAY_NAMESPACE="$2"
        shift 2
        ;;
      --quay-access_token)
        export QUAY_ACCESS_TOKEN="$2"
        shift 2
        ;;
      --docker-config)
        export QUAY_ACCESS_TOKEN="basic $(cat "$2" | parse_docker_quay_auth)"
        shift 2
        ;;
      --omps-host)
        export OMPS_HOST="$2"
        shift 2
        ;;
      --)
        shift
        break
        ;;
      -*|--*=)
        echo "Error: Unsupported flag $1" >&2
        exit 1
        ;;
    esac
  done

  if [[ -z "$OMPS_HOST" ]]; then
    export OMPS_HOST="http://0.0.0.0:8080"
  fi
  echo "Running OMPS at \"$OMPS_HOST\""
  if [[ -z "$QUAY_NAMESPACE" ]]; then
    export QUAY_NAMESPACE="operator-manifests"
  fi
  echo "Using QUAY_NAMESPACE \"$QUAY_NAMESPACE\""
  if [[ -z "$QUAY_ACCESS_TOKEN" ]]; then
    echo "One of QUAY_ACCESS_TOKEN, --quay-access-token, or --docker-config must be set for integration tests"
    exit 1
  fi
}

set -e

parse_args $@

# Runs inside of omps repo dir in integration container.
if [[ ! -d omps ]]; then
  echo "Integration tests must run in the integration Docker container"
  exit 1
fi
./docker/install-ca.sh
gunicorn-3 \
  --daemon \
  --workers $WORKERS_NUM \
  --timeout $WORKER_TIMEOUT \
  --bind $(echo "$OMPS_HOST" | sed -E 's|(.+://)(.+)|\2|') \
  --access-logfile=- \
  --enable-stdio-inheritance \
  omps.app:app

pushd "/operator-courier"
TOXENV=py37 tox -e integration
