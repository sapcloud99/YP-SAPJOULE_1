"""Tool for detecting Segregation of Duties (SoD) conflicts."""
import json
import logging
import os
from langchain_core.tools import tool
from role_discovery_tool import get_session_dataset

logger = logging.getLogger(__name__)

# Default built-in SoD rules if no external rule file is found
DEFAULT_SOD_RULES = [
    {
        "rule_id": "SOD-001",
        "description": "Create and Approve Purchase Orders",
        "role_a_pattern": "purchase_order_create",
        "role_b_pattern": "purchase_order_approve",
        "risk_level": "High",
        "mitigation": "Assign approval role to a different user. Use workflow-based approval.",
    },
    {
        "rule_id": "SOD-002",
        "description": "Vendor Master Maintenance and Payment Processing",
        "role_a_pattern": "vendor_master",
        "role_b_pattern": "payment_process",
        "risk_level": "High",
        "mitigation": "Separate vendor management from payment execution responsibilities.",
    },
    {
        "rule_id": "SOD-003",
        "description": "User Administration and Audit Log Access",
        "role_a_pattern": "user_admin",
        "role_b_pattern": "audit_log",
        "risk_level": "High",
        "mitigation": "Restrict audit log access to a separate security/compliance role.",
    },
    {
        "rule_id": "SOD-004",
        "description": "Role Administration and Business Role Assignment",
        "role_a_pattern": "role_admin",
        "role_b_pattern": "business_role_assign",
        "risk_level": "Medium",
        "mitigation": "Ensure role administrators cannot assign roles to themselves.",
    },
    {
        "rule_id": "SOD-005",
        "description": "Financial Posting and Period Closing",
        "role_a_pattern": "fi_post",
        "role_b_pattern": "period_close",
        "risk_level": "Medium",
        "mitigation": "Period closing should be performed by a finance controller, not the posting user.",
    },
]

SOD_CONFLICT_THRESHOLD = int(os.environ.get("SOD_CONFLICT_THRESHOLD", "50"))


def load_sod_rules() -> list[dict]:
    """Load SoD rules from the skill reference file, falling back to defaults."""
    skill_path = os.path.join(
        os.path.dirname(__file__),
        "skills", "sod-detection", "references", "sod-rule-template.json"
    )
    if os.path.exists(skill_path):
        try:
            with open(skill_path) as f:
                rules = json.load(f)
                if isinstance(rules, list) and rules:
                    return rules
        except Exception as e:
            logger.warning("Could not load SoD rules from %s: %s", skill_path, e)
    return DEFAULT_SOD_RULES


def roles_match_pattern(role_name: str, pattern: str) -> bool:
    """Check if a role name matches a pattern (substring, case-insensitive)."""
    return pattern.lower() in role_name.lower()


@tool
def sod_detection_tool() -> str:
    """Detect Segregation of Duties conflicts in the current session role dataset.

    Scans all user-role assignments and flags conflicting role combinations
    based on the configured SoD rule library. Auto-triggers report generation
    if conflicts exceed the configured threshold.
    """
    dataset = get_session_dataset()
    if not dataset:
        return json.dumps({
            "status": "error",
            "message": "Session dataset is empty. Run role_discovery_tool or file_ingestion_tool first.",
        })

    rules = load_sod_rules()

    # Group roles by user+environment
    user_env_roles: dict[tuple, list[str]] = {}
    for record in dataset:
        key = (record["user_id"], record["environment"])
        user_env_roles.setdefault(key, []).append(record["role_name"])

    conflicts = []
    for (user_id, environment), roles in user_env_roles.items():
        for rule in rules:
            pattern_a = rule.get("role_a_pattern", "")
            pattern_b = rule.get("role_b_pattern", "")
            roles_with_a = [r for r in roles if roles_match_pattern(r, pattern_a)]
            roles_with_b = [r for r in roles if roles_match_pattern(r, pattern_b)]
            if roles_with_a and roles_with_b:
                conflicts.append({
                    "user_id": user_id,
                    "environment": environment,
                    "rule_id": rule["rule_id"],
                    "description": rule["description"],
                    "conflicting_role_a": roles_with_a[0],
                    "conflicting_role_b": roles_with_b[0],
                    "risk_level": rule.get("risk_level", "Medium"),
                    "mitigation": rule.get("mitigation", ""),
                })

    # Sort by risk level
    risk_order = {"High": 0, "Medium": 1, "Low": 2}
    conflicts.sort(key=lambda c: risk_order.get(c["risk_level"], 3))

    risk_counts = {"High": 0, "Medium": 0, "Low": 0}
    for c in conflicts:
        rl = c["risk_level"]
        risk_counts[rl] = risk_counts.get(rl, 0) + 1

    result = {
        "status": "success",
        "total_conflicts": len(conflicts),
        "risk_breakdown": risk_counts,
        "conflicts": conflicts,
        "auto_report_triggered": len(conflicts) > SOD_CONFLICT_THRESHOLD,
    }

    if len(conflicts) > SOD_CONFLICT_THRESHOLD:
        result["message"] = (
            f"Conflict count ({len(conflicts)}) exceeds threshold ({SOD_CONFLICT_THRESHOLD}). "
            "Statistical report auto-generation recommended."
        )

    return json.dumps(result)
