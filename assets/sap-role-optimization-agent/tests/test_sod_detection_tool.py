"""Unit tests for sod_detection_tool — 5 seeded conflicts."""
import json
import pytest

from role_discovery_tool import clear_session_dataset, merge_records
from sod_detection_tool import sod_detection_tool, load_sod_rules, roles_match_pattern


@pytest.fixture(autouse=True)
def reset_dataset():
    clear_session_dataset()
    yield
    clear_session_dataset()


def _seed_full():
    assignments = [
        ("USR001","BR_EMPLOYEE_SELF_SERVICE","S4_CLOUD"),("USR001","BR_MM_PURCHASING_USER","S4_CLOUD"),
        ("USR002","BR_EMPLOYEE_SELF_SERVICE","S4_CLOUD"),("USR002","BR_MANAGER_APPROVE","S4_CLOUD"),
        ("USR003","BR_HR_PAYROLL_USER","S4_CLOUD"),("USR004","BR_SD_SALES_ORDER_PROCESS","S4_CLOUD"),
        ("USR005","BR_FI_ACCOUNTING_USER","S4_CLOUD"),
        # SoD-001 (High): USR006
        ("USR006","BR_PURCHASE_ORDER_CREATE","S4_CLOUD"),("USR006","BR_PURCHASE_ORDER_APPROVE","S4_CLOUD"),
        ("USR006","BR_MM_PURCHASING_USER","S4_CLOUD"),
        # SoD-005 (Medium): USR007
        ("USR007","BR_FI_POST_EXECUTE","S4_ON_PREM"),("USR007","BR_PERIOD_CLOSE_ADMIN","S4_ON_PREM"),
        ("USR007","BR_FI_ACCOUNTING_USER","S4_ON_PREM"),
        ("USR008","BR_ABAP_DEVELOPER","BTP"),("USR009","BR_ABAP_DEVELOPER","BTP"),
        ("USR010","BR_BTP_DEVELOPER","BTP"),("USR011","BR_MIDDLEWARE_DEVELOPER","BTP"),
        ("USR012","BR_EXTENSION_DEVELOPER","BTP"),("USR013","BR_ABAP_DEVELOPER","BTP"),
        ("USR014","BR_ADMIN","S4_ON_PREM"),("USR014","BR_BASIS_OPS","S4_ON_PREM"),
        ("USR015","BR_SYSADMIN_SUPPORT","S4_ON_PREM"),("USR016","BR_TRANSPORT_MANAGER","S4_ON_PREM"),
        ("USR017","BR_CLIENT_ADMIN","S4_ON_PREM"),("USR018","BR_BATCH_ADMIN","S4_ON_PREM"),
        ("USR019","BR_BASIS_OPS","MULTI_TENANT"),("USR019","BR_ABAP_DEVELOPER","MULTI_TENANT"),
        ("USR020","BR_HELPDESK_AGENT","BTP"),("USR021","BR_SUPPORT_L2_SPECIALIST","BTP"),
        ("USR022","BR_SUPPORT_L3_EXPERT","BTP"),("USR023","BR_MONITORING_OPS","BTP"),
        ("USR024","BR_SERVICE_DESK_AGENT","BTP"),
        ("USR025","BR_SECURITY_ADMIN","S4_ON_PREM"),("USR025","BR_AUTH_ADMIN","S4_ON_PREM"),
        ("USR026","BR_IAM_GOVERNANCE_USER","S4_CLOUD"),("USR026","BR_USER_ADMIN","S4_CLOUD"),
        ("USR027","BR_GRC_ACCESS_CONTROL","S4_CLOUD"),("USR028","BR_AUDIT_LOG_VIEWER","S4_CLOUD"),
        # SoD-004 (Medium): USR029
        ("USR029","BR_ROLE_ADMIN","S4_CLOUD"),("USR029","BR_SECURITY_AUDITOR","S4_CLOUD"),
        ("USR029","BR_BUSINESS_ROLE_ASSIGN","S4_CLOUD"),
        # SoD-003 (High): USR030
        ("USR030","BR_USER_ADMIN","S4_CLOUD"),("USR030","BR_AUDIT_LOG_VIEWER","S4_CLOUD"),
        # SoD-002 (High): USR031
        ("USR031","BR_VENDOR_MASTER_ADMIN","BTP"),("USR031","BR_PAYMENT_PROCESS_EXECUTE","BTP"),
        ("USR032","BR_FI_ACCOUNTING_USER","S4_CLOUD"),("USR032","BR_MANAGER_APPROVE","S4_CLOUD"),
    ]
    merge_records([{"user_id": u, "role_name": r, "environment": e, "source":"test","source_ref":f"{u}/{r}/{e}"}
                   for u, r, e in assignments])


