import datetime
import logging
import os

import pytest

from github_rate_limits_exporter.utils import (
    base64_decode,
    extend_datetime_now,
    initialize_logger,
    is_ipv4_addr,
    is_ipv6_addr,
    is_string_base64_encoded,
)
from tests.utils import LogLevel


@pytest.mark.parametrize(
    "ipv4_addr, expected",
    [
        ("1.1.1.1", True),
        ("1.1.1.111", True),
        ("127.0.0.1", True),
        ("::1.1.1", False),
        ("100.1000.100.1", False),
        ("a.1.1.2", False),
        ("0.0.0.1", True),
    ],
)
def test_is_ipv4_address(ipv4_addr, expected):
    assert is_ipv4_addr(ipv4_addr) == expected


@pytest.mark.parametrize(
    "ipv6_addr, expected",
    [
        ("FE80:0000:0000:0000:0202:B3FF:FE1E:8329", True),
        ("FE80::0202:B3FF:FE1E:8329", True),
        ("2001:db8:0:1", False),
        ("::1", True),
        ("1200::AB00:1234::2552:7777:1313", False),
        ("FE80:FE1E:8329", False),
        ("1200:0000:AB00:1234:O000:2552:7777:1313", False),
    ],
)
def test_is_ipv6_address(ipv6_addr, expected):
    assert is_ipv6_addr(ipv6_addr) == expected


@pytest.mark.parametrize(
    "string, expected",
    [
        ("teststring", False),
        ("dGVzdHN0cmluZwo=", True),
        ("3591916071403198536", False),
        (f"RU5E{os.linesep}IFJTQSBQUklWQVRFIEtFWS0tLS0tCg=={os.linesep}", True),
    ],
)
def test_is_string_base64_encoded(string, expected):
    assert is_string_base64_encoded(string) == expected


@pytest.mark.parametrize(
    "string, expected",
    [("teststring", "teststring"), ("dGVzdHN0cmluZwo=", f"teststring{os.linesep}")],
)
def test_base64_decode(string, expected):
    assert base64_decode(string) == expected


@pytest.fixture
def logger(request):
    return logging.getLogger(request.param)


@pytest.mark.parametrize(
    "msg, level, logger",
    [
        ("test msg", LogLevel("error", 1), "exporter"),
        ("test critical", LogLevel("critical", 0), "emergency"),
        ("another msg", LogLevel("debug", 4), "debugger"),
        ("another warning", LogLevel("warning", 2), "warnings"),
        ("info msg", LogLevel("info", 3), "gives info"),
        ("out_of_verbosity_level", LogLevel("debug", 6), "debug_more"),
    ],
    indirect=["logger"],
)
def test_get_logger(logger, caplog, msg, level):
    initialize_logger(level.value)
    getattr(logger, level.name)(msg)
    number = getattr(logging, level.name.upper())
    assert caplog.record_tuples == [(logger.name, number, msg)]


def test_extended_datetime_now(freezer):
    freezer.move_to("2023-01-15")
    expected = datetime.datetime(2023, 1, 22, tzinfo=datetime.timezone.utc)
    assert extend_datetime_now(weeks=1) == expected


def test_shared_exception_queue_put(exception_queue, exception_queue_put_error):
    value = exception_queue_put_error()
    assert value is None
    assert str(exception_queue.get(block=False)) == "invalid value"


def test_shared_exception_queue_get_error(exception_queue, exception_queue_put_error):
    exception_queue_put_error()
    with pytest.raises(ValueError):
        exception_queue.get_error()
