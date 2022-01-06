# Notice 

:warning: **This project is deprecated and is no longer supported or maintained.**

AppRegistry packaging format is no longer supported by [OLM](https://github.com/operator-framework/operator-lifecycle-manager).
You can use the [Bundle](https://github.com/operator-framework/operator-registry/blob/v1.19.5/docs/design/operator-bundle.md) format and [Operator Registry](https://github.com/operator-framework/operator-registry) instead.

**What about `operator-courier verify`? How can I verify the manifests?**  

All tests and checks made by this project were moved to the project [operator-framwork/api](https://github.com/operator-framework/api) and specifically to the validator [OperatorHub](https://github.com/operator-framework/api/blob/v0.10.7/pkg/validation/internal/operatorhub.go). You can use the [operator-framwork/api](https://github.com/operator-framework/api) directly or [Operator-SDK](https://github.com/operator-framework/operator-sdk) to do these checks with the command `operator-sdk bundle validate ./bundle --select-optional name=operatorhub`([More info](https://sdk.operatorframework.io/docs/cli/operator-sdk_bundle_validate/)).

# Operator Courier

[![Build Status](https://travis-ci.org/operator-framework/operator-courier.svg?branch=master)](https://travis-ci.org/operator-framework/operator-courier)
[![Coverage Status](https://coveralls.io/repos/github/operator-framework/operator-courier/badge.svg?branch=master)](https://coveralls.io/github/operator-framework/operator-courier?branch=master)

The Operator Courier is used to build, validate and push Operator Artifacts.

Operator Courier is currently supported on Python 3.6 and above.

## Installation

- To install the latest version of operator-courier, just install the latest release from [PyPI](https://pypi.org/project/operator-courier/):

  ```bash
  $ pip3 install operator-courier
  ```

- To install a specific release, use the `==` operator and specify the version. For example:

  ```bash
  $ pip3 install operator-courier==2.0.1
  ```

- To upgrade an existing operator-courier release:

  ```bash
  $ pip3 install -U operator-courier
  ```

## Usage

### Command Line Interface

Once the project is installed, you can run the `verify` command on a directory that adheres to the expected [Manifest format](https://github.com/operator-framework/operator-registry#manifest-format).

```bash
$ operator-courier verify $MANIFESTS_DIR
```

To push the operator manifests to a quay.io app registry just use `operator-courier push`. Just pass the directory, namespace, repository, release version and quay.io authorization token needed to push.

```bash
$ operator-courier push $MANIFESTS_DIR $EXAMPLE_NAMESPACE $EXAMPLE_REPOSITORY $EXAMPLE_RELEASE "$AUTH_TOKEN"
```

Once that is created, you should be able to view your pushed application on quay.io's Application page for your particular namespace, repo, and release version (https://quay.io/application/$EXAMPLE_NAMESPACE/$EXAMPLE_REPOSITORY?tab=$EXAMPLE_RELEASE)

For more info, run help on the main program or any of the subcommands

```bash
$ operator-courier -h
$ operator-courier $SUBCOMMAND -h
```

### Debugging Validation Errors
You can optionally specify the `--verbose` flag to view detailed validation information during `verify` or `push`

```bash
$ operator-courier --verbose verify $MANIFESTS_DIR
$ operator-courier --verbose push $MANIFESTS_DIR $EXAMPLE_NAMESPACE $EXAMPLE_REPOSITORY $EXAMPLE_RELEASE "$AUTH_TOKEN"
```

For more information, please refer to the following docs about creating valid CSVs
- [Building a Cluster Service Version (CSV) for the Operator Framework](https://github.com/operator-framework/operator-lifecycle-manager/blob/master/doc/design/building-your-csv.md#your-custom-resource-definitions)
- [Required fields within your CSV](https://github.com/operator-framework/community-operators/blob/master/docs/required-fields.md#categories)


### Authentication
Currently, the quay API used by the courier can only be authenticated using quay.io's basic account token authentication. In order to get this token to authenticate with quay, a request needs to be made against the login API. This requires a normal quay.io account, and takes a username and password as parameters. This will return an auth token which can be passed to the courier.

```bash
$ AUTH_TOKEN=$(curl -sH "Content-Type: application/json" -XPOST https://quay.io/cnr/api/v1/users/login -d '
{
    "user": {
        "username": "'"${QUAY_USERNAME}"'",
        "password": "'"${QUAY_PASSWORD}"'"
    }
}' | jq -r '.token')
```

Expecting future enhancements, this authentication process will change somewhat in future releases.

## Library
To use the Operator Courier in your project, simply install the Operator Courier pip package. Then import the api module:

```python
from operatorcourier import api

def main():
    api.build_verify_and_push(NAMESPACE, RESPOSITORY, RELEASE_VERSION, AUTH_TOKEN, source_dir="./my/folder/to/manifests/")
```

## Building and running the tool locally with pip

```bash
$ pip3 install --user .
$ operator-courier
```

## Building the docker image

```sh
$ docker build -f Dockerfile -t $TAG
$ docker run $TAG operator-courier
```

For further details, please see the [contribution guide](docs/contributing.md).

## Testing

### Unit tests

[Install tox](https://tox.readthedocs.io/en/latest/install.html) and run:

```bash
$ tox
```

This will run the tests with several versions of Python 3, measure coverage,
and run flake8 for code linting.

### Integration tests

Before running integration tests, you must have write access credentials to a [quay.io](https://quay.io) namespace. See the [authentication](#authentication) section for more information.

First, build the integration docker images:

```sh
$ docker build -f tests/integration/dockerfiles/integration-base.Dockerfile -t operator-courier-integration-base:latest .
$ docker build -f tests/integration/dockerfiles/integration.Dockerfile -t operator-courier-integration:latest .
```

Then run the tests inside a container using your access credentials:

```sh
$ docker run \
  -e QUAY_NAMESPACE="$QUAY_NAMESPACE" \
  -e QUAY_ACCESS_TOKEN="$QUAY_ACCESS_TOKEN" \
  operator-courier-integration:latest \
  tox -e integration
```
