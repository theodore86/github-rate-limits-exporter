"""
    github_rate_limits_exporter.github
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Github authentication as a Github APP, alternative to Personal Access Token.

    Requires:

        - Application ID.
        - Private key (PEM format).
        - Installation ID.
"""

import io
import logging
from dataclasses import InitVar, dataclass, field
from typing import TextIO, Union

from github import GithubIntegration

from github_rate_limits_exporter.utils import base64_decode

logger = logging.getLogger(__name__)


@dataclass
class GithubApp:
    """
    Represents an Github Application.

    :param int integration_id: Github App identifier (JWT issuer).
    :param str private_key: Github App private key (will be used to sign the JWT token).
    :param int installation_id: Github App installation identifier.
    :raises ValueError: Github App arguments of invalid type.
    """

    _integration_id: InitVar[int]
    _private_key: InitVar[str]
    _installation_id: InitVar[int]
    app: GithubIntegration = field(init=False)

    def __post_init__(
        self, _integration_id: int, _private_key: str, _installation_id: int
    ) -> None:
        self.integration_id = _integration_id
        self.private_key = _private_key
        self.installation_id = _installation_id
        self._app = GithubIntegration(self.integration_id, self.private_key)

    @property
    def integration_id(self) -> int:
        """Github App Integration Identifier (App ID)"""
        return self._integration_id  # type: ignore[attr-defined]

    @integration_id.setter
    def integration_id(self, value: int) -> None:
        if not isinstance(value, int):
            raise ValueError(f"Github App integration id must be a int type: {value!r}")
        self._integration_id = value  # type: ignore[attr-defined]

    @property
    def installation_id(self) -> int:
        """Github App Installation Identifier"""
        return self._installation_id  # type: ignore[attr-defined]

    @installation_id.setter
    def installation_id(self, value: int) -> None:
        if not isinstance(value, int):
            raise ValueError(
                f"Github App installation id must be a int type: {value!r}"
            )
        self._installation_id = value  # type: ignore[attr-defined]

    @property
    def private_key(self) -> str:
        """Github App private key"""
        return self._private_key  # type: ignore[attr-defined]

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
        logger.debug("Private key: %s", value)
        self._private_key = value  # type: ignore[attr-defined]

    @property
    def access_token(self) -> str:
        """Github App (global) access token"""
        return self._app.get_access_token(self.installation_id).token
