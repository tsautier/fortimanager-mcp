"""add_model_device version mapping (verified live against FMG 7.6.7).

FMG expects the major version in os_ver ("7.0") and the minor in a separate
mr field; sending "7.6" as os_ver fails with "Unsupported device/ADOM
version".
"""

from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from fortimanager_mcp.tools import dvm_tools


async def _add(os_version: str) -> dict[str, Any]:
    client = MagicMock()
    client.add_device = AsyncMock(return_value={"device": {}})
    with patch.object(dvm_tools, "get_fmg_client", return_value=client):
        result = await dvm_tools.add_model_device(
            adom="root",
            name="MODEL-FGT",
            serial_number="FGT60FTK00000001",
            platform="FortiGate-60F",
            os_version=os_version,
        )
    assert result["status"] == "success", result
    return client.add_device.call_args.kwargs["device"]


class TestModelDeviceVersionMapping:
    @pytest.mark.asyncio
    async def test_minor_version_goes_to_mr_field(self) -> None:
        device = await _add("7.6")
        assert device["os_ver"] == "7.0"
        assert device["mr"] == 6

    @pytest.mark.asyncio
    async def test_dot_zero_keeps_mr_zero(self) -> None:
        device = await _add("7.0")
        assert device["os_ver"] == "7.0"
        assert device["mr"] == 0
