"""Regression tests for isolated NetworkManager practice validation."""

from unittest.mock import patch

import pytest

from tasks.networking import ConfigureStaticIPTask, TroubleshootNetworkTask


pytestmark = pytest.mark.unit


def test_nmcli_value_contains_handles_scalar_and_list_values():
    connection = {
        "ipv4.gateway": "192.0.2.1",
        "ipv4.dns": "8.8.8.8,1.1.1.1",
    }

    from tasks.networking import _nmcli_value_contains

    assert _nmcli_value_contains(connection, "ipv4.gateway", "192.0.2.1")
    assert _nmcli_value_contains(connection, "ipv4.dns", "1.1.1.1")
    assert not _nmcli_value_contains(connection, "ipv4.dns", "9.9.9.9")


def test_static_ip_accepts_gateway_and_dns_in_never_default_profile():
    task = ConfigureStaticIPTask().generate(
        interface="dummy0",
        connection="dummy0",
        ip="192.0.2.20",
        gateway="192.0.2.1",
        dns="8.8.8.8",
    )
    connection = {
        "ipv4.method": "manual",
        "ipv4.gateway": "192.0.2.1",
        "ipv4.dns": "8.8.8.8",
    }

    with patch("tasks.networking.get_ip_address", return_value="192.0.2.20"), \
         patch("tasks.networking.get_nmcli_connection_info", return_value=connection), \
         patch("tasks.networking.get_interface_state", return_value="UP"):
        result = task.validate()

    assert result.passed
    assert result.score == 15


def test_troubleshoot_accepts_profile_gateway_and_dns_without_global_route():
    task = TroubleshootNetworkTask().generate(
        interface="dummy0",
        connection="dummy0",
        ip="192.0.2.20",
        gateway="192.0.2.1",
        dns="8.8.8.8",
    )
    connection = {
        "ipv4.method": "manual",
        "ipv4.addresses": "192.0.2.20/24",
        "ipv4.gateway": "192.0.2.1",
        "ipv4.dns": "8.8.8.8",
    }

    with patch("tasks.networking.get_nmcli_connection_info", return_value=connection), \
         patch("tasks.networking.get_ip_address", return_value="192.0.2.20"), \
         patch("tasks.networking.get_interface_state", return_value="UP"):
        result = task.validate()

    assert result.passed
    assert result.score == 18
