"""Unit tests for single_holder_detection_tool."""
import json
import pytest

from role_discovery_tool import clear_session_dataset, merge_records
from single_holder_detection_tool import single_holder_detection_tool, get_criticality


@pytest.fixture(autouse=True)
def reset_dataset():
    clear_session_dataset()
    yield
    clear_session_dataset()


def _seed_full():
    assignments = [
        ("USR001","BR_EMPLOYEE_SELF_SERVICE","S4_CLOUD"),("USR002","BR_EMPLOYEE_SELF_SERVICE","S4_CLOUD"),
        ("USR003","BR_EMPLOYEE_SELF_SERVICE","S4_CLOUD"),
        ("USR014","BR_BASIS_OPS","S4_ON_PREM"),("USR016","BR_BASIS_OPS","S4_ON_PREM"),("USR018","BR_BASIS_OPS","S4_ON_PREM"),
        ("USR014","BR_TRANSPORT_MANAGER","S4_ON_PREM"),("USR016","BR_TRANSPORT_MANAGER","S4_ON_PREM"),
        ("USR008","BR_ABAP_DEVELOPER","BTP"),("USR009","BR_ABAP_DEVELOPER","BTP"),("USR013","BR_ABAP_DEVELOPER","BTP"),
        ("USR026","BR_USER_ADMIN","S4_CLOUD"),("USR030","BR_USER_ADMIN","S4_CLOUD"),
        ("USR028","BR_AUDIT_LOG_VIEWER","S4_CLOUD"),("USR030","BR_AUDIT_LOG_VIEWER","S4_CLOUD"),
        # Single-holder High-criticality
        ("USR014","BR_ADMIN","S4_ON_PREM"),
        ("USR017","BR_CLIENT_ADMIN","S4_ON_PREM"),
        ("USR025","BR_SECURITY_ADMIN","S4_ON_PREM"),
        ("USR025","BR_AUTH_ADMIN","S4_ON_PREM"),
        ("USR026","BR_IAM_GOVERNANCE_USER","S4_CLOUD"),
        # Single-holder Medium
        ("USR007","BR_FI_POST_EXECUTE","S4_ON_PREM"),
        ("USR007","BR_PERIOD_CLOSE_ADMIN","S4_ON_PREM"),
    ]
    merge_records([{"user_id":u,"role_name":r,"environment":e,"source":"test","source_ref":f"{u}/{r}/{e}"}
                   for u,r,e in assignments])


@pytest.mark.parametrize("role,expected", [
    ("BR_ADMIN","High"),("BR_SECURITY_ADMIN","High"),("BR_AUTH_ADMIN","High"),
    ("BR_CLIENT_ADMIN","High"),("BR_IAM_GOVERNANCE_USER","High"),
    ("BR_FI_POST_EXECUTE","Medium"),("BR_PERIOD_CLOSE_ADMIN","Medium"),
    ("BR_TRANSPORT_MANAGER","Medium"),("BR_MANAGER_APPROVE","Medium"),
    ("BR_SD_SALES_ORDER_PROCESS","Low"),("BR_EMPLOYEE_SELF_SERVICE","Low"),
])
def test_criticality_known_roles(role, expected):
    got, _ = get_criticality(role)
    assert got == expected, f"{role}: expected {expected}, got {got}"


def test_detects_five_high_single_holders():
    _seed_full()
    result = json.loads(single_holder_detection_tool.invoke({}))
    high = {r["role_name"] for r in result["single_holder_roles"] if r["criticality"]=="High"}
    for expected in {"BR_ADMIN","BR_CLIENT_ADMIN","BR_SECURITY_ADMIN","BR_AUTH_ADMIN","BR_IAM_GOVERNANCE_USER"}:
        assert expected in high, f"Missing: {expected}"


def test_detects_medium_single_holders():
    _seed_full()
    result = json.loads(single_holder_detection_tool.invoke({}))
    medium = {r["role_name"] for r in result["single_holder_roles"] if r["criticality"]=="Medium"}
    assert "BR_FI_POST_EXECUTE" in medium
    assert "BR_PERIOD_CLOSE_ADMIN" in medium


def test_multi_holder_roles_not_flagged():
    _seed_full()
    flagged = {r["role_name"] for r in json.loads(single_holder_detection_tool.invoke({}))["single_holder_roles"]}
    for multi in ["BR_EMPLOYEE_SELF_SERVICE","BR_BASIS_OPS","BR_TRANSPORT_MANAGER","BR_ABAP_DEVELOPER","BR_USER_ADMIN","BR_AUDIT_LOG_VIEWER"]:
        assert multi not in flagged


def test_high_criticality_sorted_first():
    _seed_full()
    roles = json.loads(single_holder_detection_tool.invoke({}))["single_holder_roles"]
    order = {"High":0,"Medium":1,"Low":2}
    for i in range(len(roles)-1):
        assert order[roles[i]["criticality"]] <= order[roles[i+1]["criticality"]]


def test_criticality_breakdown():
    _seed_full()
    bd = json.loads(single_holder_detection_tool.invoke({}))["criticality_breakdown"]
    assert bd.get("High",0) >= 5
    assert bd.get("Medium",0) >= 2


def test_result_fields():
    _seed_full()
    for r in json.loads(single_holder_detection_tool.invoke({}))["single_holder_roles"]:
        for f in ["role_name","environment","current_holder","criticality","criticality_reason","risk_statement"]:
            assert f in r


def test_cross_environment_distinct():
    merge_records([
        {"user_id":"USR014","role_name":"BR_ADMIN","environment":"S4_ON_PREM","source":"t","source_ref":"r1"},
        {"user_id":"USR099","role_name":"BR_ADMIN","environment":"BTP","source":"t","source_ref":"r2"},
    ])
    result = json.loads(single_holder_detection_tool.invoke({}))
    assert result["total_single_holder_roles"] == 2


def test_empty_dataset_error():
    result = json.loads(single_holder_detection_tool.invoke({}))
    assert result["status"] == "error"
