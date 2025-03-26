"""Configurations"""

import logging
import os
import sys

from kala.settings.consts import LOG_LEVEL, LOG_TAG  # VERSION


DEBUG = os.getenv("DEBUG", "False").lower() == "true"


handler = logging.StreamHandler(sys.stdout)
logger = logging.getLogger(LOG_TAG)
logger.addHandler(handler)
logger.setLevel(LOG_LEVEL)
