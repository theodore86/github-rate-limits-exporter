"""
    github_rate_limits_exporter.collector
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Prometheus exporter or custom collector,
    collects the github rate-limits per API.

    The collector is registered with the prometheus client
    when the exporter starts up.
"""

import argparse
import logging
from typing import Dict, Iterable, Optional

import dotmap
from prometheus_client import Metric
from prometheus_client.core import GaugeMetricFamily
from prometheus_client.registry import Collector

from github_rate_limits_exporter.constants import DEFAULT_RATE_LIMITS
from github_rate_limits_exporter.github import GithubRateLimitsRequester
from github_rate_limits_exporter.utils import SharedExceptionQueue, get_unix_timestamp

logger = logging.getLogger(__name__)


class GithubRateLimitsCollector(Collector):
    """
    Prometheus GitHub Rate Limits collector.

    :param argparse.Namespace: Argparse object to store the initial collector attributes.
        Namespace attributes are populated by the command-line interface.

      - account (str): The Github account name.
      - requester (GithubRateLimitsRequester): Github API Rate-Limits requester.
      - exception_queue: Queue with exception objects.

    :raises ValueError: Any of the attributes is not an string type.
    """

    def __init__(
        self, args: argparse.Namespace, exception_queue: SharedExceptionQueue
    ) -> None:
        self.account = args.github_account
        self._requester = GithubRateLimitsRequester(args)
        self._exception_queue = exception_queue

    @property
    def account(self) -> str:
        """The Github Account"""
        return self._account

    @account.setter
    def account(self, value: str) -> None:
        if not isinstance(value, str):
            raise ValueError(f"Github account must be a string type: {value!r}")
        self._account = value

    def _get_rate_limits(self) -> Dict[str, str]:
        return self._requester.get_rate_limits()

    def collect(self) -> Iterable[Metric]:
        """
        Returns the requested Github (per API) rate-limit metrics.

        :return list: List of metrics.
        """
        metrics = []
        logger.info("Collected metrics for %s account", self._account)
        decorated = self._exception_queue.put(self._requester.get_rate_limits)
        limits = decorated()
        metrics.extend(
            [
                self._add_metric(resources=limits),
                self._add_metric(api_name="search", resources=limits),
                self._add_metric(api_name="graphql", resources=limits),
                self._add_metric(api_name="integration_manifest", resources=limits),
                self._add_metric(api_name="code_scanning_upload", resources=limits),
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
