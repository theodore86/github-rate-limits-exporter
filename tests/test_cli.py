import argparse
from contextlib import nullcontext as does_not_raise

import pytest

from github_rate_limits_exporter import cli, exceptions


@pytest.mark.parametrize(
    "addr, expectation",
    [
        ("test", pytest.raises(argparse.ArgumentTypeError)),
        (
            "1200:0000:AB00:1234:O000:2552:7777:1313",
            pytest.raises(argparse.ArgumentTypeError),
        ),
        ("::1.1.1", pytest.raises(argparse.ArgumentTypeError)),
    ],
)
def test_ip_address_argument_error(addr, expectation):
    with expectation:
        cli.ip_address(addr)


@pytest.mark.parametrize(
    "port, expectation",
    [
        ("80", pytest.raises(argparse.ArgumentTypeError)),
        (80, pytest.raises(argparse.ArgumentTypeError)),
        ("1023", pytest.raises(argparse.ArgumentTypeError)),
        ("port", pytest.raises(argparse.ArgumentTypeError)),
        ([], pytest.raises(argparse.ArgumentTypeError)),
    ],
)
def test_listen_port_argument_error(port, expectation):
    with expectation:
        cli.listen_port(port)


def test_argparser_error_msg(argparser):
    with pytest.raises(exceptions.ArgumentError, match="^__main__.py: error message"):
        assert argparser.error("error message")


@pytest.mark.parametrize(
    "namespace, expectation",
    [
        (
            argparse.Namespace(
                github_auth_type="app",
                github_app_id=None,
                github_installation_id=123,
                github_app_private_key_path="/path",
            ),
            pytest.raises(exceptions.ArgumentError),
        ),
        (
            argparse.Namespace(
                github_auth_type="app",
                github_app_id=4455,
                github_app_installation_id=None,
                github_app_private_key_path="/path",
            ),
            pytest.raises(exceptions.ArgumentError),
        ),
        (
            argparse.Namespace(
                github_auth_type="app",
                github_app_id=123,
                github_app_installation_id=123,
                github_app_private_key_path=None,
            ),
            pytest.raises(exceptions.ArgumentError),
        ),
        (
            argparse.Namespace(github_auth_type="pat", github_token=None),
            pytest.raises(exceptions.ArgumentError),
        ),
        (
            argparse.Namespace(github_auth_type="unknown"),
            pytest.raises(exceptions.ArgumentError),
        ),
        (
            argparse.Namespace(github_auth_type="pat", github_token="token"),
            does_not_raise(),
        ),
        (
            argparse.Namespace(
                github_auth_type="app",
                github_app_id=123,
                github_app_installation_id=123,
                github_app_private_key_path="/path",
            ),
            does_not_raise(),
        ),
    ],
)
def test_mutual_inclusive_args(namespace, argparser, expectation):
    with expectation:
        cli._check_mutual_inclusive_arguments(namespace, argparser)


@pytest.mark.parametrize(
    "github_env_vars",
    [
        {
            "GITHUB_AUTH_TYPE": "pat",
            "GITHUB_TOKEN": "token",
            "GITHUB_ACCOUNT": "test",
            "EXPORTER_LOG_LEVEL": "4",
            "EXPORTER_BIND_ADDRESS": "10.0.0.1",
            "EXPORTER_LISTEN_PORT": "11000",
        }
    ],
    indirect=True,
)
def test_github_pat_auth_env_variables(github_env_vars):
    args = cli.parsecli(["--github-auth-type", "pat", "--github-account", "test"])
    assert args.github_account == github_env_vars["GITHUB_ACCOUNT"]
    assert args.github_auth_type == github_env_vars["GITHUB_AUTH_TYPE"]
    assert args.github_token == github_env_vars["GITHUB_TOKEN"]
    assert args.verbosity == github_env_vars["EXPORTER_LOG_LEVEL"]
    assert args.bind_addr == github_env_vars["EXPORTER_BIND_ADDRESS"]
    assert args.listen_port == int(github_env_vars["EXPORTER_LISTEN_PORT"])
