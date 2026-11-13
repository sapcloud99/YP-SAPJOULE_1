"""Unit tests for classify_roles_tool — full 32-user dataset."""
import json
import pytest

from role_discovery_tool import clear_session_dataset, merge_records, get_session_dataset
from classify_roles_tool import classify_roles_tool, classify_role_name, classify_user, CATEGORY_PATTERNS

ALL_USERS = {
    "USR001": ["BR_EMPLOYEE_SELF_SERVICE", "BR_MM_PURCHASING_USER"],
    "USR002": ["BR_EMPLOYEE_SELF_SERVICE", "BR_MANAGER_APPROVE", "BR_CO_COST_CENTER_MANAGER"],
    "USR003": ["BR_HR_PAYROLL_USER", "BR_EMPLOYEE_SELF_SERVICE"],
    "USR004": ["BR_SD_SALES_ORDER_PROCESS"],
    "USR005": ["BR_FI_ACCOUNTING_USER", "BR_CO_COST_CENTER_MANAGER"],
    "USR006": ["BR_PURCHASE_ORDER_CREATE", "BR_PURCHASE_ORDER_APPROVE", "BR_MM_PURCHASING_USER"],
    "USR007": ["BR_FI_POST_EXECUTE", "BR_PERIOD_CLOSE_ADMIN", "BR_FI_ACCOUNTING_USER"],
    "USR031": ["BR_VENDOR_MASTER_ADMIN", "BR_PAYMENT_PROCESS_EXECUTE"],
    "USR032": ["BR_FI_ACCOUNTING_USER", "BR_MM_PURCHASING_USER", "BR_MANAGER_APPROVE"],
    "USR008": ["BR_ABAP_DEVELOPER", "BR_ABAP_WORKBENCH"],
    "USR009": ["BR_ABAP_DEVELOPER", "BR_FIORI_DEVELOPER"],
    "USR010": ["BR_BTP_DEVELOPER", "BR_API_INTEGRATION"],
    "USR011": ["BR_MIDDLEWARE_DEVELOPER", "BR_API_INTEGRATION"],
    "USR012": ["BR_EXTENSION_DEVELOPER", "BR_BTP_DEVELOPER"],
    "USR013": ["BR_ABAP_DEVELOPER", "BR_ABAP_WORKBENCH", "BR_FIORI_DEVELOPER"],
    "USR014": ["BR_ADMIN", "BR_BASIS_OPS", "BR_TRANSPORT_MANAGER"],
    "USR015": ["BR_SYSADMIN_SUPPORT", "BR_RFC_DESTINATION_ADMIN", "BR_BATCH_ADMIN"],
    "USR016": ["BR_TRANSPORT_MANAGER", "BR_BASIS_OPS"],
    "USR017": ["BR_CLIENT_ADMIN", "BR_SYSADMIN_SUPPORT"],
    "USR018": ["BR_BATCH_ADMIN", "BR_BASIS_OPS"],
    "USR019": ["BR_BASIS_OPS", "BR_RFC_DESTINATION_ADMIN", "BR_ABAP_DEVELOPER", "BR_HELPDESK_AGENT", "BR_FI_ACCOUNTING_USER", "BR_EMPLOYEE_SELF_SERVICE"],
    "USR020": ["BR_HELPDESK_AGENT", "BR_INCIDENT_MANAGER"],
    "USR021": ["BR_SUPPORT_L2_SPECIALIST", "BR_HELPDESK_AGENT"],
    "USR022": ["BR_SUPPORT_L3_EXPERT", "BR_MONITORING_OPS"],
    "USR023": ["BR_MONITORING_OPS", "BR_INCIDENT_MANAGER"],
    "USR024": ["BR_SERVICE_DESK_AGENT", "BR_HELPDESK_AGENT"],
    "USR025": ["BR_SECURITY_ADMIN", "BR_AUTH_ADMIN"],
    "USR026": ["BR_IAM_GOVERNANCE_USER", "BR_USER_ADMIN"],
    "USR027": ["BR_GRC_ACCESS_CONTROL", "BR_COMPLIANCE_OFFICER"],
    "USR028": ["BR_AUDIT_LOG_VIEWER", "BR_COMPLIANCE_REVIEWER"],
    "USR029": ["BR_ROLE_ADMIN", "BR_SECURITY_AUDITOR", "BR_BUSINESS_ROLE_ASSIGN"],
    "USR030": ["BR_USER_ADMIN", "BR_AUDIT_LOG_VIEWER"],
}

