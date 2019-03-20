# Using Draft4Validator until jsonschema 3.x is released for Fedora 29.
import json
import yaml
from jsonschema import (
    Draft4Validator,
    ValidationError,
    FormatChecker,
    validators)


class ValidationWarning(ValidationError):
    """Differentiate warnings from errors"""
    pass


def validate_niceToHave(validator, niceToHave, instance, schema):
    """Validate an instance against a niceToHave schema

    Based on the implementation of `jsonschema._validators.required_draft4`.
    """
    if not validator.is_type(instance, "object"):
        return
    for property in niceToHave:
        if property not in instance:
            yield ValidationWarning(f"{property!r} is not defined")


# Create a custom validator by extending Draft4Validator.
CourierValidator = validators.extend(Draft4Validator, validators={
        'niceToHave': validate_niceToHave})
# Make sure, META_SCHEMA for the new validator is detached from the base one.
CourierValidator.META_SCHEMA = CourierValidator.META_SCHEMA.copy()
# `niceToHave` is similar to `required`:
# https://json-schema.org/latest/json-schema-validation.html#rfc.section.6.5.3
CourierValidator.META_SCHEMA['properties']['niceToHave'] = {
    '$ref': '#/properties/required'
}

CourierFormatChecker = FormatChecker()


@CourierFormatChecker.checks('jsonString', raises=json.JSONDecodeError)
def is_json_string(value):
    json.loads(value)
    return True


class ValidatorWrapper:
    """Wraps validators, to enable schema updates during __init__()"""
    schema = None

    def __init__(self, format_checker=CourierFormatChecker):
        self.validator = CourierValidator(self.schema,
                                          format_checker=format_checker)

    def iter_errors(self, data):
        for error in self.validator.iter_errors(data):
            yield error

    def check_schema(self):
        self.validator.check_schema(self.schema)


class CustomResourceDefinition(ValidatorWrapper):
    """CRD validator"""
    schema = yaml.safe_load("""---
$schema: http://json-schema.org/draft-04/schema#
title: Schema of a Custom Resource Definition

type: object

required:
    - metadata
    - apiVersion
    - spec

properties:
    metadata:
        type: object
        required:
            - name
        properties:
            name:
                type: string
    apiVersion: {}
    spec:
        type: object
        required:
            - names
            - group
            - version
        properties:
            names:
                type: object
                required:
                    - kind
                    - plural
                properties:
                    kind: {}
                    plural: {}
            group: {}
            version: {}
""")


class ClusterServiceVersion(ValidatorWrapper):
    """CSV validator

    Args:
        crd_list: list of strings with CRD names. The `name` attribute of the
            items in spec.customresourcedefinitions.owned[] will have to match
            one of these.
    """
    def __init__(self, crd_list=None):
        if crd_list:
            (self.schema['definitions']['spec']['properties']
                ['customresourcedefinitions']['properties']
                ['owned']['items']['properties']
                ['name']['enum']) = crd_list
        super(ClusterServiceVersion, self).__init__()

    schema = yaml.safe_load("""---
$schema: http://json-schema.org/draft-04/schema#
title: Schema of a Cluster Service Version

type: object

required:
    - metadata
    - apiVersion
    - spec

properties:
    metadata:
        $ref: "#/definitions/metadata"
    apiVersion:
        $ref: "#/definitions/apiVersion"
    spec:
        $ref: "#/definitions/spec"

definitions:
    metadata:
        type: object
        required:
            - name
        niceToHave:
            - annotations
        properties:
            name:
                type: string
            annotations:
                type: object
                niceToHave:
                    - certified
                    - categories
                    - description
                    - containerImage
                    - createdAt
                    - support
                properties:
                    certified:
                        type: string
                    categories: {}
                    description: {}
                    containerImage: {}
                    createdAt: {}
                    support: {}
                    alm-examples:
                        type: string
                        format: jsonString
    apiVersion: {}
    spec:
        type: object
        required:
            - install
            - installModes
        niceToHave:
            - displayName
            - description
            - icon
            - version
            - provider
            - maturity
        properties:
            displayName: {}
            description: {}
            icon: {}
            version: {}
            provider: {}
            maturity: {}
            installModes: {}
            install:
                type: object
                required:
                    - strategy
                    - spec
                properties:
                    strategy:
                        type: string
                        enum: ["deployment"]
                    spec:
                        type: object
                        required:
                            - deployments
                        properties:
                            deployments:
                                type: array
                            permissions:
                                type: array
                            clusterPermissions:
                                type: array
            customresourcedefinitions:
                type: object
                required:
                    - owned
                properties:
                    owned:
                        type: array
                        items:
                            type: object
                            required:
                                - name
                                - kind
                                - version
                            properties:
                                name:
                                    type: string
                                kind: {}
                                version: {}
""")
