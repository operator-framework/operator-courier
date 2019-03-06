# Operator Courier

The Operator Courier is used to build, validate and push Operator Artifacts.

## Usage

### Command Line Interface
To install the operator courier project to use from the command line, just install the latest release from [PyPI](https://pypi.org/project/operator-courier/):

```bash
$ pip3 install operator-courier
```

Once the project is installed, you can verify that a set of files is valid and can be bundled and pushed. First, create a flat directory containing all of the CSV, CRD and PACKAGE files that are included in your bundle.  Then just use `operator-courier verify` to test it.

```bash
$ operator-courier verify $BUNDLE_DIR
```

To generate an operator bundle and push it to a quay.io app registry just use `operator-courier push`. Just pass the directory, namespace, repository, release version and quay.io authorization token needed to push.

```bash
$ operator-courier push $BUNDLE_DIR $EXAMPLE_NAMESPACE $EXAMPLE_REPOSITORY $EXAMPLE_RELEASE "$AUTH_TOKEN"
```

Once that is created, you should be able to view your bundle on quay.io's Application page for your particular namespace, repo, and release version (https://quay.io/application/$EXAMPLE_NAMESPACE/$EXAMPLE_REPOSITORY?tab=$EXAMPLE_RELEASE)

For more info, run help on any of the subcommands

```bash
$ operator-courier -h
$ operator-courier push -h
```

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

```
from operatorcourier import api

def main():
    api.build_verify_and_push($your_namespace, $your_repository, $your_release_version, $your_quay_authtoken, source_dir="./my/folder/to/bundle/")
```

We also support passing a list of strings that make up the bundle by specifying the `yamls=` parameter, i.e.:

`api.build_verify_and_push($your_namespace, $your_repository, $your_release_version, $your_quay_authtoken, yamls=$your_yamls_list)`

## Building and running the tool locally with pip
```bash
$ pip3 install --user .

$ operator-courier
```

## Testing

### Running the tests

[Install tox](https://tox.readthedocs.io/en/latest/install.html) and run:

```bash 
$ tox
```

This will run the tests with several versions of Python 3, measure coverage,
and run flake8 for code linting.
