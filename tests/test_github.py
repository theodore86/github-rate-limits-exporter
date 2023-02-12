from argparse import Namespace
from contextlib import nullcontext as does_not_raise
from datetime import datetime

import pytest

from github_rate_limits_exporter.github import GithubApp, GithubToken
from tests.utils import (
    CURRENT_TIME,
    MOVE_FORWARD_CURRENT_TIME,
    NEW_TOKEN_EXPIRATION_TIME,
    TOKEN_EXPIRES_AT,
)


@pytest.mark.parametrize(
    "args, expectation",
    [
        (
            Namespace(
                github_app_id=123123,
                github_app_private_key_path="private_key_fd",
                github_app_installation_id=11112222,
            ),
            does_not_raise(),
        ),
        (
            Namespace(
                github_app_id=123123,
                github_app_private_key_path="private_key_str",
                github_app_installation_id=11112222,
            ),
            does_not_raise(),
        ),
        (
            Namespace(
                github_app_id=123123,
                github_app_private_key_path="private_key_str_base64",
                github_app_installation_id=11112222,
            ),
            pytest.raises(ValueError),
        ),
    ],
)
def test_github_app_private_key(args, expectation, request):
    private_key = request.getfixturevalue(args.github_app_private_key_path)
    args.github_app_private_key_path = private_key
    with expectation:
        GithubApp(args)


@pytest.mark.parametrize(
    "args, expectation",
    [
        (
            Namespace(
                github_app_id="123123",
                github_app_private_key_path="private_key_str",
                github_app_installation_id=11112222,
            ),
            pytest.raises(ValueError),
        ),
        (
            Namespace(
                github_app_id={},
                github_app_private_key_path="private_key_str",
                github_app_installation_id=11112222,
            ),
            pytest.raises(ValueError),
        ),
        (
            Namespace(
                github_app_id=123456,
                github_app_private_key_path="private_key_str",
                github_app_installation_id=11112222,
            ),
            does_not_raise(),
        ),
    ],
)
def test_github_app_id(args, expectation, request):
    private_key = request.getfixturevalue(args.github_app_private_key_path)
    args.github_app_private_key_path = private_key
    with expectation:
        GithubApp(args)


@pytest.mark.parametrize(
    "args, expectation",
    [
        (
            Namespace(
                github_app_id=123456,
                github_app_private_key_path="private_key_str",
                github_app_installation_id="12341234",
            ),
            pytest.raises(ValueError),
        ),
        (
            Namespace(
                github_app_id=123456,
                github_app_private_key_path="private_key_str",
                github_app_installation_id=[],
            ),
            pytest.raises(ValueError),
        ),
        (
            Namespace(
                github_app_id=123456,
                github_app_private_key_path="private_key_str",
                github_app_installation_id=12341234,
            ),
            does_not_raise(),
        ),
    ],
)
def test_github_app_installation_id(args, expectation, request):
    private_key = request.getfixturevalue(args.github_app_private_key_path)
    args.github_app_private_key_path = private_key
    with expectation:
        GithubApp(args)


@pytest.mark.parametrize(
    "token, expires_at, expectation",
    [
        ("dfgftgh4FSE#", CURRENT_TIME, does_not_raise()),
        ("token", "date", pytest.raises(ValueError)),
    ],
)
def test_github_token_expires_at(token, expires_at, expectation):
    with expectation:
        GithubToken(token, expires_at)


@pytest.mark.parametrize(
    "token, expires_at, expectation",
    [
        ("#Er%45612", CURRENT_TIME, does_not_raise()),
        (123456, CURRENT_TIME, pytest.raises(ValueError)),
        ([], CURRENT_TIME, pytest.raises(ValueError)),
    ],
)
def test_github_token_value(token, expires_at, expectation):
    with expectation:
        GithubToken(token, expires_at)


@pytest.mark.parametrize(
    "date, expectation",
    [("2022-12-25 10:25:38", True), ("2022-12-23 12:30:45", False)],
)
def test_github_token_has_expired(access_token, freezer, date, expectation):
    freezer.move_to(date)
    assert access_token.has_expired() == expectation


def test_github_rate_limits_requester_app_token_init(
    install_auth, github_app_access_token_mock, github_app_requester
):
    token = install_auth(TOKEN_EXPIRES_AT)
    assert github_app_requester.token == GithubToken(token.token, token.expires_at)
    assert github_app_access_token_mock.call_count == 1


def test_github_rate_limits_requester_pat_token_init(github_pat_requester):
    assert github_pat_requester.token == GithubToken(
        "some-value", datetime(2042, 2, 15, 12, 45)
    )


def test_github_rate_limits_requester(
    freezer,
    github_mock,
    github_app_access_token_mock,
    github_app_requester,
    rate_limits_json_dotmap,
):
    freezer.move_to(CURRENT_TIME)
    assert github_app_requester.get_rate_limits() == rate_limits_json_dotmap
    assert github_mock.call_count == 1
    assert github_app_access_token_mock.call_count == 1


def test_github_rate_limits_request_refresh_token(
    freezer,
    github_mock,
    github_app_access_token_mock,
    github_app_requester,
    rate_limits_json_dotmap,
):
    freezer.move_to(MOVE_FORWARD_CURRENT_TIME)
    assert github_app_requester.get_rate_limits() == rate_limits_json_dotmap
    assert github_app_requester.token == GithubToken("some-value", NEW_TOKEN_EXPIRATION_TIME)
    assert github_mock.call_count == 1
    assert github_app_access_token_mock.call_count == 2
