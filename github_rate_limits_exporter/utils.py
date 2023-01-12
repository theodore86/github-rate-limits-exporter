"""
    github_rate_limits_exporter.utils
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Prometheus exporter utilities/helper functions.
"""

import base64
import binascii
import datetime
import logging
import signal
import socket
import sys
from types import FrameType
from typing import Optional

from github_rate_limits_exporter.constants import DEFAULT_LOG_FMT


def get_unix_timestamp() -> float:
    """
    Get unix timestamp in UTC.

    :returns int: UTC in unix timestamp.
    """
    return datetime.datetime.now(datetime.timezone.utc).timestamp()


def is_string_base64_encoded(string: str) -> bool:
    """
    Check if string argument is base64 encoded.

    :string str: The input string.
    :returns bool: ``True`` if base64 encoded else ``False``.
    """
    try:
        return base64.b64encode(base64.b64decode(string)).decode() == string
    except binascii.Error:
        return False


def base64_decode(string: str) -> str:
    """
    Decode base64 encoded input string.

    :string str: Base64 encoded input string.
    :returns str: The base64 decoded string (if encoded).
    """
    if is_string_base64_encoded(string):
        return base64.b64decode(string).decode()
    return string


def initialize_logger(level: int) -> None:
    """
    Initialize and setup the level of effectiveness.

    :param int level: Verbosity level (0...4)
    :returns: Nothing.
    """
    levels = {
        0: logging.CRITICAL,
        1: logging.ERROR,
        2: logging.WARNING,
        3: logging.INFO,
        4: logging.DEBUG,
    }
    console = logging.StreamHandler(sys.stdout)
    template = logging.Formatter(DEFAULT_LOG_FMT)
    console.setFormatter(template)
    verbosity_level = levels.get(int(level), logging.DEBUG)
    logger = logging.getLogger()
    logger.addHandler(console)
    logger.setLevel(verbosity_level)


# pylint: disable=too-few-public-methods
class GracefulShutdown:
    """Shutdown process gracefully"""

    SIGNALS = ("SIGTERM", "SIGINT", "SIGHUP")
    SHUTDOWN = False

    @classmethod
    def register_handler(cls) -> None:
        """Register handler to signals"""
        for name in cls.SIGNALS:
            signal.signal(getattr(signal, name), cls._shutdown_now)

    @classmethod
    # pylint: disable=unused-argument
    def _shutdown_now(cls, signum: int, frame: Optional[FrameType] = None) -> None:
        cls.SHUTDOWN = True


def is_ipv4_addr(ip_addr: str) -> bool:
    """
    Validates the format of an IPv4 address.

    :param str ip_addr: an IPv4 address
    :returns bool: ``True`` if valid IPv4 address`` else ``False``.
    """
    try:
        socket.inet_pton(socket.AF_INET, ip_addr)
    except AttributeError:
        try:
            socket.inet_aton(ip_addr)
        except socket.error:
            return False
    except socket.error:
        return False
    return True


def is_ipv6_addr(ip_addr: str) -> bool:
    """
    Validates the format of an IPv6 address.

    :param str ip_addr: An IPv6 address.
    :returns bool: ``True`` if valid IPv6 address or else ``False``.
    """
    try:
        socket.inet_pton(socket.AF_INET6, ip_addr)
    except socket.error:
        return False
    return True


def extend_datetime_now(weeks: int = 1) -> datetime.datetime:
    """
    Extend the current date in UTC by X number of weeks.

    :params int weeks: Number of weeks
    :returns datetime.datetime: The current datetime object extend by X weeks.
    """
    now = datetime.datetime.utcnow()
    return now + datetime.timedelta(weeks=weeks)
