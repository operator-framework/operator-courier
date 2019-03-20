# Using JSON Schema for Operator Artifact Validation

## Recommended JSON Schema resources

* [Getting Started Step-By-Step][1]
* [JSON Schema Validation: A Vocabulary for Structural Validation of JSON][2]
  - in depth documentation explaining how schema validation works, including
  validation keywords.
* [python-jsonschema docs][3]

## Why define the schemas using YAML?

YAML was chosen to define the schemas, because it's more compact and so,
somewhat easier to read and write. Compare: 

```json
"customresourcedefinitions": {
    "type": "object",
    "required": [
        "owned",
    ],
    "properties": {
        "owned": {
            "type": "array",
            "items": {
                "type": "object",
                "required": [
                    "name"
                ],
                "properties": {
                    "name": {
                        "type": "string"
                    }
                }
            }
        }
    }
}

```

with

```yaml
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
                properties:
                    name:
                        type: string

```

## Organizing schemas

Schemas can be broken up using the [`definitions`][4] keyword. This can help
with re-usability and avoid excessive indenting.

## Programmatically update schemas

Some values and validation aspects will have to be decided during runtime.
`schema.ValidatorWrapper` is meant to enable just that. 

The basic idea is to have all JSON Schema validators wrapped in classes
inheriting from `ValidatorWrapper`. When some aspects need to be calculated
during runtime, these will be done _before_ `__init__()` for the validator is
called, the results passed on to `__init__()` as keyword arguments, and the
schema is updated based on these keyword arguments.

This approach was chosen to keep `ValidatorWrapper`s as simple as possible and
avoid _"hiding"_ any complicated logic in these classes.

## Custom validators

Where necessary, custom validators can be created in order to extend the
default JSON Schema. See `CourierValidator`, which extends object validation
with the `niceToHave` keyword.

Although not strictly required, it is a good practice to update the
`META_SCHEMA` when the schema is extended with new keywords, as an invalid
schema can lead to undefined behavior during validation.


[1]: https://json-schema.org/learn/getting-started-step-by-step.html
[2]: https://json-schema.org/latest/json-schema-validation.html
[3]: https://python-jsonschema.readthedocs.io/en/stable/
[4]: https://json-schema.org/latest/json-schema-validation.html#rfc.section.9
