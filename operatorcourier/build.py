import os
import yaml
import operatorcourier.identify as identify


class BuildCmd():
    def _get_empty_bundle(self):
        return dict(
            data=dict(
                customResourceDefinitions=[],
                clusterServiceVersions=[],
                packages=[],
            ),
            metadata=dict(
                filenames=dict()
            )
        )

    def _get_relative_path(self, path):
        """
        :param path: the path of the file
        :return: the file name along with its parent folder
        If the file is in the root directory from where it was
        called, just return the input path.
        """
        path = os.path.normpath(path)
        parts = path.split(os.sep)
        if len(parts) > 1:
            return os.path.join(parts[-2], parts[-1])
        else:
            return path

    def _updateBundle(self, operatorBundle, file_name, yaml_string):
        # Determine which operator file type the yaml is
        operator_artifact = identify.get_operator_artifact_type(yaml_string)

        # If the file isn't one of our special types, we ignore it and return
        if operator_artifact == identify.UNKNOWN_FILE:
            return operatorBundle

        # Get the array name expected by the dictionary for the given file type
        op_artifact_plural = operator_artifact[0:1].lower() + operator_artifact[1:] + 's'

        # Marshal the yaml into a dictionary
        yaml_data = yaml.safe_load(yaml_string)

        # Add the data dictionary to the correct list
        operatorBundle["data"][op_artifact_plural].append(yaml_data)

        # Encode the dictionary into a string, then use that as a key to reference
        # the file name associated with that yaml file. Then add it to the metadata.
        if file_name != "":
            unencoded_yaml = yaml.dump(yaml_data)
            relative_path = self._get_relative_path(file_name)
            operatorBundle["metadata"]["filenames"][hash(unencoded_yaml)] = relative_path

        return operatorBundle

    def build_bundle(self, bundle_data):
        """build_bundle takes bundle_data, a list of yaml files and
        associated metadata, and generates a 'bundle'
        with those yaml files generated in the bundle format.

        :param bundle_data: Array of tuples consisting of yaml blobs
        and associated metadata for those blobs
        """
        # Generate an empty bundle
        bundle = self._get_empty_bundle()

        # For each file, append the file to the right place in the bundle
        # and add the associated metadata to the metadata field
        for data in bundle_data:
            bundle = self._updateBundle(bundle, data[0], data[1])

        return bundle
