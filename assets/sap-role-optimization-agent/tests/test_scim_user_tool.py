"""Unit tests for scim_user_tool."""
import json
import pytest
from unittest.mock import AsyncMock

from role_discovery_tool import clear_session_dataset, get_session_dataset
from scim_user_tool import create_scim_user_tool

MOCK_SCIM_USERS = [
    {"id":"USR001","displayName":"Carol Employee",    "groups":[{"display":"BR_EMPLOYEE_SELF_SERVICE"},{"display":"BR_MM_PURCHASING_USER"}]},
    {"id":"USR002","displayName":"Dave Manager",      "groups":[{"display":"BR_EMPLOYEE_SELF_SERVICE"},{"display":"BR_MANAGER_APPROVE"},{"display":"BR_CO_COST_CENTER_MANAGER"}]},
    {"id":"USR003","displayName":"Eve HR",            "groups":[{"display":"BR_HR_PAYROLL_USER"},{"display":"BR_EMPLOYEE_SELF_SERVICE"}]},
    {"id":"USR004","displayName":"Frank Sales",       "groups":[{"display":"BR_SD_SALES_ORDER_PROCESS"}]},
    {"id":"USR005","displayName":"Grace Finance",     "groups":[{"display":"BR_FI_ACCOUNTING_USER"},{"display":"BR_CO_COST_CENTER_MANAGER"}]},
    {"id":"USR006","displayName":"Henry Proc",        "groups":[{"display":"BR_PURCHASE_ORDER_CREATE"},{"display":"BR_PURCHASE_ORDER_APPROVE"},{"display":"BR_MM_PURCHASING_USER"}]},
    {"id":"USR007","displayName":"Iris Finance Ctrl", "groups":[{"display":"BR_FI_POST_EXECUTE"},{"display":"BR_PERIOD_CLOSE_ADMIN"},{"display":"BR_FI_ACCOUNTING_USER"}]},
    {"id":"USR008","displayName":"Alice ABAP Dev",    "groups":[{"display":"BR_ABAP_DEVELOPER"},{"display":"BR_ABAP_WORKBENCH"}]},
    {"id":"USR009","displayName":"Bob Fiori Dev",     "groups":[{"display":"BR_ABAP_DEVELOPER"},{"display":"BR_FIORI_DEVELOPER"}]},
    {"id":"USR010","displayName":"Carol BTP Dev",     "groups":[{"display":"BR_BTP_DEVELOPER"},{"display":"BR_API_INTEGRATION"}]},
    {"id":"USR011","displayName":"Dave Integration",  "groups":[{"display":"BR_MIDDLEWARE_DEVELOPER"},{"display":"BR_API_INTEGRATION"}]},
    {"id":"USR012","displayName":"Eve Extension Dev", "groups":[{"display":"BR_EXTENSION_DEVELOPER"},{"display":"BR_BTP_DEVELOPER"}]},
    {"id":"USR013","displayName":"Frank Tech Dev",    "groups":[{"display":"BR_ABAP_DEVELOPER"},{"display":"BR_ABAP_WORKBENCH"},{"display":"BR_FIORI_DEVELOPER"}]},
    {"id":"USR014","displayName":"John Basis Admin",  "groups":[{"display":"BR_ADMIN"},{"display":"BR_BASIS_OPS"},{"display":"BR_TRANSPORT_MANAGER"}]},
    {"id":"USR015","displayName":"Kate SysAdmin",     "groups":[{"display":"BR_SYSADMIN_SUPPORT"},{"display":"BR_RFC_DESTINATION_ADMIN"},{"display":"BR_BATCH_ADMIN"}]},
    {"id":"USR016","displayName":"Leo Transport Mgr", "groups":[{"display":"BR_TRANSPORT_MANAGER"},{"display":"BR_BASIS_OPS"}]},
    {"id":"USR017","displayName":"Mia Client Admin",  "groups":[{"display":"BR_CLIENT_ADMIN"},{"display":"BR_SYSADMIN_SUPPORT"}]},
    {"id":"USR018","displayName":"Nora Batch Admin",  "groups":[{"display":"BR_BATCH_ADMIN"},{"display":"BR_BASIS_OPS"}]},
    {"id":"USR019","displayName":"Oscar Basis Ops",   "groups":[{"display":"BR_BASIS_OPS"},{"display":"BR_RFC_DESTINATION_ADMIN"},{"display":"BR_ABAP_DEVELOPER"},{"display":"BR_HELPDESK_AGENT"},{"display":"BR_FI_ACCOUNTING_USER"},{"display":"BR_EMPLOYEE_SELF_SERVICE"}]},
    {"id":"USR020","displayName":"Emma L1 Support",   "groups":[{"display":"BR_HELPDESK_AGENT"},{"display":"BR_INCIDENT_MANAGER"}]},
    {"id":"USR021","displayName":"Frank L2 Support",  "groups":[{"display":"BR_SUPPORT_L2_SPECIALIST"},{"display":"BR_HELPDESK_AGENT"}]},
    {"id":"USR022","displayName":"Grace L3 Expert",   "groups":[{"display":"BR_SUPPORT_L3_EXPERT"},{"display":"BR_MONITORING_OPS"}]},
    {"id":"USR023","displayName":"Harry Ops Mgr",     "groups":[{"display":"BR_MONITORING_OPS"},{"display":"BR_INCIDENT_MANAGER"}]},
    {"id":"USR024","displayName":"Iris Service Desk", "groups":[{"display":"BR_SERVICE_DESK_AGENT"},{"display":"BR_HELPDESK_AGENT"}]},
    {"id":"USR025","displayName":"Jack Sec Admin",    "groups":[{"display":"BR_SECURITY_ADMIN"},{"display":"BR_AUTH_ADMIN"}]},
    {"id":"USR026","displayName":"Kate IAM Manager",  "groups":[{"display":"BR_IAM_GOVERNANCE_USER"},{"display":"BR_USER_ADMIN"}]},
    {"id":"USR027","displayName":"Leo GRC Analyst",   "groups":[{"display":"BR_GRC_ACCESS_CONTROL"},{"display":"BR_COMPLIANCE_OFFICER"}]},
    {"id":"USR028","displayName":"Mia Auditor",       "groups":[{"display":"BR_AUDIT_LOG_VIEWER"},{"display":"BR_COMPLIANCE_REVIEWER"}]},
    {"id":"USR029","displayName":"Nora Role Admin",   "groups":[{"display":"BR_ROLE_ADMIN"},{"display":"BR_SECURITY_AUDITOR"},{"display":"BR_BUSINESS_ROLE_ASSIGN"}]},
    {"id":"USR030","displayName":"Oscar Sec Analyst", "groups":[{"display":"BR_USER_ADMIN"},{"display":"BR_AUDIT_LOG_VIEWER"}]},
    {"id":"USR031","displayName":"Peter Vendor Mgr",  "groups":[{"display":"BR_VENDOR_MASTER_ADMIN"},{"display":"BR_PAYMENT_PROCESS_EXECUTE"}]},
    {"id":"USR032","displayName":"Quinn Finance Mgr", "groups":[{"display":"BR_FI_ACCOUNTING_USER"},{"display":"BR_MM_PURCHASING_USER"},{"display":"BR_MANAGER_APPROVE"}]},
]


