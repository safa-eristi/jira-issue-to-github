import logging
import os

def configure_app(app):
    """
    set environment variable and
    override secret values that needs to stay on machine
    """
    app.url_map.strict_slashes = False
    app.config['PROPAGATE_EXCEPTIONS'] = True

    request_logger = logging.getLogger("general_logger")
    request_logger.setLevel(logging.DEBUG)
    handler = logging.FileHandler("/var/log/webhook/request.log")
    formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
    handler.setFormatter(formatter)
    request_logger.addHandler(handler)

    fail_logger = logging.getLogger("fail_logger")
    fail_logger.setLevel(logging.DEBUG)
    handler = logging.FileHandler("/var/log/webhook/fail.log")
    formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
    handler.setFormatter(formatter)
    fail_logger.addHandler(handler)
