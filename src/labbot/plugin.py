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
            self.db, default_max_labs=10, default_lab_lifetime=60 * 60
        )
        self.admin_channel = self.settings.get("ADMIN_CHANNEL", None)
        logger.info("LabBot active")

    # @respond_to(r"^about$")
    # def module_help(self, msg):
    # msg.reply(cleandoc(cls.__doc__).format(**{"version": __version__})

    @staticmethod
    def make_lab_status_callback(msg):
        while True:
            status_message = yield
            msg.reply_dm(f"Lab Status : {status_message}")

    @respond_to(r"^lab reset$", re.IGNORECASE)
    def lab_reset(self, msg):

        if self.admin_channel is None:
            self.admin_channel = msg.channel.id
            logger.warn(f"admin channel set to {self.admin_channel}\n{msg.channel}")

        if msg.channel.id != self.admin_channel:
            logger.warn(f"Unauthorized admin command")
            return

        msg.reply(f"Resetting labs")
        self.manager.destroy_all(self.make_lab_status_callback(msg))

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

    @respond_to(r"^killlab$")
    def kill_lab(self, msg):
        try:

            msg.reply_dm(f"Destroying lab for {msg.sender.id}")
            self.manager.destroy_lab(msg.sender.id, self.make_lab_status_callback(msg))
            msg.reply_dm(f"Request finished")
        except (LabExists, LabTotalExceeded, LabCloudTimeout) as e:
            msg.reply_dm(f"{e}")
        except Exception as e:
            msg.reply_dm(f"Unhandled Exception {e}")
