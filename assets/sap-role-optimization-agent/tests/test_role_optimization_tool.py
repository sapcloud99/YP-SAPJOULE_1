"""Unit tests for role_optimization_tool."""
import json
import pytest

from role_discovery_tool import clear_session_dataset, merge_records
from classify_roles_tool import classify_roles_tool
from role_optimization_tool import role_optimization_tool, find_excess_roles


@pytest.fixture(autouse=True)
def reset_dataset():
    clear_session_dataset()
    yield
    clear_session_dataset()


def _seed_full():
    assignments = [
        ("USR001","BR_EMPLOYEE_SELF_SERVICE","S4_CLOUD"),("USR001","BR_MM_PURCHASING_USER","S4_CLOUD"),
        ("USR002","BR_EMPLOYEE_SELF_SERVICE","S4_CLOUD"),("USR002","BR_MANAGER_APPROVE","S4_CLOUD"),
        ("USR003","BR_HR_PAYROLL_USER","S4_CLOUD"),
        ("USR004","BR_SD_SALES_ORDER_PROCESS","S4_CLOUD"),   # under-privileged
        ("USR005","BR_FI_ACCOUNTING_USER","S4_CLOUD"),
        ("USR006","BR_PURCHASE_ORDER_CREATE","S4_CLOUD"),("USR006","BR_PURCHASE_ORDER_APPROVE","S4_CLOUD"),
        ("USR007","BR_FI_POST_EXECUTE","S4_ON_PREM"),("USR007","BR_PERIOD_CLOSE_ADMIN","S4_ON_PREM"),
        ("USR008","BR_ABAP_DEVELOPER","BTP"),("USR009","BR_ABAP_DEVELOPER","BTP"),
        ("USR010","BR_BTP_DEVELOPER","BTP"),("USR011","BR_MIDDLEWARE_DEVELOPER","BTP"),
        ("USR012","BR_EXTENSION_DEVELOPER","BTP"),("USR013","BR_ABAP_DEVELOPER","BTP"),
        ("USR014","BR_ADMIN","S4_ON_PREM"),("USR014","BR_BASIS_OPS","S4_ON_PREM"),
        ("USR015","BR_SYSADMIN_SUPPORT","S4_ON_PREM"),("USR016","BR_TRANSPORT_MANAGER","S4_ON_PREM"),
        ("USR017","BR_CLIENT_ADMIN","S4_ON_PREM"),("USR018","BR_BATCH_ADMIN","S4_ON_PREM"),
        # USR019: over-privileged (6 roles, 4 categories)
        ("USR019","BR_BASIS_OPS","MULTI_TENANT"),("USR019","BR_ABAP_DEVELOPER","MULTI_TENANT"),
        ("USR019","BR_HELPDESK_AGENT","MULTI_TENANT"),("USR019","BR_FI_ACCOUNTING_USER","MULTI_TENANT"),
        ("USR019","BR_EMPLOYEE_SELF_SERVICE","MULTI_TENANT"),("USR019","BR_RFC_DESTINATION_ADMIN","MULTI_TENANT"),
        ("USR020","BR_HELPDESK_AGENT","BTP"),("USR021","BR_SUPPORT_L2_SPECIALIST","BTP"),
        ("USR022","BR_SUPPORT_L3_EXPERT","BTP"),("USR023","BR_MONITORING_OPS","BTP"),
        ("USR024","BR_SERVICE_DESK_AGENT","BTP"),
        ("USR025","BR_SECURITY_ADMIN","S4_ON_PREM"),("USR026","BR_IAM_GOVERNANCE_USER","S4_CLOUD"),
        ("USR027","BR_GRC_ACCESS_CONTROL","S4_CLOUD"),("USR028","BR_AUDIT_LOG_VIEWER","S4_CLOUD"),
        ("USR029","BR_ROLE_ADMIN","S4_CLOUD"),("USR029","BR_BUSINESS_ROLE_ASSIGN","S4_CLOUD"),
        ("USR030","BR_USER_ADMIN","S4_CLOUD"),("USR031","BR_VENDOR_MASTER_ADMIN","BTP"),
        ("USR032","BR_FI_ACCOUNTING_USER","S4_CLOUD"),("USR032","BR_MANAGER_APPROVE","S4_CLOUD"),
    ]
    merge_records([{"user_id":u,"role_name":r,"environment":e,"source":"test","source_ref":f"{u}/{r}/{e}"}
                   for u,r,e in assignments])
    classify_roles_tool.invoke({})


def test_find_excess_technical_with_security():
    excess = find_excess_roles(["BR_ABAP_DEVELOPER","BR_SECURITY_ADMIN"],"Technical")
    assert "BR_SECURITY_ADMIN" in excess


def test_find_excess_clean_user_no_excess():
    excess = find_excess_roles(["BR_ABAP_DEVELOPER","BR_ABAP_WORKBENCH","BR_FIORI_DEVELOPER"],"Technical")
    assert len(excess) == 0


def test_find_excess_basis_with_finance():
    excess = find_excess_roles(["BR_ADMIN","BR_BASIS_OPS","BR_FI_ACCOUNTING_USER"],"Backend/Basis")
    assert "BR_FI_ACCOUNTING_USER" in excess


def test_32_users_analyzed():
    _seed_full()
    result = json.loads(role_optimization_tool.invoke({}))
    assert result["status"] == "success"
    assert result["total_users_analyzed"] == 32


def test_usr019_over_privileged():
    _seed_full()
    over_ids = {u["user_id"] for u in json.loads(role_optimization_tool.invoke({}))["over_privileged_users"]}
    assert "USR019" in over_ids


def test_usr004_under_privileged():
    _seed_full()
    under_ids = {u["user_id"] for u in json.loads(role_optimization_tool.invoke({}))["under_privileged_users"]}
    assert "USR004" in under_ids


def test_all_require_approval():
    _seed_full()
    result = json.loads(role_optimization_tool.invoke({}))
    assert result["all_recommendations_require_human_approval"] is True
    for entry in result["over_privileged_users"] + result["under_privileged_users"]:
        assert entry["requires_human_approval"] is True


def test_result_fields():
    _seed_full()
    result = json.loads(role_optimization_tool.invoke({}))
    for f in ["total_users_analyzed","over_privileged_count","under_privileged_count","optimal_count"]:
        assert f in result


def test_not_classified_error():
    merge_records([{"user_id":"USR001","role_name":"BR_EMPLOYEE_SELF_SERVICE",
                    "environment":"S4_CLOUD","source":"test","source_ref":"r1"}])
    result = json.loads(role_optimization_tool.invoke({}))
    assert result["status"] == "error"


def test_empty_dataset_error():
    result = json.loads(role_optimization_tool.invoke({}))
    assert result["status"] == "error"
