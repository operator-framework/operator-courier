# Contributiong to operator-courier
The following is a set of best practices for contributiong to the operator-courier project. For any questions or concerns please reach out to the AOS-Marketplace team: <aos-marketplace@redhat.com>

## Development Environment Setup
This project uses [pipenv](https://github.com/pypa/pipenv) to manage dependencies and create virual environments for development environment.

### Prerequisites
Python3

`sudo dnf install python3`

pipenv

`sudo dnf install pipenv`

### Configure virtualenv, run locally
To test the package locally, we need to install dependent pip packages in a way that does not make modifications to the local environment. To achieve this, start a `pipenv` shell

`pipenv shell`

Inside this environment all of the dependent packages are installed without polluting the local environment. For more detailed info, take a look at their (pipenv's) [starter documentation](https://pipenv.readthedocs.io/en/latest/).
