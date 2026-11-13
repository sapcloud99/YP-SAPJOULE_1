"""Tool for detecting single-holder critical roles (single point of failure)."""
import json
import logging
import os
from langchain_core.tools import tool
from role_discovery_tool import get_session_dataset

logger = logging.getLogger(__name__)

# Default criticality rules if no external file found
DEFAULT_CRITICALITY_RULES = [
    # ── High criticality ─────────────────────────────────────────────────────
    # Specific compound patterns must come BEFORE generic "admin" so that
    # e.g. "period_close_admin" doesn't get grabbed as High by "admin".
    {"pattern": "iam_governance",  "criticality": "High",   "reason": "IAM governance access"},
    {"pattern": "role_admin",      "criticality": "High",   "reason": "Role administration access"},
    {"pattern": "user_admin",      "criticality": "High",   "reason": "User administration access"},
    {"pattern": "auth_admin",      "criticality": "High",   "reason": "Authorization administration"},
    {"pattern": "security_admin",  "criticality": "High",   "reason": "Security administration"},
    {"pattern": "security",        "criticality": "High",   "reason": "Security administration"},
    {"pattern": "super_user",      "criticality": "High",   "reason": "Super user / emergency access"},
    {"pattern": "firefighter",     "criticality": "High",   "reason": "Emergency access"},
    {"pattern": "emergency_access","criticality": "High",   "reason": "Emergency bypass access"},
    {"pattern": "payment",         "criticality": "High",   "reason": "Financial payment execution"},
    {"pattern": "audit",           "criticality": "High",   "reason": "Audit and compliance access"},
    {"pattern": "client_admin",    "criticality": "High",   "reason": "SAP client administration"},
    {"pattern": "basis",           "criticality": "High",   "reason": "SAP Basis / system-level access"},
    # ── Medium criticality — MUST appear before generic "admin" ─────────────
    # Any role containing "admin" that hasn't matched the High patterns above
    # might still be Medium (e.g. period_close_ADMIN, vendor_master_ADMIN).
    {"pattern": "period_close",    "criticality": "Medium", "reason": "Period closing (financial)"},
    {"pattern": "fi_post",         "criticality": "Medium", "reason": "Financial posting"},
    {"pattern": "bank_master",     "criticality": "Medium", "reason": "Bank master data management"},
    {"pattern": "vendor_master",   "criticality": "Medium", "reason": "Vendor master data management"},
    {"pattern": "transport",       "criticality": "Medium", "reason": "Transport management"},
    {"pattern": "approve",         "criticality": "Medium", "reason": "Approval rights"},
    {"pattern": "manager",         "criticality": "Medium", "reason": "Manager-level approval rights"},
    # ── High catch-all — MUST be last among High patterns ───────────────────
    {"pattern": "admin",           "criticality": "High",   "reason": "Administrative access"},
]


def load_criticality_rules() -> list[dict]:
    """Load criticality rules from the skill reference file."""
    skill_path = os.path.join(
        os.path.dirname(__file__),
        "skills", "backup-recommendation", "references", "criticality-criteria.md"
    )
    # If the file exists but is markdown, we use default rules (structured JSON preferred)
    return DEFAULT_CRITICALITY_RULES


def get_criticality(role_name: str) -> tuple[str, str]:
    """Return (criticality, reason) for a role name."""
    rules = load_criticality_rules()
    role_lower = role_name.lower()
    for rule in rules:
        if rule["pattern"].lower() in role_lower:
            return rule["criticality"], rule["reason"]
    return "Low", "Standard business role"


@tool
def single_holder_detection_tool() -> str:
    """Identify all roles in the session dataset that are held by only one user (single point of failure).

    Returns all such roles sorted by criticality (High first), along with the current holder
    and the criticality classification with reasoning.
    """
    dataset = get_session_dataset()
    if not dataset:
        return json.dumps({
            "status": "error",
            "message": "Session dataset is empty. Run role_discovery_tool or file_ingestion_tool first.",
        })

    # Count holders per role per environment
    role_env_holders: dict[tuple, set] = {}
    for record in dataset:
        key = (record["role_name"], record["environment"])
        role_env_holders.setdefault(key, set()).add(record["user_id"])

    single_holder_roles = []
    for (role_name, environment), holders in role_env_holders.items():
        if len(holders) == 1:
            criticality, reason = get_criticality(role_name)
            single_holder_roles.append({
                "role_name": role_name,
                "environment": environment,
                "holder_count": 1,
                "current_holder": list(holders)[0],
                "criticality": criticality,
                "criticality_reason": reason,
                "risk_statement": (
                    f"Role '{role_name}' in {environment} has only one holder "
                    f"({list(holders)[0]}). Losing this user would remove all "
                    f"access to this capability ({reason})."
                ),
            })

    # Sort by criticality
    criticality_order = {"High": 0, "Medium": 1, "Low": 2}
    single_holder_roles.sort(key=lambda r: criticality_order.get(r["criticality"], 3))

    criticality_counts = {"High": 0, "Medium": 0, "Low": 0}
    for r in single_holder_roles:
        cl = r["criticality"]
        criticality_counts[cl] = criticality_counts.get(cl, 0) + 1

    return json.dumps({
        "status": "success",
        "total_single_holder_roles": len(single_holder_roles),
        "criticality_breakdown": criticality_counts,
        "single_holder_roles": single_holder_roles,
    })
