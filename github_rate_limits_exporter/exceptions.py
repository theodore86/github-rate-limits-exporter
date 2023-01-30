"""
    github_rate_limits_exporter.exceptions
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Prometheus exporter custom exceptions.
"""

from github import GithubException
from requests import RequestException
from urllib3.exceptions import HTTPError


class Error(Exception):
    """
    This class is the base of all exceptions raised
    by github_rate_limits_exporter
    """


class ArgumentError(Error):
    """An error from creating or using an argument"""


# Those exceptions will be handle gracefully by the main thread.
ERROR_STATUS_ON_EXCEPTIONS = (
    Error,
    ValueError,
    GithubException,
    RequestException,
    HTTPError,
)
