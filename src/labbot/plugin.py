# flake8: noqa E501
"""
*LabBot* {version}
Copyright (c) 2019 Richard Clark <richardc@cybrick.com> All rights reserved.
Copyright (C) 2015 Slackbot Contributors

Training / Presentation session virtual container management system
"""

import re
import logging
import simplejson as json
from machine.plugins.base import MachineBasePlugin
from machine.plugins.decorators import respond_to, listen_to
from inspect import cleandoc
from .version import __version__
from labbot.database import DB, Lab
from sqlalchemy import and_
from .lab import LabManager
from .errors import LabExists, LabCloudException, LabCloudTimeout, LabTotalExceeded
logger = logging.getLogger(__name__)


class LabBotPlugin(MachineBasePlugin):
    """
    *LabBot*
    Copyright (c) 2019 Richard Clark <richardc@cybrick.com> All rights reserved.
    Copyright (C) 2015 Slackbot Contributors

    Training / Presentation session virtual container management system

    """

    def init(self):

        # from pudb import set_trace; set_trace()
        self.db = DB(self.settings["LABBOT_DB_URL"])
        self.manager = LabManager(
            self.db,
            default_max_labs=10,
            default_lab_lifetime=60 * 60,
        )
        logger.info("LabBot active")

    # @respond_to(r"^about$")
    # def module_help(self, msg):
    # msg.reply(cleandoc(cls.__doc__).format(**{"version": __version__})

    @staticmethod
    def make_lab_status_callback(msg):
        while True:
            status_message = yield
            msg.reply_dm(f"Lab Status : {status_message}")

    @respond_to(r"^makelab$")
    def make_lab(self, msg):
        try:

            msg.reply_dm(f"Making a lab for {msg.sender.id}")
            self.manager.create_lab(msg.sender.id, self.make_lab_status_callback(msg))
            msg.reply_dm(f"Request finished")
        except (LabExists, LabTotalExceeded, LabCloudTimeout) as e:
            msg.reply_dm(f"{e}")
        except Exception as e:
            msg.reply_dm(f"Unhandled Exception {e}")
