import yaml
import operatorcourier.identify as identify

class BuildCmd():
    def _get_empty_bundle(self):
         return dict(
            data = dict(
                customResourceDefinitions = [],
                clusterServiceVersions = [],
                packages = [],
            )
        )
    
    def _get_field_entry(self, yamlContent):
        yaml_type = identify.get_operator_artifact_type(yamlContent)
        return yaml_type[0:1].lower() + yaml_type[1:] + 's'

    def _updateBundle(self, operatorBundle, yamlContent):
        operatorBundle["data"][self._get_field_entry(yamlContent)].append(yaml.safe_load(yamlContent))
        return operatorBundle

    def build_bundle(self, strings):
        """build_bundle takes an array of yaml files and generates a 'bundle' with those yaml files
        generated in the bundle format.

        :param strings: Array of yaml strings to bundle
        """
        bundle =  self._get_empty_bundle()
        for item in strings:
            bundle = self._updateBundle(bundle, item)

        return bundle
