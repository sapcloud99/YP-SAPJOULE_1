"""Tool for classifying SAP roles and users by functional category."""
# pylint: disable=import-error
import json
import logging
from langchain_core.tools import tool
from role_discovery_tool import get_session_dataset  # type: ignore[import]

logger = logging.getLogger(__name__)

# Keyword patterns per functional category (role name matching).
# Categories are checked in this exact order — FIRST match wins.
CATEGORY_PATTERNS = {
    # 1. Security/Compliance — specific "admin" roles must be listed here explicitly
    #    so they don't fall into Backend/Basis's generic "admin" catch-all.
    "Security/Compliance": [
        "user_admin",          # BR_USER_ADMIN
        "role_admin",          # BR_ROLE_ADMIN
        "auth_admin",          # BR_AUTH_ADMIN
        "security_admin",      # BR_SECURITY_ADMIN
        "security_auditor",    # BR_SECURITY_AUDITOR
        "iam_governance",      # BR_IAM_GOVERNANCE_USER
        "grc_",                # BR_GRC_ACCESS_CONTROL
        "compliance",          # BR_COMPLIANCE_OFFICER, BR_COMPLIANCE_REVIEWER
        "audit_log",           # BR_AUDIT_LOG_VIEWER
        "access_control",      # generic access control
        "business_role_assign",# BR_BUSINESS_ROLE_ASSIGN
    ],
    # 2. Functional — finance, procurement, HR, sales roles.
    #    Listed BEFORE Backend/Basis to prevent "vendor_master_ADMIN",
    #    "purchase_order", "fi_post_execute", "period_close_admin" being
    #    swallowed by the generic "admin" pattern in Backend/Basis.
    "Functional": [
        "purchase_order",      # BR_PURCHASE_ORDER_CREATE/APPROVE
        "purchasing_user",     # BR_MM_PURCHASING_USER
        "vendor_master",       # BR_VENDOR_MASTER_ADMIN
        "payment_process",     # BR_PAYMENT_PROCESS_EXECUTE
        "period_close",        # BR_PERIOD_CLOSE_ADMIN (Finance)
        "fi_post",             # BR_FI_POST_EXECUTE
        "fi_accounting",       # BR_FI_ACCOUNTING_USER
        "cost_center_manager", # BR_CO_COST_CENTER_MANAGER
        "manager_approve",     # BR_MANAGER_APPROVE
        "payroll",             # BR_HR_PAYROLL_USER
        "sales_order",         # BR_SD_SALES_ORDER_PROCESS
        "employee_self",       # BR_EMPLOYEE_SELF_SERVICE
        "employee",            # generic employee
        "self_service",        # generic self-service
        "approver",            # generic approver role
        "fi_",                 # FI module roles
        "co_",                 # CO module roles
        "mm_",                 # MM module roles
        "sd_",                 # SD module roles
        "hr_",                 # HR module roles
    ],
    # 3. Backend/Basis — system-level admin roles.
    #    "admin" here only matches roles NOT already caught by Sec/Compliance
    #    or Functional above (e.g. BR_ADMIN, BR_SYSADMIN_SUPPORT, BR_CLIENT_ADMIN).
    "Backend/Basis": [
        "basis",               # BR_BASIS_OPS
        "sysadmin",            # BR_SYSADMIN_SUPPORT
        "system_admin",        # generic system admin
        "transport",           # BR_TRANSPORT_MANAGER
        "client_admin",        # BR_CLIENT_ADMIN
        "rfc_destination",     # BR_RFC_DESTINATION_ADMIN
        "batch_admin",         # BR_BATCH_ADMIN
        "batch",               # generic batch
        "netweaver",           # SAP NetWeaver
        "abap_admin",          # ABAP admin
        "admin",               # catch-all: BR_ADMIN, remaining *_ADMIN roles
    ],
    # 4. Technical — developers and integration specialists.
    "Technical": [
        "abap_developer",      # BR_ABAP_DEVELOPER
        "abap_workbench",      # BR_ABAP_WORKBENCH
        "fiori_developer",     # BR_FIORI_DEVELOPER
        "btp_developer",       # BR_BTP_DEVELOPER
        "api_integration",     # BR_API_INTEGRATION
        "middleware_developer",# BR_MIDDLEWARE_DEVELOPER
        "extension_developer", # BR_EXTENSION_DEVELOPER
        "developer",           # generic developer
        "abap",                # generic ABAP
        "api",                 # generic API
        "integration",         # generic integration
        "middleware",          # generic middleware
        "extension",           # generic extension
        "btp",                 # SAP BTP roles
    ],
    # 5. Support — helpdesk and operational support (checked last).
    "Support": [
        "helpdesk",            # BR_HELPDESK_AGENT
        "service_desk",        # BR_SERVICE_DESK_AGENT
        "incident_manager",    # BR_INCIDENT_MANAGER
        "l2_specialist",       # BR_SUPPORT_L2_SPECIALIST
        "l3_expert",           # BR_SUPPORT_L3_EXPERT
        "monitoring_ops",      # BR_MONITORING_OPS
        "support",             # generic support
        "incident",            # generic incident
        "monitoring",          # generic monitoring
        "operations",          # generic ops
    ],
}


