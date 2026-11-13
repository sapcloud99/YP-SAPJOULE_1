"""Integration test: full IAM governance pipeline with 32-user dataset."""
import json
import pytest
from unittest.mock import AsyncMock

from role_discovery_tool import clear_session_dataset, get_session_dataset
from classify_roles_tool import classify_roles_tool
from sod_detection_tool import sod_detection_tool
from single_holder_detection_tool import single_holder_detection_tool
from backup_recommendation_tool import backup_recommendation_tool
from role_optimization_tool import role_optimization_tool
from report_generation_tool import report_generation_tool
from file_ingestion_tool import file_ingestion_tool
from scim_user_tool import create_scim_user_tool

FULL_CSV = """\
user_id,role_name,environment,functional_type
USR001,BR_EMPLOYEE_SELF_SERVICE,S4_CLOUD,Functional
USR001,BR_MM_PURCHASING_USER,S4_CLOUD,Functional
USR002,BR_EMPLOYEE_SELF_SERVICE,S4_CLOUD,Functional
USR002,BR_MANAGER_APPROVE,S4_CLOUD,Functional
USR002,BR_CO_COST_CENTER_MANAGER,S4_CLOUD,Functional
USR003,BR_HR_PAYROLL_USER,S4_CLOUD,Functional
USR003,BR_EMPLOYEE_SELF_SERVICE,S4_CLOUD,Functional
USR004,BR_SD_SALES_ORDER_PROCESS,S4_CLOUD,Functional
USR005,BR_FI_ACCOUNTING_USER,S4_CLOUD,Functional
USR005,BR_CO_COST_CENTER_MANAGER,S4_CLOUD,Functional
USR006,BR_PURCHASE_ORDER_CREATE,S4_CLOUD,Functional
USR006,BR_PURCHASE_ORDER_APPROVE,S4_CLOUD,Functional
USR006,BR_MM_PURCHASING_USER,S4_CLOUD,Functional
USR007,BR_FI_POST_EXECUTE,S4_ON_PREM,Functional
USR007,BR_PERIOD_CLOSE_ADMIN,S4_ON_PREM,Functional
USR007,BR_FI_ACCOUNTING_USER,S4_ON_PREM,Functional
USR008,BR_ABAP_DEVELOPER,BTP,Technical
USR008,BR_ABAP_WORKBENCH,BTP,Technical
USR009,BR_ABAP_DEVELOPER,BTP,Technical
USR009,BR_FIORI_DEVELOPER,BTP,Technical
USR010,BR_BTP_DEVELOPER,BTP,Technical
USR010,BR_API_INTEGRATION,BTP,Technical
USR011,BR_MIDDLEWARE_DEVELOPER,BTP,Technical
USR011,BR_API_INTEGRATION,BTP,Technical
USR012,BR_EXTENSION_DEVELOPER,BTP,Technical
USR012,BR_BTP_DEVELOPER,BTP,Technical
USR013,BR_ABAP_DEVELOPER,BTP,Technical
USR013,BR_ABAP_WORKBENCH,BTP,Technical
USR013,BR_FIORI_DEVELOPER,BTP,Technical
USR014,BR_ADMIN,S4_ON_PREM,Backend/Basis
USR014,BR_BASIS_OPS,S4_ON_PREM,Backend/Basis
USR014,BR_TRANSPORT_MANAGER,S4_ON_PREM,Backend/Basis
USR015,BR_SYSADMIN_SUPPORT,S4_ON_PREM,Backend/Basis
USR015,BR_RFC_DESTINATION_ADMIN,S4_ON_PREM,Backend/Basis
USR015,BR_BATCH_ADMIN,S4_ON_PREM,Backend/Basis
USR016,BR_TRANSPORT_MANAGER,S4_ON_PREM,Backend/Basis
USR016,BR_BASIS_OPS,S4_ON_PREM,Backend/Basis
USR017,BR_CLIENT_ADMIN,S4_ON_PREM,Backend/Basis
USR017,BR_SYSADMIN_SUPPORT,S4_ON_PREM,Backend/Basis
USR018,BR_BATCH_ADMIN,S4_ON_PREM,Backend/Basis
USR018,BR_BASIS_OPS,S4_ON_PREM,Backend/Basis
USR019,BR_BASIS_OPS,MULTI_TENANT,Backend/Basis
USR019,BR_RFC_DESTINATION_ADMIN,MULTI_TENANT,Backend/Basis
USR019,BR_ABAP_DEVELOPER,MULTI_TENANT,Technical
USR019,BR_HELPDESK_AGENT,MULTI_TENANT,Support
USR019,BR_FI_ACCOUNTING_USER,MULTI_TENANT,Functional
USR019,BR_EMPLOYEE_SELF_SERVICE,MULTI_TENANT,Functional
USR020,BR_HELPDESK_AGENT,BTP,Support
USR020,BR_INCIDENT_MANAGER,BTP,Support
USR021,BR_SUPPORT_L2_SPECIALIST,BTP,Support
USR021,BR_HELPDESK_AGENT,BTP,Support
USR022,BR_SUPPORT_L3_EXPERT,BTP,Support
USR022,BR_MONITORING_OPS,BTP,Support
USR023,BR_MONITORING_OPS,BTP,Support
USR023,BR_INCIDENT_MANAGER,BTP,Support
USR024,BR_SERVICE_DESK_AGENT,BTP,Support
USR024,BR_HELPDESK_AGENT,BTP,Support
USR025,BR_SECURITY_ADMIN,S4_ON_PREM,Security/Compliance
USR025,BR_AUTH_ADMIN,S4_ON_PREM,Security/Compliance
USR026,BR_IAM_GOVERNANCE_USER,S4_CLOUD,Security/Compliance
USR026,BR_USER_ADMIN,S4_CLOUD,Security/Compliance
USR027,BR_GRC_ACCESS_CONTROL,S4_CLOUD,Security/Compliance
USR027,BR_COMPLIANCE_OFFICER,S4_CLOUD,Security/Compliance
USR028,BR_AUDIT_LOG_VIEWER,S4_CLOUD,Security/Compliance
USR028,BR_COMPLIANCE_REVIEWER,S4_CLOUD,Security/Compliance
USR029,BR_ROLE_ADMIN,S4_CLOUD,Security/Compliance
USR029,BR_SECURITY_AUDITOR,S4_CLOUD,Security/Compliance
USR029,BR_BUSINESS_ROLE_ASSIGN,S4_CLOUD,Security/Compliance
USR030,BR_USER_ADMIN,S4_CLOUD,Security/Compliance
USR030,BR_AUDIT_LOG_VIEWER,S4_CLOUD,Security/Compliance
USR031,BR_VENDOR_MASTER_ADMIN,BTP,Functional
USR031,BR_PAYMENT_PROCESS_EXECUTE,BTP,Functional
USR032,BR_FI_ACCOUNTING_USER,S4_CLOUD,Functional
USR032,BR_MM_PURCHASING_USER,S4_CLOUD,Functional
USR032,BR_MANAGER_APPROVE,S4_CLOUD,Functional
"""


