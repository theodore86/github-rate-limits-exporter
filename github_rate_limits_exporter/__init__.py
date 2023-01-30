"""
    github_rate_limits_exporter
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Prometheus Github REST API Rate Limits exporter.
    Supports the following Github authentication methods:

        - PAT (Personal Access Token) requires:
          - GITHUB_TOKEN
        - APP (as a Github Application) requires:
          - GITHUB_APP_ID
          - GITHUB_INSTALLATION_ID
          - GITHUB_PRIVATE_KEY_PATH
"""

import logging
import queue
from typing import List, Optional

from prometheus_client import REGISTRY, start_http_server

from github_rate_limits_exporter.cli import parsecli
from github_rate_limits_exporter.collector import GithubRateLimitsCollector
from github_rate_limits_exporter.exceptions import ERROR_STATUS_ON_EXCEPTIONS
from github_rate_limits_exporter.utils import (
    GracefulShutdown,
    SharedExceptionQueue,
    initialize_logger,
)

logger = logging.getLogger(__name__)


def main(argv: Optional[List[str]] = None) -> int:
    """Prometheus exporter Main Entrypoint"""
    try:
        args = parsecli(argv=argv, description=__doc__)
        initialize_logger(args.verbosity)
        logger.info('Register collector for "%s" Github account', args.github_account)
        exception_queue = SharedExceptionQueue(queue.Queue())
        collector = GithubRateLimitsCollector(args, exception_queue)
        REGISTRY.register(collector)
        logger.info(
            "HTTP metrics server started on [%s:%d]", args.bind_addr, args.listen_port
        )
        start_http_server(args.listen_port, addr=args.bind_addr)
        GracefulShutdown.register_handler()
        while not GracefulShutdown.SHUTDOWN:
            exception_queue.get_error(timeout=1)
    except ERROR_STATUS_ON_EXCEPTIONS as err:
        logger.error(err, exc_info=True)
        return 1
    return 0
