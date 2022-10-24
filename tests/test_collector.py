import pytest
import dotmap
from prometheus_client.core import GaugeMetricFamily
from .conftest import does_not_raise


def test_add_metrics(collector, rate_limits_json, mocker):
    mock_resources = dotmap.DotMap(rate_limits_json)
    mocker.patch(
        'github_rate_limits_exporter.collector.get_unix_timestamp',
        return_value=1668193356
    )
    expected_metric = GaugeMetricFamily(
        'github_rate_limits_search',
        'API requests in search per hour',
        labels = ['account', 'type']
    )
    expected_metric.add_metric(['github_account','limit'], float(30), 1668193356)
    expected_metric.add_metric(['github_account','used'], float(12), 1668193356)
    expected_metric.add_metric(['github_account','remaining'], float(18), 1668193356)
    actual_metric = collector._add_metric(
        api_name='search',
        resources=mock_resources
    )
    assert actual_metric == expected_metric


def test_collect_metrics(collector, mock_rate_limits, mocker):
    mocker.patch(
        'github_rate_limits_exporter.collector.github.Github.get_rate_limit',
        return_value=mock_rate_limits
    )
    mocker.patch(
        'github_rate_limits_exporter.collector.get_unix_timestamp',
        return_value=1668193356
    )

    core = GaugeMetricFamily(
        'github_rate_limits_core',
        'API requests in core per hour',
        labels = ['account', 'type']
    )
    core.add_metric(['github_account','limit'], float(5000), 1668193356)
    core.add_metric(['github_account','used'], float(1), 1668193356)
    core.add_metric(['github_account','remaining'], float(4999), 1668193356)

    search = GaugeMetricFamily(
        'github_rate_limits_search',
        'API requests in search per hour',
        labels = ['account', 'type']
    )
    search.add_metric(['github_account','limit'], float(30), 1668193356)
    search.add_metric(['github_account','used'], float(12), 1668193356)
    search.add_metric(['github_account','remaining'], float(18), 1668193356)

    graphql = GaugeMetricFamily(
        'github_rate_limits_graphql',
        'API requests in graphql per hour',
        labels = ['account', 'type']
    )
    graphql.add_metric(['github_account','limit'], float(5000), 1668193356)
    graphql.add_metric(['github_account','used'], float(7), 1668193356)
    graphql.add_metric(['github_account','remaining'], float(4993), 1668193356)

    integration_manifest = GaugeMetricFamily(
        'github_rate_limits_integration_manifest',
        'API requests in integration_manifest per hour',
        labels = ['account', 'type']
    )
    integration_manifest.add_metric(['github_account','limit'], float(5000), 1668193356)
    integration_manifest.add_metric(['github_account','used'], float(1), 1668193356)
    integration_manifest.add_metric(['github_account','remaining'], float(4999), 1668193356)

    code_scanning_upload = GaugeMetricFamily(
        'github_rate_limits_code_scanning_upload',
        'API requests in code_scanning_upload per hour',
        labels = ['account', 'type']
    )
    code_scanning_upload.add_metric(['github_account','limit'], float(500), 1668193356)
    code_scanning_upload.add_metric(['github_account','used'], float(20), 1668193356)
    code_scanning_upload.add_metric(['github_account','remaining'], float(480), 1668193356)

    expected_metrics = [
        core, search, graphql,
        integration_manifest,
        code_scanning_upload
    ]

    assert collector.collect() == expected_metrics


@pytest.mark.parametrize('resources, expectation', [
    (dict(api_name='core'), pytest.raises(ValueError)),
    (None, does_not_raise()),
    (list(), pytest.raises(ValueError)),
    (dotmap.DotMap(), does_not_raise())
])
def test_collector_resource_type(collector, resources, expectation):
    with expectation:
        collector._add_metric(
            api_name='test', resources=resources
        )
