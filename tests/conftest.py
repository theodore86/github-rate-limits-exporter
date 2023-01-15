import argparse
import base64
import datetime
import json
import os
from unittest.mock import PropertyMock

import dotmap
import pytest
from github.InstallationAuthorization import InstallationAuthorization

from github_rate_limits_exporter import cli, github
from github_rate_limits_exporter.collector import GithubRateLimitsCollector
from github_rate_limits_exporter.github import GithubRateLimitsRequester
from tests.utils import CURRENT_TIME, TOKEN_EXPIRES_AT


@pytest.fixture(scope="module")
def file_path():
    def _file_path(relative):
        return os.path.abspath(os.path.join(os.path.dirname(__file__), relative))

    return _file_path


@pytest.fixture(scope="module")
def private_key_path(file_path):
    return file_path("files/rsa.private")


@pytest.fixture(scope="module")
def private_key_fd(private_key_path):
    fd = open(private_key_path, "r")
    yield fd
    fd.close()


@pytest.fixture(scope="module")
def private_key_str(private_key_path):
    fd = open(private_key_path, "r")
    value = fd.read()
    yield value
    fd.close()


@pytest.fixture(scope="module")
def private_key_str_base64(private_key_str):
    return base64.b64encode(private_key_str.encode())


@pytest.fixture(scope="module")
def rate_limits_json_path(file_path):
    return file_path("files/rate_limits.json")


@pytest.fixture(scope="module")
def rate_limits_json(rate_limits_json_path):
    fd = open(rate_limits_json_path, "r")
    rate_limits = json.loads(fd.read()).get("resources")
    yield rate_limits
    fd.close()


@pytest.fixture(scope="module")
def rate_limits_json_dotmap(rate_limits_json):
    return dotmap.DotMap(rate_limits_json)


@pytest.fixture(scope="module")
def mock_github(rate_limits_json):
    class GithubMock:
        def __init__(self, login_or_token):
            self.token = login_or_token

        def get_rate_limit(self):
            class RateLimits:
                @property
                def raw_data(self):
                    return rate_limits_json

            return RateLimits()

    return GithubMock("some-value")


@pytest.fixture(scope="module")
def mock_github_rate_limits_requester(rate_limits_json):
    class GithubRateLimitsRequesterMock:
        def __init__(self, args):
            self.args = args

        def get_rate_limits(self):
            return dotmap.DotMap(rate_limits_json)

    return GithubRateLimitsRequesterMock


@pytest.fixture
def collector(mocker, private_key_str, mock_github_rate_limits_requester):
    mocker.patch(
        "github_rate_limits_exporter.collector.GithubRateLimitsRequester",
        mock_github_rate_limits_requester,
    )
    return GithubRateLimitsCollector(
        argparse.Namespace(
            github_account="github_account",
            github_app_id=11112222,
            github_app_installation_id=12345678,
            github_app_private_key_path=private_key_str,
        )
    )


@pytest.fixture(scope="session")
def argparser():
    return cli.ArgumentParser()


@pytest.fixture
def github_env_vars(request):
    old_environ = os.environ
    os.environ = request.param
    yield request.param
    os.environ.clear()
    os.environ = old_environ


@pytest.fixture(scope="module")
def access_token():
    return github.GithubToken(
        "some-value", datetime.datetime(2022, 12, 24, 9, 25, 38)
    )


@pytest.fixture
def github_mock(mocker, mock_github):
    return mocker.patch(
        "github_rate_limits_exporter.github.Github", return_value=mock_github
    )


@pytest.fixture
def github_app_access_token_mock(mocker, install_auth):
    mock_token = mocker.patch(
        "github_rate_limits_exporter.github.GithubApp.access_token",
        new_callable=PropertyMock,
    )
    mock_token.side_effect = [install_auth(TOKEN_EXPIRES_AT)]
    return mock_token


@pytest.fixture
def github_app_requester(private_key_str):
    return GithubRateLimitsRequester(
        argparse.Namespace(
            github_auth_type="app",
            github_app_id=123123,
            github_app_private_key_path=private_key_str,
            github_app_installation_id=11112222,
        )
    )


@pytest.fixture
def github_pat_requester(freezer):
    freezer.move_to(CURRENT_TIME)
    return GithubRateLimitsRequester(
        argparse.Namespace(github_auth_type="pat", github_token="some-value")
    )


@pytest.fixture(scope="module")
def install_auth():
    def auth(expires_at):
        return InstallationAuthorization(
            requester=None,
            headers=None,
            attributes={
                "token": "some-value",
                "expires_at": expires_at,
                "on_behalf_of": "exporter",
            },
            completed=True,
        )

    return auth
