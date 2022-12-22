"""
    github_rate_limits_exporter.collector
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Prometheus exporter or custom collector,
    collects the github rate-limits per API.

    The collector is registered with the prometheus client
    when the exporter starts up.
"""

import logging
from typing import Iterable, Optional

import dotmap
import github
from prometheus_client import Metric
from prometheus_client.core import GaugeMetricFamily
from prometheus_client.registry import Collector

from github_rate_limits_exporter.constants import DEFAULT_RATE_LIMITS
from github_rate_limits_exporter.utils import get_unix_timestamp

logger = logging.getLogger(__name__)


class GithubRateLimitsCollector(Collector):
    """
    Prometheus GitHub Rate Limits collector.

    :param str account: Github account name.
    :param str token: Github APP (installation) or personal token (PAT).
    :raises ValueError: Any of the attributes is not an string type.
    """

    def __init__(self, account: str, token: str) -> None:
        self.account = account
        self.token = token
        self._api = github.Github(login_or_token=self._token)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self._account!r}, {self._token!r})"

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
    def account(self) -> str:
        """Github Account"""
        return self._account

    @account.setter
    def account(self, value: str) -> None:
        if not isinstance(value, str):
            raise ValueError(f"Github account must be a string type: {value!r}")
        self._account = value

    @property
    def rate_limits(self) -> dotmap.DotMap:
        """Github API rate-limits"""
        rate_limits = self._api.get_rate_limit()
        return dotmap.DotMap(rate_limits.raw_data)

    def collect(self) -> Iterable[Metric]:
        """
        Returns the requested Github (per API) rate-limit metrics.

        :return list: List of metrics.
        """
        metrics = []
        logger.debug("Collected metrics for %s account", self._account)
        rate_limits = self.rate_limits
        metrics.extend(
            [
                self._add_metric(resources=rate_limits),
                self._add_metric(api_name="search", resources=rate_limits),
                self._add_metric(api_name="graphql", resources=rate_limits),
                self._add_metric(
                    api_name="integration_manifest", resources=rate_limits
                ),
                self._add_metric(
                    api_name="code_scanning_upload", resources=rate_limits
                ),
            ]
        )
        logger.debug("%s", metrics)
        return metrics

    def _add_metric(
        self, api_name: str = "core", resources: Optional[dotmap.DotMap] = None
    ) -> Metric:
        if resources is None:
            resources = dotmap.DotMap(api_name=DEFAULT_RATE_LIMITS)
        if not isinstance(resources, dotmap.DotMap):
            raise ValueError(
                f"Github resources must be type of: {dotmap.DotMap.__name__}"
            )
        api_name = str(api_name).lower()
        limits = resources.get(api_name, DEFAULT_RATE_LIMITS)
        gauge = GaugeMetricFamily(
            f"github_rate_limits_{api_name}",
            f"API requests in {api_name} per hour",
            labels=["account", "type"],
        )
        gauge.add_metric(
            [self._account, "limit"], float(limits.limit), get_unix_timestamp()
        )
        gauge.add_metric(
            [self._account, "used"], float(limits.used), get_unix_timestamp()
        )
        gauge.add_metric(
            [self._account, "remaining"], float(limits.remaining), get_unix_timestamp()
        )
        gauge.add_metric(
            [self._account, "reset"], float(limits.reset), get_unix_timestamp()
        )
        return gauge
