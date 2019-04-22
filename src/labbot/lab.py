# flake8: noqa E501
"""
*LabBot* - Lab instance managment
Copyright (c) 2019 Richard Clark <richardc@cybrick.com> All rights reserved.
Copyright (C) 2015 Slackbot Contributors

"""

import logging
import threading
import time
import sys
import traceback
from labbot.database import DB, Lab, LabStatus
from labbot.singleton import Singleton
from labbot.errors import LabExists, LabTotalExceeded
from labbot.cloud.do import create_instance
from labbot.cloud.cloudflare import create_lab_a_record, delete_lab_a_record

logger = logging.getLogger(__name__)


class LabManager(object, metaclass=Singleton):
    def __init__(self, db, default_max_labs, default_lab_lifetime):
        self.db = db
        self.max_labs = default_max_labs
        self.lab_lifetime = default_lab_lifetime
        self.list_lock = threading.Lock()
        self._labs = dict()
        with self.db.session() as s:
            _labs_query = s.query(Lab)
            for _lab in _labs_query:
                self._labs[str(_lab.id)] = _lab

    def create_lab(self, slack_id, status_callback=None):

        if status_callback is not None:
            next(status_callback)

        lab = None
        with self.db.session() as s:
            with self.list_lock:
                if len(self._labs) >= self.max_labs:
                    raise LabTotalExceeded(
                        f"Sorry, there are already {self.max_labs} allocated, try again later"
                    )
                for k, v in self._labs.items():
                    v = s.merge(v)
                    if v.slack_owner_id == slack_id:
                        raise LabExists(
                            f"Slack ID {slack_id} already has an active/stuck lab"
                        )

                lab = Lab(slack_owner_id=slack_id, status=LabStatus.WAITING_INSTANCE)
                s.add(lab)
                self._labs[str(lab.id)] = lab
                s.commit()

            logger.debug(
                f"Creating new Lab {lab.id} for slack client {lab.slack_owner_id}"
            )

            # Finish with the lock as quick as we can
            # and now go through the stages to create the lab
            if status_callback is not None:
                status_callback.send("Starting Instance Creation")

            try:
                _instance_id, _ip = create_instance(lab.slack_owner_id)
                lab.do_reference = _instance_id
                lab.ip = _ip
                lab.status = LabStatus.WAITING_DNS
                s.commit()

                # Setup DNS record
                if status_callback is not None:
                    status_callback.send("Instance Ready - Setting up DNS")

                dns_reference, dns_url = create_lab_a_record(lab.slack_owner_id, lab.ip)
                lab.cf_reference = dns_reference
                lab.url = f"http://{dns_url}:8443"
                lab.status = LabStatus.WAITING_HEALTH
                s.commit()

                # Validate URL
                if status_callback is not None:
                    status_callback.send(f"Doing Health Check on {lab.url}")

                time.sleep(5)

                lab.status = LabStatus.ACTIVE
                s.commit()

                if status_callback is not None:
                    status_callback.send(f"Instance Ready to use at {lab.url}")
                    status_callback.close()

                return lab
            except Exception as e:
                traceback.print_exc(file=sys.stdout)
                logger.error(f"Instance Creation Error {e}")
                lab.status = LabStatus.UNKNOWN
                s.commit()
                if status_callback is not None:
                    status_callback.send(f"Instance Failed - {e}")
                    status_callback.close()

    def delete_lab(self, lab):
        pass

    def delete_lab_by_slack_id(self, slack_id):
        pass

    def expire_labs(self):
        pass
