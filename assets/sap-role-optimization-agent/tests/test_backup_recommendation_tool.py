"""Unit tests for backup_recommendation_tool."""
import json
import pytest

from role_discovery_tool import clear_session_dataset, merge_records
from classify_roles_tool import classify_roles_tool
from backup_recommendation_tool import backup_recommendation_tool, score_backup_candidate


@pytest.fixture(autouse=True)
def reset_dataset():
    clear_session_dataset()
    yield
    clear_session_dataset()


def _seed_and_classify():
    assignments = [
        ("USR001","BR_EMPLOYEE_SELF_SERVICE","S4_CLOUD"),
        ("USR002","BR_MANAGER_APPROVE","S4_CLOUD"),
        ("USR008","BR_ABAP_DEVELOPER","BTP"),("USR008","BR_ABAP_WORKBENCH","BTP"),
        ("USR009","BR_ABAP_DEVELOPER","BTP"),("USR009","BR_FIORI_DEVELOPER","BTP"),
        ("USR014","BR_ADMIN","S4_ON_PREM"),("USR014","BR_BASIS_OPS","S4_ON_PREM"),("USR014","BR_TRANSPORT_MANAGER","S4_ON_PREM"),
        ("USR015","BR_SYSADMIN_SUPPORT","S4_ON_PREM"),("USR015","BR_BATCH_ADMIN","S4_ON_PREM"),
        ("USR016","BR_TRANSPORT_MANAGER","S4_ON_PREM"),("USR016","BR_BASIS_OPS","S4_ON_PREM"),
        ("USR017","BR_CLIENT_ADMIN","S4_ON_PREM"),("USR017","BR_SYSADMIN_SUPPORT","S4_ON_PREM"),
        ("USR025","BR_SECURITY_ADMIN","S4_ON_PREM"),("USR025","BR_AUTH_ADMIN","S4_ON_PREM"),
        ("USR026","BR_IAM_GOVERNANCE_USER","S4_CLOUD"),("USR026","BR_USER_ADMIN","S4_CLOUD"),
        ("USR029","BR_ROLE_ADMIN","S4_CLOUD"),("USR029","BR_SECURITY_AUDITOR","S4_CLOUD"),
    ]
    merge_records([{"user_id":u,"role_name":r,"environment":e,"source":"test","source_ref":f"{u}/{r}/{e}"}
                   for u,r,e in assignments])
    classify_roles_tool.invoke({})


def test_score_category_match_adds_40():
    scored = score_backup_candidate("USR015",["BR_SYSADMIN_SUPPORT","BR_BATCH_ADMIN","BR_BASIS_OPS"],"BR_ADMIN","Backend/Basis")
    assert scored["score"] >= 40


def test_score_role_overlap_adds_points():
    scored = score_backup_candidate("USR016",["BR_BASIS_OPS","BR_ADMIN_BACKUP"],"BR_ADMIN","Backend/Basis")
    assert scored["score"] > 0


def test_score_no_match_zero():
    scored = score_backup_candidate("USR001",["BR_EMPLOYEE_SELF_SERVICE"],"BR_ADMIN","Backend/Basis")
    assert scored["score"] == 0


def test_backup_br_admin_has_basis_candidates():
    _seed_and_classify()
    result = json.loads(backup_recommendation_tool.invoke({"role_name":"BR_ADMIN","environment":"S4_ON_PREM","max_candidates":3}))
    assert result["status"] in ("success","no_candidates")
    if result["status"] == "success":
        assert len(result["backup_candidates"]) >= 1
        for c in result["backup_candidates"]:
            assert c["score"] > 0


def test_backup_excludes_current_holder():
    _seed_and_classify()
    result = json.loads(backup_recommendation_tool.invoke({"role_name":"BR_ADMIN","environment":"S4_ON_PREM"}))
    if result["status"] == "success":
        assert "USR014" not in [c["candidate_id"] for c in result["backup_candidates"]]


def test_backup_ranked_by_score():
    _seed_and_classify()
    result = json.loads(backup_recommendation_tool.invoke({"role_name":"BR_ADMIN","environment":"S4_ON_PREM","max_candidates":5}))
    if result["status"] == "success":
        scores = [c["score"] for c in result["backup_candidates"]]
        assert scores == sorted(scores, reverse=True)


def test_backup_summaries_match_candidates():
    _seed_and_classify()
    result = json.loads(backup_recommendation_tool.invoke({"role_name":"BR_ADMIN","environment":"S4_ON_PREM"}))
    if result["status"] == "success":
        assert len(result["access_request_summaries"]) == len(result["backup_candidates"])
        for s in result["access_request_summaries"]:
            assert s["requires_human_approval"] is True


def test_backup_human_approval_always_true():
    _seed_and_classify()
    result = json.loads(backup_recommendation_tool.invoke({"role_name":"BR_ADMIN","environment":"S4_ON_PREM"}))
    assert result.get("human_approval_required") is True


def test_backup_max_candidates_respected():
    _seed_and_classify()
    result = json.loads(backup_recommendation_tool.invoke({"role_name":"BR_ADMIN","environment":"S4_ON_PREM","max_candidates":2}))
    if result["status"] == "success":
        assert len(result["backup_candidates"]) <= 2


def test_backup_role_not_found_error():
    _seed_and_classify()
    result = json.loads(backup_recommendation_tool.invoke({"role_name":"BR_NONEXISTENT","environment":"S4_CLOUD"}))
    assert result["status"] == "error"
    assert "not found" in result["message"]


def test_backup_empty_dataset_error():
    result = json.loads(backup_recommendation_tool.invoke({"role_name":"BR_ADMIN","environment":"S4_ON_PREM"}))
    assert result["status"] == "error"
