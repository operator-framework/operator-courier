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
$ operator-courier push $BUNDLE_DIR $EXAMPLE_NAMESPACE $EXAMPLE_REPOSITORY $EXAMPLE_RELEASE $AUTH_TOKEN
```

Once that is created, you should be able to view your bundle on quay.io's Application page for your particular namespace, repo, and release version (https://quay.io/application/$EXAMPLE_NAMESPACE/$EXAMPLE_REPOSITORY?tab=$EXAMPLE_RELEASE)

For more info, run help on any of the subcommands

```bash
$ operator-courier -h
$ operator-courier push -h
```

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
```bash 
$ python3 setup.py test
```
