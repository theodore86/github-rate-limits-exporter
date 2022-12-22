"""
    github_rate_limits_exporter.constants
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Prometheus exporter constant variables.
"""

import dotmap

DEFAULT_LOG_FMT = "[%(levelname)s - %(asctime)s]: %(message)s"
DEFAULT_RATE_LIMITS = dotmap.DotMap(limit=0.0, used=0.0, remaining=0.0, reset=0.0)
