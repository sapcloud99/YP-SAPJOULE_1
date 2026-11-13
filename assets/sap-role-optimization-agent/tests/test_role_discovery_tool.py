"""Unit tests for role_discovery_tool."""
import json
import pytest
from unittest.mock import AsyncMock

from role_discovery_tool import (
    create_role_discovery_tool,
    clear_session_dataset,
    get_session_dataset,
    normalize_environment,
    merge_records,
)


@pytest.fixture(autouse=True)
def reset_dataset():
    clear_session_dataset()
    yield
    clear_session_dataset()


@pytest.mark.parametrize("raw,expected", [
    ("on-premise",    "S4_ON_PREM"),
    ("onprem",        "S4_ON_PREM"),
    ("s/4 op",        "S4_ON_PREM"),
    ("BTP",           "BTP"),
    ("btp",           "BTP"),
    ("cloud",         "S4_CLOUD"),
    ("s4_cloud",      "S4_CLOUD"),
    ("multi-tenant",  "MULTI_TENANT"),
    ("multitenant",   "MULTI_TENANT"),
    ("MULTI_TENANT",  "MULTI_TENANT"),
])
def test_normalize_environment_aliases(raw, expected):
    assert normalize_environment(raw) == expected


def test_merge_records_deduplication():
    rec = {"user_id": "USR001", "role_name": "BR_ADMIN", "environment": "BTP", "source": "api", "source_ref": "r1"}
    added1 = merge_records([rec])
    added2 = merge_records([rec])
    assert added1 == 1
    assert added2 == 0
    assert len(get_session_dataset()) == 1


def test_merge_records_same_user_different_env():
    records = [
        {"user_id": "USR001", "role_name": "BR_ADMIN", "environment": "BTP",         "source": "api", "source_ref": "r1"},
        {"user_id": "USR001", "role_name": "BR_ADMIN", "environment": "S4_ON_PREM",  "source": "api", "source_ref": "r2"},
        {"user_id": "USR001", "role_name": "BR_ADMIN", "environment": "S4_CLOUD",    "source": "api", "source_ref": "r3"},
        {"user_id": "USR001", "role_name": "BR_ADMIN", "environment": "MULTI_TENANT","source": "api", "source_ref": "r4"},
    ]
    assert merge_records(records) == 4


def test_merge_records_32_users_no_loss():
    records = []
    for i in range(1, 33):
        for role in [f"BR_ROLE_{j}" for j in range(1, 4)]:
            records.append({"user_id": f"USR{i:03d}", "role_name": role, "environment": "S4_CLOUD",
                             "source": "api", "source_ref": f"USR{i:03d}/{role}"})
    assert merge_records(records) == 32 * 3
    assert len(get_session_dataset()) == 32 * 3


def test_merge_records_cross_env_tagging():
    records = [
        {"user_id": "USR014", "role_name": "BR_BASIS_OPS", "environment": "S4_ON_PREM", "source": "api", "source_ref": "r1"},
        {"user_id": "USR014", "role_name": "BR_BASIS_OPS", "environment": "BTP",        "source": "api", "source_ref": "r2"},
    ]
    assert merge_records(records) == 2
    envs = {r["environment"] for r in get_session_dataset()}
    assert "S4_ON_PREM" in envs and "BTP" in envs


@pytest.mark.asyncio
async def test_role_discovery_tool_success_normalizes_records():
    mock_tool = AsyncMock()
    mock_tool.name = "list_businessroles"
    mock_tool.ainvoke = AsyncMock(return_value={"value": [
        {"BusinessRole": "BR_ADMIN",        "BusinessRoleAssignment": "USR014"},
        {"BusinessRole": "BR_BASIS_OPS",     "BusinessRoleAssignment": "USR014"},
        {"BusinessRole": "BR_ABAP_DEVELOPER","BusinessRoleAssignment": "USR008"},
        {"BusinessRole": "BR_ABAP_DEVELOPER","BusinessRoleAssignment": "USR009"},
        {"BusinessRole": "BR_HELPDESK_AGENT","BusinessRoleAssignment": "USR020"},
    ]})
    tool = create_role_discovery_tool([mock_tool])
    result = json.loads(await tool.ainvoke({"environment": "S4_ON_PREM"}))
    assert result["status"] == "success"
    assert result["environment"] == "S4_ON_PREM"
    assert result["roles_fetched"] == 5


@pytest.mark.asyncio
async def test_role_discovery_tool_list_response_format():
    mock_tool = AsyncMock()
    mock_tool.name = "list_businessroles"
    mock_tool.ainvoke = AsyncMock(return_value=[
        {"BusinessRole": "BR_ADMIN", "BusinessRoleAssignment": "USR014"},
    ])
    tool = create_role_discovery_tool([mock_tool])
    result = json.loads(await tool.ainvoke({"environment": "BTP"}))
    assert result["status"] == "success"


@pytest.mark.asyncio
async def test_role_discovery_tool_no_mcp_tools():
    tool = create_role_discovery_tool([])
    result = json.loads(await tool.ainvoke({"environment": "BTP"}))
    assert result["status"] == "error"
    assert "not available" in result["message"]


@pytest.mark.asyncio
async def test_role_discovery_tool_normalizes_environment_alias():
    mock_tool = AsyncMock()
    mock_tool.name = "list_businessroles"
    mock_tool.ainvoke = AsyncMock(return_value={"value": [
        {"BusinessRole": "BR_ADMIN", "BusinessRoleAssignment": "USR014"},
    ]})
    tool = create_role_discovery_tool([mock_tool])
    result = json.loads(await tool.ainvoke({"environment": "on-premise"}))
    assert result["environment"] == "S4_ON_PREM"


@pytest.mark.asyncio
async def test_role_discovery_tool_deduplicates_across_calls():
    mock_tool = AsyncMock()
    mock_tool.name = "list_businessroles"
    mock_tool.ainvoke = AsyncMock(return_value={"value": [
        {"BusinessRole": "BR_ADMIN", "BusinessRoleAssignment": "USR014"},
    ]})
    tool = create_role_discovery_tool([mock_tool])
    await tool.ainvoke({"environment": "S4_CLOUD"})
    result2 = json.loads(await tool.ainvoke({"environment": "S4_CLOUD"}))
    assert result2["records_added"] == 0
    assert result2["total_in_session"] == 1