EXPECTED_CATEGORIES = {
    "USR001":"Functional","USR002":"Functional","USR003":"Functional",
    "USR004":"Functional","USR005":"Functional","USR006":"Functional",
    "USR007":"Functional","USR031":"Functional","USR032":"Functional",
    "USR008":"Technical","USR009":"Technical","USR010":"Technical",
    "USR011":"Technical","USR012":"Technical","USR013":"Technical",
    "USR014":"Backend/Basis","USR015":"Backend/Basis","USR016":"Backend/Basis",
    "USR017":"Backend/Basis","USR018":"Backend/Basis",
    "USR020":"Support","USR021":"Support","USR022":"Support",
    "USR023":"Support","USR024":"Support",
    "USR025":"Security/Compliance","USR026":"Security/Compliance",
    "USR027":"Security/Compliance","USR028":"Security/Compliance",
    "USR029":"Security/Compliance","USR030":"Security/Compliance",
}


@pytest.fixture(autouse=True)
def reset_dataset():
    clear_session_dataset()
    yield
    clear_session_dataset()


def _seed_all_users(env="S4_CLOUD"):
    records = [
        {"user_id": uid, "role_name": role, "environment": env, "source": "test", "source_ref": f"{uid}/{role}"}
        for uid, roles in ALL_USERS.items()
        for role in roles
    ]
    merge_records(records)


@pytest.mark.parametrize("role,expected", [
    ("BR_EMPLOYEE_SELF_SERVICE","Functional"),("BR_MANAGER_APPROVE","Functional"),
    ("BR_FI_ACCOUNTING_USER","Functional"),("BR_HR_PAYROLL_USER","Functional"),
    ("BR_SD_SALES_ORDER_PROCESS","Functional"),("BR_PURCHASE_ORDER_CREATE","Functional"),
    ("BR_VENDOR_MASTER_ADMIN","Functional"),("BR_PAYMENT_PROCESS_EXECUTE","Functional"),
    ("BR_PERIOD_CLOSE_ADMIN","Functional"),("BR_FI_POST_EXECUTE","Functional"),
    ("BR_ABAP_DEVELOPER","Technical"),("BR_FIORI_DEVELOPER","Technical"),
    ("BR_BTP_DEVELOPER","Technical"),("BR_API_INTEGRATION","Technical"),
    ("BR_MIDDLEWARE_DEVELOPER","Technical"),("BR_EXTENSION_DEVELOPER","Technical"),
    ("BR_ADMIN","Backend/Basis"),("BR_BASIS_OPS","Backend/Basis"),
    ("BR_TRANSPORT_MANAGER","Backend/Basis"),("BR_CLIENT_ADMIN","Backend/Basis"),
    ("BR_RFC_DESTINATION_ADMIN","Backend/Basis"),("BR_BATCH_ADMIN","Backend/Basis"),
    ("BR_HELPDESK_AGENT","Support"),("BR_INCIDENT_MANAGER","Support"),
    ("BR_SUPPORT_L2_SPECIALIST","Support"),("BR_SUPPORT_L3_EXPERT","Support"),
    ("BR_MONITORING_OPS","Support"),("BR_SERVICE_DESK_AGENT","Support"),
    ("BR_SECURITY_ADMIN","Security/Compliance"),("BR_AUTH_ADMIN","Security/Compliance"),
    ("BR_AUDIT_LOG_VIEWER","Security/Compliance"),("BR_IAM_GOVERNANCE_USER","Security/Compliance"),
    ("BR_GRC_ACCESS_CONTROL","Security/Compliance"),("BR_ROLE_ADMIN","Security/Compliance"),
    ("BR_USER_ADMIN","Security/Compliance"),("BR_COMPLIANCE_OFFICER","Security/Compliance"),
])
def test_classify_role_name_all_roles(role, expected):
    assert classify_role_name(role) == expected, f"{role}: expected {expected}, got {classify_role_name(role)}"


