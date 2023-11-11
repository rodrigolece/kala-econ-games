"""Configurations"""
import logging
import sys

from kala.settings.consts import LOG_LEVEL, LOG_TAG  # VERSION


handler = logging.StreamHandler(sys.stdout)
logger = logging.getLogger(LOG_TAG)
logger.addHandler(handler)
logger.setLevel(LOG_LEVEL)
