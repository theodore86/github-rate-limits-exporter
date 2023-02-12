from contextlib import nullcontext as does_not_raise

import dotmap
import pytest
from prometheus_client.core import GaugeMetricFamily

from tests.utils import CURRENT_TIMESTAMP


def test_add_metrics(
    github_app_access_token_mock,
    collector,
    rate_limits_json,
    mock_unix_timestamp,
):
    mock_resources = dotmap.DotMap(rate_limits_json)
    expected_metric = GaugeMetricFamily(
        "github_rate_limits_search",
        "API requests in search per hour",
        labels=["account", "type"],
    )
    expected_metric.add_metric(["github_account", "limit"], float(30), CURRENT_TIMESTAMP)
    expected_metric.add_metric(["github_account", "used"], float(12), CURRENT_TIMESTAMP)
    expected_metric.add_metric(["github_account", "remaining"], float(18), CURRENT_TIMESTAMP)
    expected_metric.add_metric(
        ["github_account", "reset"], float(1372697452), CURRENT_TIMESTAMP
    )
    actual_metric = collector._add_metric(api_name="search", resources=mock_resources)
    assert mock_unix_timestamp.call_count == 4
    assert github_app_access_token_mock.call_count == 1
    assert actual_metric == expected_metric


def test_collect_metrics(
    github_app_access_token_mock,
    github_rate_limits_requester_mock,
    collector,
    mock_unix_timestamp,
):

    core = GaugeMetricFamily(
        "github_rate_limits_core",
        "API requests in core per hour",
        labels=["account", "type"],
    )
    core.add_metric(["github_account", "limit"], float(5000), CURRENT_TIMESTAMP)
    core.add_metric(["github_account", "used"], float(1), CURRENT_TIMESTAMP)
    core.add_metric(["github_account", "remaining"], float(4999), CURRENT_TIMESTAMP)
    core.add_metric(["github_account", "reset"], float(1372700873), CURRENT_TIMESTAMP)

    search = GaugeMetricFamily(
        "github_rate_limits_search",
        "API requests in search per hour",
        labels=["account", "type"],
    )
    search.add_metric(["github_account", "limit"], float(30), CURRENT_TIMESTAMP)
    search.add_metric(["github_account", "used"], float(12), CURRENT_TIMESTAMP)
    search.add_metric(["github_account", "remaining"], float(18), CURRENT_TIMESTAMP)
    search.add_metric(["github_account", "reset"], float(1372697452), CURRENT_TIMESTAMP)

    graphql = GaugeMetricFamily(
        "github_rate_limits_graphql",
        "API requests in graphql per hour",
        labels=["account", "type"],
    )
    graphql.add_metric(["github_account", "limit"], float(5000), CURRENT_TIMESTAMP)
    graphql.add_metric(["github_account", "used"], float(7), CURRENT_TIMESTAMP)
    graphql.add_metric(["github_account", "remaining"], float(4993), CURRENT_TIMESTAMP)
    graphql.add_metric(["github_account", "reset"], float(1372700389), CURRENT_TIMESTAMP)

    integration_manifest = GaugeMetricFamily(
        "github_rate_limits_integration_manifest",
        "API requests in integration_manifest per hour",
        labels=["account", "type"],
    )
    integration_manifest.add_metric(
        ["github_account", "limit"], float(5000), CURRENT_TIMESTAMP
    )
    integration_manifest.add_metric(["github_account", "used"], float(1), CURRENT_TIMESTAMP)
    integration_manifest.add_metric(
        ["github_account", "remaining"], float(4999), CURRENT_TIMESTAMP
    )
    integration_manifest.add_metric(
        ["github_account", "reset"], float(1551806725), CURRENT_TIMESTAMP
    )

    code_scanning_upload = GaugeMetricFamily(
        "github_rate_limits_code_scanning_upload",
        "API requests in code_scanning_upload per hour",
        labels=["account", "type"],
    )
    code_scanning_upload.add_metric(["github_account", "limit"], float(500), CURRENT_TIMESTAMP)
    code_scanning_upload.add_metric(["github_account", "used"], float(20), CURRENT_TIMESTAMP)
    code_scanning_upload.add_metric(
        ["github_account", "remaining"], float(480), CURRENT_TIMESTAMP
    )
    code_scanning_upload.add_metric(
        ["github_account", "reset"], float(1551806725), CURRENT_TIMESTAMP
    )

    expected_metrics = [
        core,
        search,
        graphql,
        integration_manifest,
        code_scanning_upload,
    ]

    assert collector.collect() == expected_metrics
    assert github_app_access_token_mock.call_count == 1
    assert github_rate_limits_requester_mock.call_count == 1
    assert mock_unix_timestamp.call_count == 20


@pytest.mark.parametrize(
    "resources, expectation",
    [
        (dict(api_name="core"), pytest.raises(ValueError)),
        (None, does_not_raise()),
        (list(), pytest.raises(ValueError)),
        (dotmap.DotMap(), does_not_raise()),
    ],
)
def test_collector_resource_type(
    github_app_access_token_mock,
    collector,
    resources,
    expectation,
):
    with expectation:
        collector._add_metric(api_name="test", resources=resources)
    assert github_app_access_token_mock.call_count == 1
