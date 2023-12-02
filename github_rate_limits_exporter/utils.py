"""
    github_rate_limits_exporter.utils
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Prometheus exporter utilities/helper functions.
"""

import base64
import binascii
import datetime
import logging
import os
import queue
import signal
import socket
import sys
from types import FrameType
from typing import Any, Callable, Optional

from github_rate_limits_exporter.constants import DEFAULT_LOG_FMT, LOGGING_LEVELS


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
        return base64.b64encode(base64.b64decode(string)).decode() == string.replace(
            os.linesep, ""
        )
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


def initialize_logger(level: int, fmt: Optional[str] = DEFAULT_LOG_FMT) -> None:
    """
    Initialize and setup the level of effectiveness.

    :param int level: Verbosity level (0...4)
    :param str fmt: Custom formatter.
    :returns: Nothing.
    """
    console = logging.StreamHandler(sys.stdout)
    template = logging.Formatter(fmt)
    console.setFormatter(template)
    verbosity_level = LOGGING_LEVELS.get(int(level), logging.DEBUG)
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
    now = datetime.datetime.now(datetime.timezone.utc)
    return now + datetime.timedelta(weeks=weeks)


class SharedExceptionQueue:
    """Queue for transfering exceptions between threads"""

    def __init__(self, equeue: queue.Queue) -> None:
        self.equeue = equeue

    def put(self, func: Callable[..., Any]) -> Callable[..., Any]:
        """Put error (exception) of any callable into the queue"""

        def wrapper(*args: Any, **kwargs: Any) -> Any:
            try:
                return func(*args, **kwargs)
            except Exception as error:  # pylint: disable=broad-except
                self.equeue.put(error, block=False)
            return None

        return wrapper

    def get(self, *args: Any, **kwargs: Any) -> Exception:
        """Remove error (exception) from the queue"""
        return self.equeue.get(*args, **kwargs)

    def get_error(self, *args: Any, **kwargs: Any) -> None:
        """Remove and raise error (exception) (if available) from the queue."""
        try:
            exc = self.get(*args, **kwargs)
            raise exc
        except queue.Empty:
            pass
