"""github_rate_limits exporter test fixtures"""

import argparse
import base64
import datetime
import json
import os
import queue
from unittest.mock import Mock, PropertyMock

import dotmap
import pytest
from github.InstallationAuthorization import InstallationAuthorization

from github_rate_limits_exporter import cli, github
from github_rate_limits_exporter.collector import GithubRateLimitsCollector
from github_rate_limits_exporter.github import GithubRateLimitsRequester
from github_rate_limits_exporter.utils import SharedExceptionQueue
from tests.utils import (
    CURRENT_TIME,
    CURRENT_TIMESTAMP,
    NEW_TOKEN_EXPIRES_AT,
    TOKEN_EXPIRES_AT,
)


@pytest.fixture(scope="module")
def file_path():
    """Factory fixture, returns a function object for absolute path calculation"""

    def _file_path(relative):
        return os.path.abspath(os.path.join(os.path.dirname(__file__), relative))

    return _file_path


@pytest.fixture(scope="module")
def private_key_path(file_path):
    """Returns the private key path"""
    return file_path("files/rsa.private")


@pytest.fixture(scope="module")
def private_key_fd(private_key_path):
    """Returns a file-descriptor object of the private key"""
    fd = open(private_key_path, "r")
    yield fd
    fd.close()


@pytest.fixture(scope="module")
def private_key_str(private_key_path):
    """Returns the content of the private key as strinb object"""
    fd = open(private_key_path, "r", encoding="utf-8")
    value = fd.read()
    yield value
    fd.close()


@pytest.fixture(scope="module")
def private_key_str_base64(private_key_str):
    """Returns the private key as string object decoded"""
    return base64.b64encode(private_key_str.encode())


@pytest.fixture(scope="module")
def rate_limits_json_path(file_path):
    """Returns the JSON rate-limits absolute path"""
    return file_path("files/rate_limits.json")


@pytest.fixture(scope="module")
def rate_limits_json(rate_limits_json_path):
    """Returns an object of pre-defined rate-limits in JSON format"""
    fd = open(rate_limits_json_path, "r", encoding="utf-8")
    rate_limits = json.loads(fd.read()).get("resources")
    yield rate_limits
    fd.close()


@pytest.fixture(scope="module")
def rate_limits_json_dotmap(rate_limits_json):
    """Returns a dotmap.Dotmap object of the pre-defined rate-limits"""
    return dotmap.DotMap(rate_limits_json)


@pytest.fixture
def github_rate_limits_requester_mock(mocker, rate_limits_json):
    """Returns a Mock object of the GithubRateLimitsRequester.get_rate_limits attribute"""
    return mocker.patch.object(
        GithubRateLimitsRequester,
        "get_rate_limits",
        return_value=dotmap.DotMap(rate_limits_json),
        autospec=True,
    )


@pytest.fixture
def mock_unix_timestamp(mocker):
    """Return a Mock object of the collector.get_unix_timestamp attribute"""
    return mocker.patch(
        "github_rate_limits_exporter.collector.get_unix_timestamp",
        return_value=CURRENT_TIMESTAMP,
        autospec=True,
    )


@pytest.fixture
def exception_queue():
    """Returns an Queue object"""
    return SharedExceptionQueue(queue.Queue())


@pytest.fixture
def exception_queue_put_error(exception_queue):
    """Returns an Queue object with an pre-defined exception in queue"""
    return exception_queue.put(lambda: exec('raise(ValueError("invalid value"))'))


@pytest.fixture
def collector(private_key_str, exception_queue):
    """Returns a collector instance"""
    return GithubRateLimitsCollector(
        argparse.Namespace(
            github_auth_type="app",
            github_account="github_account",
            github_app_id=11112222,
            github_app_installation_id=12345678,
            github_app_private_key_path=private_key_str,
        ),
        exception_queue,
    )


@pytest.fixture(scope="session")
def argparser():
    """Returns an ArgumentParser instance"""
    return cli.ArgumentParser()


@pytest.fixture
def github_env_vars(request):
    """Fixture sets and unsets ENV variables"""
    old_environ = os.environ
    os.environ = request.param
    yield request.param
    os.environ.clear()
    os.environ = old_environ


@pytest.fixture(scope="module")
def access_token():
    """Returns a GithubToken instance"""
    return github.GithubToken(
        "token-value",
        datetime.datetime(2022, 12, 24, 9, 25, 38, tzinfo=datetime.timezone.utc),
    )


@pytest.fixture
def github_mock(mocker, rate_limits_json):
    """Returns a Mock object of the Github.get_rate_limit attribute"""
    return mocker.patch(
        "github_rate_limits_exporter.github.Github.get_rate_limit",
        return_value=Mock(raw_data=rate_limits_json),
        autospec=True,
    )


@pytest.fixture
def github_app_access_token_mock(mocker, install_auth):
    """Returns a Mock object of the Githubapp.access_token attribute"""
    mock_token = mocker.patch(
        "github_rate_limits_exporter.github.GithubApp.access_token",
        new_callable=PropertyMock,
    )
    mock_token.side_effect = [
        install_auth(TOKEN_EXPIRES_AT),
        install_auth(NEW_TOKEN_EXPIRES_AT),
    ]
    return mock_token


@pytest.fixture
def github_app_requester(private_key_str):
    """Returns an APP GithubRateLimitsRequester instance"""
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
    """Returns a PAT GithubRateLimitsRequester instance"""
    freezer.move_to(CURRENT_TIME)
    return GithubRateLimitsRequester(
        argparse.Namespace(github_auth_type="pat", github_token="some-value")
    )


@pytest.fixture(scope="module")
def install_auth():
    """Factory fixture, returns an function object to create GithubApp installations"""

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
