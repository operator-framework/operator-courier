general_required_fields = [
    "spec"
]

metadata_required_fields = [
    {
        "field": "annotations",
        "description": "Without this field, your operator will be missing "
                       "essential data for the UI. Please add this field to the "
                       "CSV and run validation again to see what subfields "
                       "are required.",
        "required": True
    }
]

metadata_annotations_required_fields = [
    {
        "field": "description",
        "description": "Without this field, the description displayed in "
                       "the tiles of the UI will be a truncated "
                       "version of spec.description.",
        "required": False
    },
    {
        "field": "categories",
        "description": "Without this field, the operator will be "
                       "categorized as Other.",
        "required": False
    },
    {
        "field": "capabilities",
        "description": "Without this field, the operator will be assigned "
                       "the basic install capability - you can read more "
                       "about operator maturity models here "
                       "https://www.operatorhub.io/getting-started#How-do-I-start-writing-an-Operator?.",  # noqa
        "required": False
    },
    {
        "field": "repository",
        "description": "Without this field, the link to the operator source "
                       "code will not be displayed in the UI.",
        "required": False
    },
    {
        "field": "createdAt",
        "description": "Without this field, the time stamp at which the "
                       "operator was created will not be displayed in the UI.",
        "required": False
    },
    {
        "field": "containerImage",
        "description": "Without this field, the link to the operator "
                       "image will not be displayed in the UI.",
        "required": False
    },
    {
        "field": "alm-examples",
        "description": "Without this field, users will not have examples "
                       "of how to write Custom Resources for the operator.",
        "required": False
    }
]

spec_required_fields = [
    {
        "field": "displayName",
        "description": "Without this field, the name of the operator for "
                       "both the tile and the details view will default "
                       "to metadata.name.",
        "required": True
    },
    {
        "field": "description",
        "description": "Without this field, the description in the details "
                       "view of the operator will default to "
                       "metadata.annotations.description.",
        "required": True
    },
    {
        "field": "version",
        "description": "Without this field, the version in the details "
                       "view of the operator will be empty.",
        "required": True
    },
    {
        "field": "links",
        "description": "Without this field, no links will be displayed "
                       "in the details page side panel. You can for "
                       "example link to some additional Documentation, "
                       "related Blogs or Repositories.",
        "required": False
    },
    {
        "field": "icon",
        "description": "Without this field, the operator will display "
                       "a default operator framework icon.",
        "required": False
    },
    {
        "field": "provider",
        "description": "Without this field, users will not be able "
                       "to filter for provider.",
        "required": True
    },
    {
        "field": "maintainers",
        "description": "Without this field, the operator details page "
                       "will not display the name and contact for users "
                       "to get support in using the operator. "
                       "The field should be a yaml list of name & email pairs.",
        "required": False
    },
    {
        "field": "customresourcedefinitions",
        "description": "Without this field, the operator details page will "
                       "not display any CRDs the operator needs "
                       "in order to function.",
        "required": False
    },
    {
        "field": "installModes",
        "description": "Without this field, OLM will not be able "
                       "to deploy your operator.",
        "required": True
    }
]