def test_all_five_categories_in_patterns():
    assert set(CATEGORY_PATTERNS.keys()) == {"Functional","Technical","Backend/Basis","Support","Security/Compliance"}


def test_classify_user_pure_technical():
    assert classify_user(["BR_ABAP_DEVELOPER","BR_ABAP_WORKBENCH","BR_FIORI_DEVELOPER"])["primary_category"] == "Technical"


def test_classify_user_pure_security():
    assert classify_user(["BR_SECURITY_ADMIN","BR_AUTH_ADMIN"])["primary_category"] == "Security/Compliance"


def test_classify_user_pure_support():
    assert classify_user(["BR_HELPDESK_AGENT","BR_INCIDENT_MANAGER"])["primary_category"] == "Support"


def test_classify_user_pure_basis():
    assert classify_user(["BR_ADMIN","BR_BASIS_OPS","BR_TRANSPORT_MANAGER"])["primary_category"] == "Backend/Basis"


def test_classify_user_pure_functional():
    assert classify_user(["BR_EMPLOYEE_SELF_SERVICE","BR_MANAGER_APPROVE"])["primary_category"] == "Functional"


def test_classify_user_usr019_cross_functional():
    result = classify_user(["BR_BASIS_OPS","BR_RFC_DESTINATION_ADMIN","BR_ABAP_DEVELOPER","BR_HELPDESK_AGENT","BR_FI_ACCOUNTING_USER","BR_EMPLOYEE_SELF_SERVICE"])
    assert result["cross_functional"] is True
    assert len(result["all_categories"]) >= 2


def test_classify_user_empty_roles_defaults_functional():
    assert classify_user([])["primary_category"] == "Functional"


def test_classify_all_32_users_correct_categories():
    _seed_all_users()
    result = json.loads(classify_roles_tool.invoke({}))
    assert result["status"] == "success"
    assert result["users_classified"] == 32
    classified = {u["user_id"]: u["primary_category"] for u in result["classified_users"]}
    misclassified = [f"{uid}: expected={exp}, got={classified.get(uid)}"
                     for uid, exp in EXPECTED_CATEGORIES.items() if classified.get(uid) != exp]
    assert not misclassified, "Misclassified:\n" + "\n".join(misclassified)


def test_classify_all_five_categories_populated():
    _seed_all_users()
    result = json.loads(classify_roles_tool.invoke({}))
    cats = set(result["categories"].keys())
    for cat in ["Functional","Technical","Backend/Basis","Support","Security/Compliance"]:
        assert cat in cats


def test_classify_usr019_flagged_cross_functional():
    _seed_all_users()
    result = json.loads(classify_roles_tool.invoke({}))
    usr019 = next(u for u in result["classified_users"] if u["user_id"] == "USR019")
    assert usr019["cross_functional"] is True


def test_classify_functional_count():
    _seed_all_users()
    result = json.loads(classify_roles_tool.invoke({}))
    assert result["categories"].get("Functional", 0) >= 7


def test_classify_security_count():
    _seed_all_users()
    result = json.loads(classify_roles_tool.invoke({}))
    assert result["categories"].get("Security/Compliance", 0) >= 6


def test_classify_technical_count():
    _seed_all_users()
    result = json.loads(classify_roles_tool.invoke({}))
    assert result["categories"].get("Technical", 0) >= 6


def test_classify_basis_count():
    _seed_all_users()
    result = json.loads(classify_roles_tool.invoke({}))
    assert result["categories"].get("Backend/Basis", 0) >= 5


def test_classify_support_count():
    _seed_all_users()
    result = json.loads(classify_roles_tool.invoke({}))
    assert result["categories"].get("Support", 0) >= 5


def test_classify_session_records_updated_with_category():
    _seed_all_users()
    classify_roles_tool.invoke({})
    assert any("functional_category" in r for r in get_session_dataset())


def test_classify_empty_dataset_returns_error():
    result = json.loads(classify_roles_tool.invoke({}))
    assert result["status"] == "error"


def test_classify_confidence_below_threshold_flagged_for_review():
    _seed_all_users()
    result = json.loads(classify_roles_tool.invoke({"confidence_threshold": 0.9}))
    assert "USR019" in result.get("needs_review_users", [])
