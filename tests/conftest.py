import os
import base64
import json
import pytest
from github_rate_limits_exporter import cli
from github_rate_limits_exporter.collector import GithubRateLimitsCollector


@pytest.fixture(scope='module')
def file_path():
    def _file_path(relative):
        return os.path.abspath(
            os.path.join(
                os.path.dirname(__file__),
                relative
            )
        )
    return _file_path


@pytest.fixture(scope='module')
def private_key_path(file_path):
    return file_path('files/rsa.private')


@pytest.fixture(scope='module')
def private_key_fd(private_key_path):
    fd = open(private_key_path, 'r')
    yield fd
    fd.close()


@pytest.fixture(scope='module')
def private_key_str(private_key_path):
    fd = open(private_key_path, 'r')
    value = fd.read()
    yield value
    fd.close()


@pytest.fixture(scope='module')
def private_key_str_base64(private_key_str):
    return base64.b64encode(private_key_str.encode())


@pytest.fixture(scope='module')
def rate_limits_json_path(file_path):
    return file_path('files/rate_limits.json')


@pytest.fixture(scope='module')
def rate_limits_json(rate_limits_json_path):
    fd = open(rate_limits_json_path, 'r')
    rate_limits = json.loads(fd.read()).get('resources')
    yield rate_limits
    fd.close()


@pytest.fixture(scope='module')
def mock_rate_limits(rate_limits_json):
    class RateLimit:
        @property
        def raw_data(self):
            return rate_limits_json
    return RateLimit()


@pytest.fixture(scope='session')
def collector():
    return GithubRateLimitsCollector(
        'github_account', 'github_token'
    )


@pytest.fixture(scope='session')
def argparser():
    return cli.ArgumentParser()


@pytest.fixture
def github_env_vars(request):
    old_environ = os.environ
    os.environ =request.param
    yield request.param
    os.environ.clear()
    os.environ = old_environ
