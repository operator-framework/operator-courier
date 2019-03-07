import yaml
from operatorcourier.build import BuildCmd


class _literal(str):
    pass


def _literal_presenter(dumper, data):
    return dumper.represent_scalar('tag:yaml.org,2002:str', data, style='|')


def _get_empty_formatted_bundle():
    return dict(
        data=dict(
            customResourceDefinitions='',
            clusterServiceVersions='',
            packages='',
        )
    )


def format_bundle(bundle):
    """
    Converts a bundle object into a push-ready bundle by
    changing list values of 'customResourceDefinitions',
    'clusterServiceVersions', and 'packages' into stringified yaml literals.

    This format is required by the Marketplace backend.

    :param bundle: A bundle object
    """

    formattedBundle = _get_empty_formatted_bundle()

    yaml.add_representer(_literal, _literal_presenter)

    if 'data' not in bundle:
        return formattedBundle

    # Format data fields as string literals to match backend expected format
    if bundle['data'].get('customResourceDefinitions'):
        formattedBundle['data']['customResourceDefinitions'] = _literal(
            yaml.dump(bundle['data']['customResourceDefinitions'],
                      default_flow_style=False))

    if 'clusterServiceVersions' in bundle['data']:
        # Format description and alm-examples
        clusterServiceVersions = []
        for csv in bundle['data']['clusterServiceVersions']:
            if csv.get('metadata', {}).get('annotations', {}).get('alm-examples'):
                csv['metadata']['annotations']['alm-examples'] = _literal(
                    csv['metadata']['annotations']['alm-examples'])

            if csv.get('spec', {}).get('description'):
                csv['spec']['description'] = _literal(csv['spec']['description'])

            clusterServiceVersions.append(csv)

        if clusterServiceVersions:
            formattedBundle['data']['clusterServiceVersions'] = _literal(
                yaml.dump(clusterServiceVersions, default_flow_style=False))

    if bundle['data'].get('packages'):
        formattedBundle['data']['packages'] = _literal(
            yaml.dump(bundle['data']['packages'], default_flow_style=False))

    return formattedBundle


def unformat_bundle(formattedBundle):
    """
    Converts a push-ready bundle into a structured object by changing
    stringified yaml of 'customResourceDefinitions', 'clusterServiceVersions',
    and 'packages' into lists of objects.
    Undoing the format helps simplify bundle validation.

    :param formattedBundle: A push-ready bundle
    """

    bundle = BuildCmd()._get_empty_bundle()

    if 'data' not in formattedBundle:
        return bundle

    if 'customResourceDefinitions' in formattedBundle['data']:
        customResourceDefinitions = yaml.safe_load(
            formattedBundle['data']['customResourceDefinitions'])
        if customResourceDefinitions:
            bundle['data']['customResourceDefinitions'] = customResourceDefinitions

    if 'clusterServiceVersions' in formattedBundle['data']:
        clusterServiceVersions = yaml.safe_load(
            formattedBundle['data']['clusterServiceVersions'])
        if clusterServiceVersions:
            bundle['data']['clusterServiceVersions'] = clusterServiceVersions

    if 'packages' in formattedBundle['data']:
        packages = yaml.safe_load(formattedBundle['data']['packages'])
        if packages:
            bundle['data']['packages'] = packages

    return bundle
