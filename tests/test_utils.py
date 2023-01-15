import datetime
import logging

import pytest

from github_rate_limits_exporter import utils


@pytest.mark.parametrize('ipv4_addr, expected', [
    ('1.1.1.1', True), ('1.1.1.111', True), ('127.0.0.1', True),
    ('::1.1.1', False), ('100.1000.100.1', False), ('a.1.1.2', False), ('0.0.0.1', True)])
def test_is_ipv4_address(ipv4_addr, expected):
    assert utils.is_ipv4_addr(ipv4_addr) == expected


@pytest.mark.parametrize('ipv6_addr, expected', [
    ('FE80:0000:0000:0000:0202:B3FF:FE1E:8329', True), ('FE80::0202:B3FF:FE1E:8329', True),
    ('2001:db8:0:1', False), ('::1', True), ('1200::AB00:1234::2552:7777:1313', False),
    ('FE80:FE1E:8329', False), ('1200:0000:AB00:1234:O000:2552:7777:1313', False)])
def test_is_ipv6_address(ipv6_addr, expected):
    assert utils.is_ipv6_addr(ipv6_addr) == expected


@pytest.mark.parametrize('string, expected', [
    ('teststring', False),
    ('dGVzdHN0cmluZwo=', True),
    ('3591916071403198536', False)
])
def test_is_string_base64_encoded(string, expected):
    assert utils.is_string_base64_encoded(string) == expected


@pytest.mark.parametrize('string, expected', [
    ('teststring', 'teststring'),
    ('dGVzdHN0cmluZwo=', 'teststring\n')
])
def test_base64_decode(string, expected):
    assert utils.base64_decode(string) == expected


@pytest.fixture
def logger(request):
    return logging.getLogger(request.param)


@pytest.mark.parametrize('msg, level, logger', [
    ('test msg', ('error', 1), 'exporter'),
    ('another msg', ('debug', 4), 'debugger'),
    ('out_of_verbosity_level', ('debug', 6), 'debug_more')
], indirect=['logger'])
def test_get_logger(logger, caplog, msg, level):
    utils.initialize_logger(level[1])
    getattr(logger, level[0])(msg)
    number = getattr(logging, level[0].upper())
    assert caplog.record_tuples == [(logger.name, number, msg)]


def test_extended_datetime_now(freezer):
    freezer.move_to('2023-01-15')
    expected = datetime.datetime(2023, 1, 22)
    assert utils.extend_datetime_now(weeks=1) == expected
