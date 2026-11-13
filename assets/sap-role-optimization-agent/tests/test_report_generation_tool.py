"""Unit tests for report_generation_tool."""
import json
import pytest

from role_discovery_tool import clear_session_dataset, merge_records
from classify_roles_tool import classify_roles_tool
from sod_detection_tool import sod_detection_tool
from single_holder_detection_tool import single_holder_detection_tool
from role_optimization_tool import role_optimization_tool
from report_generation_tool import (
    report_generation_tool, calculate_iam_risk_score, LARGE_DATASET_THRESHOLD,
)


@pytest.fixture(autouse=True)
def reset_dataset():
    clear_session_dataset()
    yield
    clear_session_dataset()


def _seed_small():
    records = [{"user_id":f"USR{i:03d}","role_name":f"BR_ROLE_{i}",
                "environment":"S4_CLOUD" if i<=10 else "BTP","source":"test","source_ref":f"r{i}"}
               for i in range(1, 21)]
    merge_records(records)


@pytest.mark.parametrize("sod,sh,over,total,expected", [
    (0,0,0,10,0.0),(5,3,2,10,min((5*2+3*3+2)/10*100,100.0)),
    (100,100,100,1,100.0),(0,0,0,0,0.0),(1,0,0,100,2.0),(0,1,0,100,3.0),(0,0,1,100,1.0),
])
def test_iam_risk_score(sod,sh,over,total,expected):
    assert abs(calculate_iam_risk_score(sod,sh,over,total) - expected) < 0.01


def test_risk_score_always_0_to_100():
    for sod in [0,1,10]:
        for sh in [0,1]:
            assert 0.0 <= calculate_iam_risk_score(sod,sh,1,20) <= 100.0


def test_small_dataset_not_auto_triggered():
    _seed_small()
    result = json.loads(report_generation_tool.invoke({}))
    assert result["status"] == "success"
    assert result["auto_triggered"] is False


def test_report_structure():
    _seed_small()
    result = json.loads(report_generation_tool.invoke({}))
    assert "tabular_summary" in result
    assert "visual_charts" in result
    assert "report_payload" in result


def test_large_dataset_auto_triggered():
    records = [{"user_id":f"LUSR{i:03d}","role_name":f"BR_ROLE_{j}",
                "environment":["S4_CLOUD","BTP","S4_ON_PREM","MULTI_TENANT"][j%4],
                "source":"test","source_ref":f"L{i}{j}"}
               for i in range(1,23) for j in range(1,6)]
    merge_records(records)
    result = json.loads(report_generation_tool.invoke({}))
    assert result["auto_triggered"] is True


def test_large_dataset_threshold_is_100():
    assert LARGE_DATASET_THRESHOLD == 100


def _run_full_pipeline():
    assignments = [
        ("USR001","BR_EMPLOYEE_SELF_SERVICE","S4_CLOUD"),("USR006","BR_PURCHASE_ORDER_CREATE","S4_CLOUD"),
        ("USR006","BR_PURCHASE_ORDER_APPROVE","S4_CLOUD"),("USR007","BR_FI_POST_EXECUTE","S4_ON_PREM"),
        ("USR007","BR_PERIOD_CLOSE_ADMIN","S4_ON_PREM"),("USR008","BR_ABAP_DEVELOPER","BTP"),
        ("USR009","BR_ABAP_DEVELOPER","BTP"),("USR014","BR_ADMIN","S4_ON_PREM"),
        ("USR014","BR_BASIS_OPS","S4_ON_PREM"),("USR019","BR_BASIS_OPS","MULTI_TENANT"),
        ("USR019","BR_ABAP_DEVELOPER","MULTI_TENANT"),("USR019","BR_HELPDESK_AGENT","MULTI_TENANT"),
        ("USR019","BR_FI_ACCOUNTING_USER","MULTI_TENANT"),("USR019","BR_EMPLOYEE_SELF_SERVICE","MULTI_TENANT"),
        ("USR019","BR_RFC_DESTINATION_ADMIN","MULTI_TENANT"),
        ("USR020","BR_HELPDESK_AGENT","BTP"),("USR021","BR_SUPPORT_L2_SPECIALIST","BTP"),
        ("USR025","BR_SECURITY_ADMIN","S4_ON_PREM"),("USR026","BR_IAM_GOVERNANCE_USER","S4_CLOUD"),
        ("USR029","BR_ROLE_ADMIN","S4_CLOUD"),("USR029","BR_BUSINESS_ROLE_ASSIGN","S4_CLOUD"),
        ("USR030","BR_USER_ADMIN","S4_CLOUD"),("USR030","BR_AUDIT_LOG_VIEWER","S4_CLOUD"),
        ("USR031","BR_VENDOR_MASTER_ADMIN","BTP"),("USR031","BR_PAYMENT_PROCESS_EXECUTE","BTP"),
        ("USR032","BR_FI_ACCOUNTING_USER","S4_CLOUD"),("USR032","BR_MANAGER_APPROVE","S4_CLOUD"),
    ]
    merge_records([{"user_id":u,"role_name":r,"environment":e,"source":"test","source_ref":f"{u}/{r}/{e}"}
                   for u,r,e in assignments])
    classify_roles_tool.invoke({})
    return (json.loads(sod_detection_tool.invoke({})),
            json.loads(single_holder_detection_tool.invoke({})),
            json.loads(role_optimization_tool.invoke({})))


def test_full_pipeline_risk_score_positive():
    sod_r, sh_r, opt_r = _run_full_pipeline()
    result = json.loads(report_generation_tool.invoke({
        "sod_conflicts_json": json.dumps(sod_r),
        "single_holder_json": json.dumps(sh_r),
        "optimization_json": json.dumps(opt_r),
        "delivery_channel": "chat",
    }))
    assert result["status"] == "success"
    assert 0.0 < result["iam_risk_score"] <= 100.0


def test_full_pipeline_report_summary():
    sod_r, sh_r, opt_r = _run_full_pipeline()
    result = json.loads(report_generation_tool.invoke({
        "sod_conflicts_json": json.dumps(sod_r),
        "single_holder_json": json.dumps(sh_r),
        "optimization_json": json.dumps(opt_r),
    }))
    assert "IAM GOVERNANCE REPORT" in result["tabular_summary"]
    assert "IAM RISK SCORE" in result["tabular_summary"]


def test_full_pipeline_all_envs_in_distribution():
    sod_r, sh_r, opt_r = _run_full_pipeline()
    result = json.loads(report_generation_tool.invoke({
        "sod_conflicts_json": json.dumps(sod_r),
        "single_holder_json": json.dumps(sh_r),
        "optimization_json": json.dumps(opt_r),
    }))
    env_dist = result["report_payload"]["distributions"]["by_environment"]
    for env in ["S4_CLOUD","S4_ON_PREM","BTP","MULTI_TENANT"]:
        assert env in env_dist, f"Missing env: {env}"


def test_delivery_channel_recorded():
    _seed_small()
    result = json.loads(report_generation_tool.invoke({"delivery_channel":"email"}))
    assert result["report_payload"]["delivery_channel"] == "email"


def test_visual_charts_sections():
    sod_r, sh_r, opt_r = _run_full_pipeline()
    result = json.loads(report_generation_tool.invoke({
        "sod_conflicts_json": json.dumps(sod_r),
        "single_holder_json": json.dumps(sh_r),
        "optimization_json": json.dumps(opt_r),
    }))
    charts = result["visual_charts"]
    assert "SoD Conflicts" in charts
    assert "Single-Holder" in charts
    assert "Functional Category" in charts
    assert "Environment" in charts
