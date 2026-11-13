"""Tool for identifying over- and under-privileged users."""
# pylint: disable=import-error
import json
import logging
from langchain_core.tools import tool
from role_discovery_tool import get_session_dataset  # type: ignore[import]
from classify_roles_tool import CATEGORY_PATTERNS, classify_user  # type: ignore[import]

logger = logging.getLogger(__name__)

# Expected role patterns per functional category (minimum expected roles)
EXPECTED_ROLES_BY_CATEGORY = {
    "Functional": ["employee", "self_service", "manager", "approver"],
    "Technical": ["developer", "development", "fiori_dev", "api"],
    "Backend/Basis": ["admin", "basis", "transport", "rfc"],
    "Support": ["helpdesk", "support", "incident", "monitoring"],
    "Security/Compliance": ["audit", "security", "compliance", "role_admin"],
}

# Max reasonable roles per category before being considered over-privileged
MAX_ROLES_BY_CATEGORY = {
    "Functional": 5,
    "Technical": 8,
    "Backend/Basis": 10,
    "Support": 5,
    "Security/Compliance": 6,
}


def find_matching_roles(roles: list[str], patterns: list[str]) -> list[str]:
    """Find roles that match any of the given patterns."""
    matched = []
    for role in roles:
        role_lower = role.lower()
        for p in patterns:
            if p.lower() in role_lower:
                matched.append(role)
                break
    return matched


def find_excess_roles(roles: list[str], category: str) -> list[str]:
    """Find roles that don't belong to the user's primary category."""
    category_patterns = CATEGORY_PATTERNS.get(category, [])
    excess = []
    for role in roles:
        role_lower = role.lower()
        matched_to_own_category = any(p in role_lower for p in category_patterns)
        if not matched_to_own_category and role != "NO_ROLE_ASSIGNED":
            # Check if this role belongs to a stricter category
            for cat, patterns in CATEGORY_PATTERNS.items():
                if cat != category and any(p in role_lower for p in patterns):
                    excess.append(role)
                    break
    return excess


@tool
def role_optimization_tool() -> str:
    """Identify over-privileged and under-privileged users in the session dataset.

    Compares each user's current roles against the expected role set for their
    functional category and returns actionable optimization recommendations.
    """
    dataset = get_session_dataset()
    if not dataset:
        return json.dumps({
            "status": "error",
            "message": "Session dataset is empty. Run role_discovery_tool and classify_roles_tool first.",
        })

    # Check if classification has been done
    classified_records = [r for r in dataset if "functional_category" in r]
    if not classified_records:
        return json.dumps({
            "status": "error",
            "message": "Users have not been classified yet. Run classify_roles_tool first.",
        })

    # Group roles by user
    user_roles: dict[str, list[str]] = {}
    user_category: dict[str, str] = {}
    user_environments: dict[str, set] = {}
    for record in dataset:
        uid = record["user_id"]
        user_roles.setdefault(uid, []).append(record["role_name"])
        user_environments.setdefault(uid, set()).add(record["environment"])
        if "functional_category" in record:
            user_category[uid] = record["functional_category"]

    over_privileged = []
    under_privileged = []
    optimal = []

    for user_id, roles in user_roles.items():
        category = user_category.get(user_id, "Functional")
        environments = list(user_environments.get(user_id, set()))
        expected_patterns = EXPECTED_ROLES_BY_CATEGORY.get(category, [])
        max_roles = MAX_ROLES_BY_CATEGORY.get(category, 6)

        # Find expected roles that user is missing
        missing_roles = []
        for pattern in expected_patterns:
            matched = find_matching_roles(roles, [pattern])
            if not matched:
                missing_roles.append(f"Role matching pattern '{pattern}' for {category} users")

        # Find excess roles from other categories
        excess_roles = find_excess_roles(roles, category)

        # Determine optimization action
        is_over = len(roles) > max_roles or len(excess_roles) > 0
        is_under = len(missing_roles) > 0

        if is_over:
            over_privileged.append({
                "user_id": user_id,
                "environments": environments,
                "functional_category": category,
                "current_roles": roles,
                "current_role_count": len(roles),
                "excess_roles": excess_roles,
                "recommended_action": "remove",
                "roles_to_remove": excess_roles,
                "rationale": (
                    f"User has {len(roles)} roles (max recommended for {category}: {max_roles}). "
                    f"Cross-category roles detected: {excess_roles}"
                ),
                "requires_human_approval": True,
            })

        if is_under:
            under_privileged.append({
                "user_id": user_id,
                "environments": environments,
                "functional_category": category,
                "current_roles": roles,
                "missing_role_patterns": missing_roles,
                "recommended_action": "add",
                "rationale": (
                    f"User is missing standard roles for {category} function. "
                    f"Missing patterns: {missing_roles}"
                ),
                "requires_human_approval": True,
            })

        if not is_over and not is_under:
            optimal.append({"user_id": user_id, "functional_category": category, "status": "optimal"})

    return json.dumps({
        "status": "success",
        "total_users_analyzed": len(user_roles),
        "over_privileged_count": len(over_privileged),
        "under_privileged_count": len(under_privileged),
        "optimal_count": len(optimal),
        "over_privileged_users": over_privileged,
        "under_privileged_users": under_privileged,
        "all_recommendations_require_human_approval": True,
    })