def test_sod_rules_loaded():
    assert len(load_sod_rules()) >= 5


def test_sod_rule_fields():
    for rule in load_sod_rules():
        for f in ["rule_id","role_a_pattern","role_b_pattern","risk_level"]:
            assert f in rule
        assert rule["risk_level"] in ("High","Medium","Low")


def test_roles_match_pattern():
    assert roles_match_pattern("BR_PURCHASE_ORDER_CREATE","purchase_order_create") is True
    assert roles_match_pattern("BR_EMPLOYEE_SELF_SERVICE","admin") is False


def test_detects_exactly_five_conflicts():
    _seed_full()
    result = json.loads(sod_detection_tool.invoke({}))
    assert result["status"] == "success"
    assert result["total_conflicts"] == 5


def test_sod001_usr006_high():
    _seed_full()
    conflicts = json.loads(sod_detection_tool.invoke({}))["conflicts"]
    c = next((x for x in conflicts if x["user_id"]=="USR006" and x["rule_id"]=="SOD-001"), None)
    assert c and c["risk_level"] == "High"


def test_sod005_usr007_medium():
    _seed_full()
    conflicts = json.loads(sod_detection_tool.invoke({}))["conflicts"]
    c = next((x for x in conflicts if x["user_id"]=="USR007" and x["rule_id"]=="SOD-005"), None)
    assert c and c["risk_level"] == "Medium"


def test_sod004_usr029_medium():
    _seed_full()
    conflicts = json.loads(sod_detection_tool.invoke({}))["conflicts"]
    c = next((x for x in conflicts if x["user_id"]=="USR029" and x["rule_id"]=="SOD-004"), None)
    assert c and c["risk_level"] == "Medium"


def test_sod003_usr030_high():
    _seed_full()
    conflicts = json.loads(sod_detection_tool.invoke({}))["conflicts"]
    c = next((x for x in conflicts if x["user_id"]=="USR030" and x["rule_id"]=="SOD-003"), None)
    assert c and c["risk_level"] == "High"


def test_sod002_usr031_high():
    _seed_full()
    conflicts = json.loads(sod_detection_tool.invoke({}))["conflicts"]
    c = next((x for x in conflicts if x["user_id"]=="USR031" and x["rule_id"]=="SOD-002"), None)
    assert c and c["risk_level"] == "High"


def test_risk_breakdown_3high_2medium():
    _seed_full()
    rb = json.loads(sod_detection_tool.invoke({}))["risk_breakdown"]
    assert rb.get("High",0) == 3
    assert rb.get("Medium",0) == 2


def test_high_risk_sorted_first():
    _seed_full()
    conflicts = json.loads(sod_detection_tool.invoke({}))["conflicts"]
    order = {"High":0,"Medium":1,"Low":2}
    for i in range(len(conflicts)-1):
        assert order[conflicts[i]["risk_level"]] <= order[conflicts[i+1]["risk_level"]]


def test_clean_users_not_flagged():
    _seed_full()
    flagged = {c["user_id"] for c in json.loads(sod_detection_tool.invoke({}))["conflicts"]}
    clean = {"USR001","USR002","USR003","USR004","USR005","USR008","USR014","USR015","USR020","USR025","USR026","USR032"}
    assert not (flagged & clean), f"Unexpectedly flagged: {flagged & clean}"


def test_conflict_has_mitigation():
    _seed_full()
    for c in json.loads(sod_detection_tool.invoke({}))["conflicts"]:
        assert c.get("mitigation")


def test_env_isolated_conflicts():
    merge_records([
        {"user_id":"USR999","role_name":"BR_PURCHASE_ORDER_CREATE", "environment":"S4_CLOUD","source":"t","source_ref":"r1"},
        {"user_id":"USR999","role_name":"BR_PURCHASE_ORDER_APPROVE","environment":"S4_CLOUD","source":"t","source_ref":"r2"},
        {"user_id":"USR999","role_name":"BR_PURCHASE_ORDER_CREATE", "environment":"S4_ON_PREM","source":"t","source_ref":"r3"},
    ])
    result = json.loads(sod_detection_tool.invoke({}))
    cloud_c = [c for c in result["conflicts"] if c["environment"]=="S4_CLOUD"]
    prem_c  = [c for c in result["conflicts"] if c["environment"]=="S4_ON_PREM"]
    assert len(cloud_c) >= 1
    assert len(prem_c) == 0


def test_empty_dataset_error():
    result = json.loads(sod_detection_tool.invoke({}))
    assert result["status"] == "error"