def classify_role_name(role_name: str) -> str:
    """Classify a single role name to a functional category."""
    role_lower = role_name.lower()
    for category, patterns in CATEGORY_PATTERNS.items():
        for pattern in patterns:
            if pattern in role_lower:
                return category
    return "Functional"  # Default category


def classify_user(user_roles: list[str]) -> dict:
    """Classify a user based on their full role portfolio."""
    category_hits: dict[str, int] = {}
    for role in user_roles:
        cat = classify_role_name(role)
        category_hits[cat] = category_hits.get(cat, 0) + 1

    if not category_hits:
        return {
            "primary_category": "Functional",
            "all_categories": ["Functional"],
            "cross_functional": False,
            "category_distribution": {},
        }

    sorted_cats = sorted(category_hits, key=lambda c: category_hits[c], reverse=True)
    primary = sorted_cats[0]
    cross_functional = len(sorted_cats) > 1

    return {
        "primary_category": primary,
        "all_categories": sorted_cats,
        "cross_functional": cross_functional,
        "category_distribution": category_hits,
    }


@tool
def classify_roles_tool(confidence_threshold: float = 0.7) -> str:
    """Classify all users in the session dataset by functional category.

    Args:
        confidence_threshold: Minimum confidence ratio to assign a category without
            flagging for review (0.0–1.0). Default 0.7.
    """
    dataset = get_session_dataset()
    if not dataset:
        return json.dumps({
            "status": "error",
            "message": "Session dataset is empty. Run role_discovery_tool or file_ingestion_tool first.",
        })

    user_roles: dict[str, list[str]] = {}
    for record in dataset:
        uid = record["user_id"]
        user_roles.setdefault(uid, []).append(record["role_name"])

    classified_users = []
    needs_review = []

    for user_id, roles in user_roles.items():
        result = classify_user(roles)
        total_roles = len(roles)
        top_category_count = result["category_distribution"].get(result["primary_category"], 0)
        confidence = top_category_count / total_roles if total_roles > 0 else 0.0

        entry = {
            "user_id": user_id,
            "primary_category": result["primary_category"],
            "all_categories": result["all_categories"],
            "cross_functional": result["cross_functional"],
            "confidence": round(confidence, 2),
            "total_roles": total_roles,
        }

        if confidence < confidence_threshold:
            entry["review_required"] = True
            entry["review_reason"] = (
                f"Classification confidence {confidence:.0%} is below "
                f"threshold {confidence_threshold:.0%}"
            )
            needs_review.append(user_id)
        else:
            entry["review_required"] = False

        classified_users.append(entry)

        for record in dataset:
            if record["user_id"] == user_id:
                record["functional_category"] = result["primary_category"]
                record["cross_functional"] = result["cross_functional"]

    category_counts: dict[str, int] = {}
    for u in classified_users:
        cat = u["primary_category"]
        category_counts[cat] = category_counts.get(cat, 0) + 1

    return json.dumps({
        "status": "success",
        "users_classified": len(classified_users),
        "categories": category_counts,
        "needs_review_count": len(needs_review),
        "needs_review_users": needs_review,
        "classified_users": classified_users,
    })
