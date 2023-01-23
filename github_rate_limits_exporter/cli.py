"""
    github_rate_limits_exporter.cli
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Prometheus exporter command line interface.
""" ""

import argparse
import os
from typing import List, NoReturn, Optional, Union

from github_rate_limits_exporter._version import __version__
from github_rate_limits_exporter.exceptions import ArgumentError
from github_rate_limits_exporter.utils import is_ipv4_addr, is_ipv6_addr


def parsecli(
    argv: Optional[List[str]] = None, description: Optional[str] = None
) -> argparse.Namespace:
    """
    Parser for the prometheus exporter arguments.

    :param list argv: List of command line arguments.
    :param str description: Description of the command line interface.
    :returns argparse.Namespace: Object which holds the command line arguments.
    """
    parser = ArgumentParser(
        description=description, formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument(
        "--github-auth-type",
        dest="github_auth_type",
        choices=["pat", "app"],
        default=os.getenv("GITHUB_AUTH_TYPE"),
        required=not os.getenv("GITHUB_AUTH_TYPE"),
        help="github token authentication type",
    )
    parser.add_argument(
        "--github-account",
        dest="github_account",
        default=os.getenv("GITHUB_ACCOUNT"),
        required=not os.getenv("GITHUB_ACCOUNT"),
        help="github account name",
    )
    parser.add_argument(
        "--github-token",
        dest="github_token",
        nargs="?",
        default=os.getenv("GITHUB_TOKEN"),
        help="github personal access token (PAT)",
    )
    parser.add_argument(
        "--github-app-id",
        dest="github_app_id",
        nargs="?",
        default=os.getenv("GITHUB_APP_ID"),
        type=int,
        help="github application (integration) identifier",
    )
    parser.add_argument(
        "--github-app-installation-id",
        dest="github_app_installation_id",
        nargs="?",
        default=os.getenv("GITHUB_APP_INSTALLATION_ID"),
        type=int,
        help="github installation ID for App/Org Pair",
    )
    parser.add_argument(
        "--github-app-private-key-path",
        dest="github_app_private_key_path",
        nargs="?",
        default=os.getenv("GITHUB_APP_PRIVATE_KEY_PATH"),
        type=argparse.FileType("r"),
        help="github App private key path (optionally base64 encoded)",
    )
    parser.add_argument(
        "--bind-address",
        dest="bind_addr",
        default=os.getenv("EXPORTER_BIND_ADDRESS", default="0.0.0.0"),
        type=ip_address,
        help="exporter HTTP bind address, (default: %(default)s)",
    )
    parser.add_argument(
        "--listen-port",
        dest="listen_port",
        default=os.getenv("EXPORTER_LISTEN_PORT") or 10050,
        type=listen_port,
        help="exporter HTTP listen port, (default: %(default)s)",
    )
    parser.add_argument(
        "--version", "-V", action="version", version=f"%(prog)s: {__version__}"
    )
    parser.add_argument(
        "-v",
        dest="verbosity",
        default=os.getenv("EXPORTER_LOG_LEVEL") or 0,
        action="count",
        help="logging verbosity (up to 5 times),default: CRITICAL",
    )
    args, __ = parser.parse_known_args(args=argv)
    _check_mutual_inclusive_arguments(args, parser)
    return args


def _check_mutual_inclusive_arguments(
    args: argparse.Namespace, parser: argparse.ArgumentParser
) -> None:
    if args.github_auth_type == "pat":
        if args.github_token is None:
            parser.error("Github PAT authentication type requires: --github-token")
    elif args.github_auth_type == "app":
        if (
            args.github_app_id is None
            or args.github_app_installation_id is None
            or args.github_app_private_key_path is None
        ):
            parser.error(
                "Github App authentication type requires:"
                " --github-app-id,"
                " --github-app-installation-id,"
                " --github-app-private-key-path"
            )
    else:
        parser.error(f'invalid Github authentication type: "{args.github_auth_type}"')


class ArgumentParser(argparse.ArgumentParser):
    """
    Overrides the argparse ``stderr`` to handle any errors
    from creating or using an argument.
    """

    def _error_message(self, message: str) -> str:
        return os.linesep.join([message or "", self.format_usage()])

    def error(self, message: str) -> NoReturn:
        """
        Default argument parser errors.

        :param str message: The error message to display.
        :raises ArgumentError: When there are errors with the parser's actions.
        """
        _message = self._error_message(message)
        raise ArgumentError(f"{self.prog}: {_message}")


def ip_address(ip_addr: str) -> str:
    """
    Validates if the IP address is IPv4 or IPv6.

    :param str ip_addr: IPv4 or IPv6 address.
    :raises ArgumentTypeError:If IP address is invalid.
    """
    if not (is_ipv4_addr(ip_addr) or is_ipv6_addr(ip_addr)):
        raise argparse.ArgumentTypeError(
            f"{ip_addr!r} is not valid IPv4 or IPv6 address"
        )
    return ip_addr


def listen_port(port: Union[int, str]) -> int:
    """
    Validates that the server listening port is non-negative
    and greater than 1024 (non-privileged)

    :param int_or_str port: Server listening port number.
    :raises ArgumentTypeError: If server port is less than 1024 or negative.
    """
    try:
        port = int(port)
    except (ValueError, TypeError) as err:
        raise argparse.ArgumentTypeError(
            f"server listening port must be integer not: {port!r}"
        ) from err

    if port < 1024:
        raise argparse.ArgumentTypeError(
            f"server listening port must be greater than 1024, not: {port}"
        )
    return port
