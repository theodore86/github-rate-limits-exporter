"""
    github_rate_limits_exporter.constants
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Prometheus exporter constant variables.
"""

import logging
import types

import dotmap

DEFAULT_LOG_FMT = "[%(levelname)s - %(asctime)s]: %(message)s"
DEFAULT_RATE_LIMITS = dotmap.DotMap(limit=0.0, used=0.0, remaining=0.0, reset=0.0)


LOGGING_LEVELS = types.MappingProxyType(
    {
        0: logging.CRITICAL,
        1: logging.ERROR,
        2: logging.WARNING,
        3: logging.INFO,
        4: logging.DEBUG,
    }
)
