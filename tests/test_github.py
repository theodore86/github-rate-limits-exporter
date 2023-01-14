from contextlib import nullcontext as does_not_raise

import pytest

from github_rate_limits_exporter.github import AccessToken, GithubApp
from tests.utils import CURRENT_TIME


@pytest.mark.parametrize('private_key, expectation', [
    ('private_key_fd', does_not_raise()),
    ('private_key_str', does_not_raise()),
    ('private_key_str_base64', pytest.raises(ValueError))
])
def test_github_app_private_key(private_key, expectation, request):
    with expectation:
        GithubApp(
            123123,
            request.getfixturevalue(private_key),
            11112222
        )


@pytest.mark.parametrize('app_id, expectation', [
    ('123123', pytest.raises(ValueError)),
    ({}, pytest.raises(ValueError)),
    (123456, does_not_raise())
])
def test_github_app_id(app_id, expectation, request):
    with expectation:
        GithubApp(
            app_id,
            request.getfixturevalue('private_key_str'),
            11112222
        )


@pytest.mark.parametrize('install_id, expectation', [
    ('12341234', pytest.raises(ValueError)),
    ([], pytest.raises(ValueError)),
    (12341234, does_not_raise())
])
def test_github_app_installation_id(install_id, expectation, request):
    with expectation:
        GithubApp(
            111222,
            request.getfixturevalue('private_key_str'),
            install_id
        )


@pytest.mark.parametrize('token, expires_at, expectation', [
    ('value', CURRENT_TIME, does_not_raise()),
    ('another_value', 'date', pytest.raises(ValueError))
])
def test_access_token(token, expires_at, expectation):
    with expectation:
         AccessToken(token, expires_at)


@pytest.mark.parametrize('date, expectation', [
    ('2022-12-25 10:25:38', True),
    ('2022-12-23 12:30:45', False)
])
def test_access_token_has_expired(access_token, freezer, date, expectation):
    freezer.move_to(date)
    assert access_token.has_expired() == expectation
