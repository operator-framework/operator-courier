class ProdConfig:
    LOG_LEVEL = "DEBUG"
    LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    REQUEST_TIMEOUT = 30

    DEFAULT_RELEASE_VERSION = "0.0.1"
    ORGANIZATIONS = {
        "operator-manifests": {}
    }