@pytest.fixture(autouse=True)
def reset_dataset():
    clear_session_dataset()
    yield
    clear_session_dataset()


def _make_scim_tool(users=None):
    mock_tool = AsyncMock()
    mock_tool.name = "getAllUsersUsingGET"
    mock_tool.ainvoke = AsyncMock(return_value={"Resources": users or MOCK_SCIM_USERS})
    return create_scim_user_tool([mock_tool])


@pytest.mark.asyncio
async def test_scim_ingests_all_32_users():
    tool = _make_scim_tool()
    result = json.loads(await tool.ainvoke({"environment": "S4_CLOUD"}))
    assert result["status"] == "success"
    assert result["users_fetched"] == 32
    assert len({r["user_id"] for r in get_session_dataset()}) == 32


@pytest.mark.asyncio
async def test_scim_total_role_records():
    tool = _make_scim_tool()
    await tool.ainvoke({"environment": "S4_CLOUD"})
    expected = sum(len(u["groups"]) for u in MOCK_SCIM_USERS)
    assert len(get_session_dataset()) == expected


@pytest.mark.asyncio
async def test_scim_over_privileged_user_has_6_records():
    tool = _make_scim_tool()
    await tool.ainvoke({"environment": "S4_CLOUD"})
    assert len([r for r in get_session_dataset() if r["user_id"] == "USR019"]) == 6


@pytest.mark.asyncio
async def test_scim_single_role_user_stored():
    tool = _make_scim_tool()
    await tool.ainvoke({"environment": "BTP"})
    usr004 = [r for r in get_session_dataset() if r["user_id"] == "USR004"]
    assert len(usr004) == 1
    assert usr004[0]["role_name"] == "BR_SD_SALES_ORDER_PROCESS"


@pytest.mark.asyncio
async def test_scim_multi_env_no_cross_contamination():
    tool = _make_scim_tool(users=[{"id": "USR014", "displayName": "John", "groups": [{"display": "BR_ADMIN"}]}])
    await tool.ainvoke({"environment": "S4_ON_PREM"})
    await tool.ainvoke({"environment": "S4_CLOUD"})
    envs = {r["environment"] for r in get_session_dataset() if r["user_id"] == "USR014"}
    assert "S4_ON_PREM" in envs and "S4_CLOUD" in envs


@pytest.mark.asyncio
async def test_scim_no_groups_assigns_no_role_marker():
    tool = _make_scim_tool(users=[{"id": "USR099", "displayName": "Ghost", "groups": []}])
    result = json.loads(await tool.ainvoke({"environment": "BTP"}))
    assert result["status"] == "success"
    assert get_session_dataset()[0]["role_name"] == "NO_ROLE_ASSIGNED"


@pytest.mark.asyncio
async def test_scim_no_mcp_tool_returns_error():
    tool = create_scim_user_tool([])
    result = json.loads(await tool.ainvoke({"environment": "BTP"}))
    assert result["status"] == "error"
