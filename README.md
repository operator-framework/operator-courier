# Operator Courier

The Operator Courier is used to build, validate and push Operator Artifacts.

It is currently in a pre-alpha stage.

## Usage
To use the Operator Courier in your project, simply install the Operator Courier pip package. Then import the api module:

```
from operatorcourier import api

def main():
    api.build_verify_and_push($your_namespace, $your_repository, $your_release_version, $your_quay_authtoken, source_dir="./my/folder/to/bundle/")
```

We also support passing a list of strings that make up the bundle by specifying the `yamls=` parameter, i.e.:

`api.build_verify_and_push($your_namespace, $your_repository, $your_release_version, $your_quay_authtoken, yamls=$your_yamls_list)`

Not only that, but we also support the use of the tool as a command line interface. Just invoke `operator-courier` from a shell:

```bash
$ operator-courier verify --source_dir="./temp/bundles/couchbase/"
```

For more information run `operator-courier -h`

## Building and running the tool locally with pip
```bash
$ pip install --user .

$ operator-courier
```

## Testing

### Running the tests
```bash 
$ python3 setup.py test
```
