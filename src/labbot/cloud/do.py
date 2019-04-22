# flake8: noqa E501
"""
*LabBot* - Digital Ocean wrapper functions
Copyright (c) 2019 Richard Clark <richardc@cybrick.com> All rights reserved.
Copyright (C) 2015 Slackbot Contributors

Training / Presentation session virtual container management system

"""
import os
import sys, traceback
import logging
import digitalocean
import time
from labbot.errors import LabCloudException, LabCloudTimeout

DO_KEY = os.environ.get("DO_API_TOKEN", None)
DO_ZONE = os.environ.get("DO_ZONE", "SFO2")
DO_SIZE = os.environ.get("DO_SIZE", "s-1vcpu-1gb")
DO_IMAGE = os.environ.get("DO_IMAGE", "ubuntu-18-04-x64")
DO_TIMEOUT = os.environ.get("DO_TIMEOUT", 600)

logger = logging.getLogger(__name__)


def validate_key():
    try:
        _account = digitalocean.Account(token=DO_KEY)
        _account.load()
    except Exception:
        return False

    return True


def create_instance(reference):
    # from pudb import set_trace; set_trace()

    if not validate_key():
        raise LabCloudException("Unable to reach cloud API / Token issue")

    try:
        _droplet = digitalocean.Droplet(
            token=DO_KEY,
            name=f"LabBot-{reference}",
            region=DO_ZONE,
            image=DO_IMAGE,
            size_slug=DO_SIZE,
            tags=["labbot", reference],
        )

        _droplet.create()

        logger.warn(f"New DO instance requested #{_droplet.id}")

        if _droplet.id is None:
            raise LabCloudException(f"DO did not return an instance ID")

        # Wait for ready
        _start = time.time()
        _waiting = True
        while _waiting:
            if time.time() - _start > DO_TIMEOUT:
                raise LabCloudException("Timeout waiting for instance to be ready")
            for action in _droplet.get_actions():
                action.load()
                logger.warn(f"Action = {action.type} {action.status}")
                if action.type == "create" and action.status == "completed":
                    _waiting = False
                    break
            time.sleep(5)

        # Return instance details
        _droplet.load()
        return (_droplet.id, _droplet.ip_address)

    except LabCloudException:
        traceback.print_exc(file=sys.stdout)
        raise
    except Exception as e:
        traceback.print_exc(file=sys.stdout)
        raise LabCloudException(f"Unhandled exception on droplet creation {e}")