@pytest.fixture(autouse=True)
def reset_dataset():
    clear_session_dataset()
    yield
    clear_session_dataset()


@pytest.mark.asyncio
async def test_full_32_user_pipeline():
    # Step 1: Ingest
    ingest = json.loads(file_ingestion_tool.invoke({"file_content": FULL_CSV, "file_format": "csv"}))
    assert ingest["status"] == "success"
    assert ingest["records_added"] >= 70
    assert len(get_session_dataset()) >= 70

    # Step 2: Classify
    classify_r = json.loads(classify_roles_tool.invoke({}))
    assert classify_r["status"] == "success"
    assert classify_r["users_classified"] == 32
    cats = classify_r["categories"]
    assert cats.get("Functional",0) >= 7
    assert cats.get("Technical",0) >= 5
    assert cats.get("Backend/Basis",0) >= 4
    assert cats.get("Support",0) >= 4
    assert cats.get("Security/Compliance",0) >= 5

    # Step 3: SoD
    sod_r = json.loads(sod_detection_tool.invoke({}))
    assert sod_r["status"] == "success"
    assert sod_r["total_conflicts"] >= 4
    conflicted = {c["user_id"] for c in sod_r["conflicts"]}
    assert "USR006" in conflicted
    assert "USR007" in conflicted
    assert "USR031" in conflicted

    # Step 4: Single-holder
    sh_r = json.loads(single_holder_detection_tool.invoke({}))
    assert sh_r["status"] == "success"
    assert sh_r["total_single_holder_roles"] >= 5
    high_sh = {r["role_name"] for r in sh_r["single_holder_roles"] if r["criticality"]=="High"}
    assert "BR_ADMIN" in high_sh
    assert "BR_SECURITY_ADMIN" in high_sh

    # Step 5: Backup for 3 critical single-holder roles
    for sh_role in [r for r in sh_r["single_holder_roles"] if r["criticality"]=="High"][:3]:
        backup_r = json.loads(backup_recommendation_tool.invoke({
            "role_name": sh_role["role_name"],
            "environment": sh_role["environment"],
            "max_candidates": 3,
        }))
        assert backup_r["status"] in ("success","no_candidates")
        if backup_r["status"] == "success":
            for s in backup_r["access_request_summaries"]:
                assert s["requires_human_approval"] is True

    # Step 6: Optimization
    opt_r = json.loads(role_optimization_tool.invoke({}))
    assert opt_r["status"] == "success"
    assert opt_r["total_users_analyzed"] == 32
    assert "USR019" in {u["user_id"] for u in opt_r["over_privileged_users"]}
    assert "USR004" in {u["user_id"] for u in opt_r["under_privileged_users"]}

    # Step 7: Report
    report_r = json.loads(report_generation_tool.invoke({
        "sod_conflicts_json": json.dumps(sod_r),
        "single_holder_json": json.dumps(sh_r),
        "optimization_json": json.dumps(opt_r),
        "delivery_channel": "chat",
    }))
    assert report_r["status"] == "success"
    assert 0.0 < report_r["iam_risk_score"] <= 100.0
    assert "IAM GOVERNANCE REPORT" in report_r["tabular_summary"]
    payload = report_r["report_payload"]
    assert payload["metrics"]["total_users"] == 32
    assert payload["metrics"]["sod_conflicts"] >= 4
    for env in ["S4_CLOUD","S4_ON_PREM","BTP","MULTI_TENANT"]:
        assert env in payload["distributions"]["by_environment"]


