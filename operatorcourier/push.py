import base64
import requests
import tarfile
import logging
from tempfile import TemporaryDirectory

logger = logging.getLogger(__name__)


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
        base64_bundle = self._create_base64_bundle(bundle_dir, repository)
        self._push_to_registry(namespace, repository, release, base64_bundle, auth_token)

    def _create_base64_bundle(self, bundle_dir, repository):
        with TemporaryDirectory() as temp_dir:
            tarfile_name = "{}/{}.tar.gz".format(temp_dir, repository)
            with tarfile.open(tarfile_name, "w:gz") as tar:
                tar.add(bundle_dir, "")
            with open(tarfile_name, "rb") as tarball:
                result = tarball.read()
            result64 = base64.b64encode(result).decode("utf-8")
            return result64

    def _push_to_registry(self, namespace, repository, release, bundle, auth_token):
        push_uri = 'https://quay.io/cnr/api/v1/packages/{}/{}'.format(namespace, repository)
        logger.info('Pushing bundle to {}'.format(push_uri))
        headers = {'Content-Type': 'application/json', 'Authorization': auth_token}
        json = {'blob': bundle, 'release': release, "media_type": "helm"}
        r = requests.post(push_uri, json=json, headers=headers)
        if r.status_code != 200:
            logger.error(r.text)

            msg = 'Failed to get error details'
            try:
                error = r.json()['error']
                msg = "Quay.io answered: '{}' ({})".format(
                    error['code'], error['message'])
            except Exception:
                pass

            raise ValueError("Failed to push to app registry: {}".format(msg))
