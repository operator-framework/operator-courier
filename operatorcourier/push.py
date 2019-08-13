import os
import base64
import requests
import tarfile
import logging
from tempfile import TemporaryDirectory
from operatorcourier.errors import (
    OpCourierQuayCommunicationError,
    OpCourierQuayErrorResponse
)
from operatorcourier.manifest_parser import filterOutFiles

logger = logging.getLogger(__name__)
# BLACK_LIST is a list of files to be removed from the manifest directory
BLACK_LIST = ["art.yaml", "image-references"]


class PushCmd():
    name = 'push'

    def __init__(self):
        pass

    def push(self, bundle_dir, namespace, repository, release, auth_token):
        """Push takes a bundle and pushes it to the specified app registry repository.

        :param bundle_dir: Path to generated local directory that contains the bundle.
        :param namespace: Namespace that contains the repository for the application.
        :param repository: Repository name of the application described by the bundle.
        :param release: Release version of the bundle.
        :param auth_token: Authentication token used to push to Quay.io.
        """
        logger.info('Generating 64 bit bundle and pushing to app registry.')
        filterOutFiles(bundle_dir, BLACK_LIST)
        base64_bundle = self._create_base64_bundle(bundle_dir, repository)
        self._push_to_registry(namespace, repository, release, base64_bundle, auth_token)

    def _create_base64_bundle(self, bundle_dir, repository):
        with TemporaryDirectory() as temp_dir:
            tarfile_name = os.path.join(temp_dir, "%s.tar.gz" % repository)
            with tarfile.open(tarfile_name, "w:gz") as tar:
                tar.add(bundle_dir, os.path.basename(bundle_dir))
            with open(tarfile_name, "rb") as tarball:
                result = tarball.read()
            result64 = base64.b64encode(result).decode("utf-8")
            return result64

    def _push_to_registry(self, namespace, repository, release, bundle, auth_token):
        push_uri = 'https://quay.io/cnr/api/v1/packages/%s/%s' % (namespace, repository)
        logger.info('Pushing bundle to %s' % push_uri)
        headers = {'Content-Type': 'application/json', 'Authorization': auth_token}
        json = {'blob': bundle, 'release': release, "media_type": "helm"}

        try:
            r = requests.post(push_uri, json=json, headers=headers)
        except requests.RequestException as e:
            msg = str(e)
            logger.error(msg)
            raise OpCourierQuayCommunicationError(msg)

        if r.status_code != 200:
            logger.error(r.text)

            try:
                r_json = r.json()
            except ValueError:
                r_json = {}

            msg = r_json.get('error', {}).get(
                'message', 'Failed to get error details.'
            )
            raise OpCourierQuayErrorResponse(msg, r.status_code, r_json)
