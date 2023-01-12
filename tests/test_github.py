from datetime import datetime
import iso8601
import pytest
from contextlib import nullcontext as does_not_raise
from github_rate_limits_exporter.github import GithubApp, AccessToken
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