@pytest.mark.asyncio
async def test_multi_environment_via_scim():
    mock_scim = AsyncMock()
    mock_scim.name = "getAllUsersUsingGET"
    mock_scim.ainvoke = AsyncMock(return_value={"Resources": [
        {"id":"USR014","displayName":"John","groups":[{"display":"BR_ADMIN"}]},
        {"id":"USR025","displayName":"Jack","groups":[{"display":"BR_SECURITY_ADMIN"}]},
    ]})
    tool = create_scim_user_tool([mock_scim])
    for env in ["S4_CLOUD","S4_ON_PREM","BTP","MULTI_TENANT"]:
        await tool.ainvoke({"environment": env})
    ds = get_session_dataset()
    assert {r["environment"] for r in ds} == {"S4_CLOUD","S4_ON_PREM","BTP","MULTI_TENANT"}
    assert len(ds) == 8  # 2 users × 4 envs


@pytest.mark.asyncio
async def test_csv_plus_scim_combined():
    csv = "user_id,role_name,environment\nUSR014,BR_ADMIN,S4_ON_PREM\nUSR015,BR_SYSADMIN_SUPPORT,S4_ON_PREM\n"
    json.loads(file_ingestion_tool.invoke({"file_content": csv, "file_format": "csv"}))
    mock_scim = AsyncMock()
    mock_scim.name = "getAllUsersUsingGET"
    mock_scim.ainvoke = AsyncMock(return_value={"Resources": [
        {"id":"USR014","displayName":"John","groups":[{"display":"BR_BASIS_OPS"}]},
        {"id":"USR016","displayName":"Leo","groups":[{"display":"BR_TRANSPORT_MANAGER"}]},
    ]})
    await create_scim_user_tool([mock_scim]).ainvoke({"environment": "BTP"})
    ds = get_session_dataset()
    assert len(ds) == 4
    envs = {r["environment"] for r in ds}
    assert "S4_ON_PREM" in envs and "BTP" in envs
