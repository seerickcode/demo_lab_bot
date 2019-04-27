# flake8: noqa E501
"""
*LabBot* - Digital Ocean wrapper functions
Copyright (c) 2019 Richard Clark <richardc@cybrick.com> All rights reserved.
Copyright (C) 2015 Slackbot Contributors

Training / Presentation session virtual container management system

"""

import os
import CloudFlare
import logging
from labbot.errors import LabConfigMissing

logger = logging.getLogger(__name__)

CF_API_KEY = os.environ.get("CF_API_KEY", None)
CF_API_EMAIL = os.environ.get("CF_API_EMAIL", None)
CF_ZONE = os.environ.get("CF_ZONE", None)
CF_ZONE_PREFIX = os.environ.get("CF_ZONE_PREFIX", ".lab")


def check_config():

    if CF_ZONE is None:
        raise LabConfigMissing("CF_ZONE not configured")

    if CF_API_KEY is None:
        raise LabConfigMissing("CF_API_KEY not configured")

    if CF_API_EMAIL is None:
        raise LabConfigMissing("CF_API_EMAIL not configured")


def create_lab_a_record(reference, ip_address):

    check_config()
    cf = CloudFlare.CloudFlare(debug=True, email=CF_API_EMAIL, token=CF_API_KEY)
    record = {"name": reference + CF_ZONE_PREFIX, "type": "A", "content": ip_address, "ttl": 120}
    r = cf.zones.dns_records.post(CF_ZONE, data=record)
    return (r.get("id"), r.get("name"))


def delete_lab_a_record(record_id):

    try:
        check_config()
        cf = CloudFlare.CloudFlare(debug=True, email=CF_API_EMAIL, token=CF_API_KEY)
        r = cf.zones.dns_records.delete(CF_ZONE, record_id)
        return r.get("id")
    except CloudFlare.exceptions.CloudFlareAPIError:
        logger.warn(f"CF record missing / already destroyed ? #{record_id}")
        return
