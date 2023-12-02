"""
    github_rate_limits_exporter.github
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Github authentication using:

      - GithubApp (Installation Access Token)
      - Personal Access Token (PAT)

    To aquire access token from GithubApp:

        - Application ID.
        - Private key (PEM format).
        - Installation ID.

    - PAT access token lifetime is defined by the user.
    - IAT access token (GithubApp) lifetime is at 1 hour.
"""

import argparse
import datetime
import io
import logging
from dataclasses import InitVar, dataclass, field
from typing import TextIO, Union

import dotmap
from github import Github, GithubIntegration
from github.InstallationAuthorization import InstallationAuthorization

from github_rate_limits_exporter.utils import base64_decode, extend_datetime_now

logger = logging.getLogger(__name__)


@dataclass
class GithubApp:
    """
    Represents an Github Application.

    :param argparse.Namespace: Namespace object to store the initial app attributes.

      - installation_id (str): Github App identifier (JWT issuer).
      - private_key (str): Github App private key (will be used to sign the JWT token).
      - installation_id (int): Github App installation identifier.

    :raises ValueError: Github App arguments of invalid type.
    """

    args: InitVar[argparse.Namespace]
    _app: GithubIntegration = field(init=False)

    def __post_init__(self, args: argparse.Namespace) -> None:
        self.app_id = args.github_app_id
        self.private_key = args.github_app_private_key_path
        self.installation_id = args.github_app_installation_id
        self._app = GithubIntegration(self.app_id, self.private_key)

    @property
    def app_id(self) -> int:
        """Github App Integration Identifier (App ID)"""
        return self._app_id

    @app_id.setter
    def app_id(self, value: int) -> None:
        if not isinstance(value, int):
            raise ValueError(f"Github App id must be a int type: {value!r}")
        self._app_id = value

    @property
    def installation_id(self) -> int:
        """Github App Installation Identifier"""
        return self._installation_id

    @installation_id.setter
    def installation_id(self, value: int) -> None:
        if not isinstance(value, int):
            raise ValueError(
                f"Github App installation id must be a int type: {value!r}"
            )
        self._installation_id = value

    @property
    def private_key(self) -> str:
        """Github App private key"""
        return self._private_key

    @private_key.setter
    def private_key(self, value: Union[TextIO, str]) -> None:
        if isinstance(value, io.TextIOBase):
            filed = value
            try:
                value = filed.read()
            finally:
                filed.close()
        if not isinstance(value, str):
            raise ValueError(f"Github App private key must be a string type: {value!r}")
        value = base64_decode(value)
        self._private_key = value

    @property
    def access_token(self) -> InstallationAuthorization:
        """Github App (global)) access token"""
        return self._app.get_access_token(self.installation_id)


@dataclass
class GithubToken:
    """
    Represents an Github (Access) Token.

    :param str token: The Github token as string object type.
    :param datetime expires_at: Token expiration (UTC) datetime object type.
    :raises ValueError:
      - If the token is not a string object type.
      - If the token expiration is not a datetime object type.
    """

    _init_token: InitVar[str]
    _init_expires_at: InitVar[datetime.datetime]
    _token: str = field(init=False)
    _expires_at: datetime.datetime = field(init=False)

    def __post_init__(
        self, _init_token: str, _init_expires_at: datetime.datetime
    ) -> None:
        self.token = _init_token
        self.expires_at = _init_expires_at

    def __str__(self) -> str:
        return f"expires_at: {self._expires_at}"

    @property
    def token(self) -> str:
        """Github Token"""
        return self._token

    @token.setter
    def token(self, value: str) -> None:
        if not isinstance(value, str):
            raise ValueError(f"Github token must be a string type: {value!r}")
        self._token = value

    @property
    def expires_at(self) -> datetime.datetime:
        """Token expiration time in UTC"""
        return self._expires_at

    @expires_at.setter
    def expires_at(self, value: datetime.datetime) -> None:
        if not isinstance(value, datetime.datetime):
            raise ValueError(
                f"Token expiration date must be a datetime type: {value!r}"
            )
        if value.tzinfo is None:
            raise ValueError("Token expiration date must be timezone aware")
        self._expires_at = value

    def has_expired(self, seconds: int = 300) -> bool:
        """
        Validates the token expiration time.
        :seconds int: Seconds to extended the current time.
        :returns bool: ``True`` or ``False`` if token has expired compared to the current time.
        """
        now = datetime.datetime.now(datetime.timezone.utc)
        now = now + datetime.timedelta(seconds=seconds)
        logger.debug("Github Token expires at: %s", self.expires_at)
        return self.expires_at < now


class GithubRateLimitsRequester:
    """
    Represents a requester to ``GET`` the Github API rate-limits.

    :param argparse.Namespace: Argparse object to store the initial requester attributes.
        Namespace attributes are populated by the command-line interface.

      - token (GithubToken): The Github Access Token (PAT or APP).
      - api (Github API): The Github API to ``GET`` the rate-limit data from.
    """

    def __init__(self, args: argparse.Namespace) -> None:
        self.token = self._initialize_token(args)
        self._api = Github(login_or_token=self.token.token)

    def _initialize_token(self, args: argparse.Namespace) -> GithubToken:
        logger.debug("Github authentication type: %s", args.github_auth_type)
        if args.github_auth_type == "pat":
            return GithubToken(args.github_token, extend_datetime_now(weeks=999))
        self._app = GithubApp(args)
        token = self._app.access_token
        return GithubToken(token.token, token.expires_at)

    def get_rate_limits(self) -> dotmap.DotMap:
        """Retrieve the Github API rate-limits"""
        if self.token.has_expired():
            logger.debug("Github Token expired at: %s", self.token.expires_at)
            self._refresh_token()
        rate_limits = self._api.get_rate_limit()
        return dotmap.DotMap(rate_limits.raw_data)

    def _refresh_token(self) -> None:
        logger.debug("Requesting new Github Token")
        token = self._app.access_token
        self.token = GithubToken(token.token, token.expires_at)
        self._api = Github(login_or_token=token.token)
