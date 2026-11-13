"""Tool for recommending backup users for single-holder critical roles."""
# pylint: disable=import-error
import json
import logging
from langchain_core.tools import tool
from role_discovery_tool import get_session_dataset  # type: ignore[import]
from classify_roles_tool import classify_user  # type: ignore[import]

logger = logging.getLogger(__name__)


def score_backup_candidate(
    candidate_id: str,
    candidate_roles: list[str],
    target_role: str,
    target_category: str,
) -> dict:
    """Score a candidate's eligibility as a backup for a given role."""
    score = 0
    reasons = []

    # Category match
    candidate_classification = classify_user(candidate_roles)
    candidate_category = candidate_classification["primary_category"]
    if candidate_category == target_category:
        score += 40
        reasons.append(f"Functional category match ({candidate_category})")

    # Existing role overlap (similar role names)
    # Filter out common non-semantic prefix tokens ("br", "sap", etc.)
    _STOP_TOKENS = {"br", "sap", "the", "a", "an"}
    target_lower = target_role.lower()
    for role in candidate_roles:
        # Check for partial name overlap
        role_parts = set(role.lower().replace("_", " ").split()) - _STOP_TOKENS
        target_parts = set(target_lower.replace("_", " ").split()) - _STOP_TOKENS
        overlap = len(role_parts & target_parts)
        if overlap >= 2:
            score += 30
            reasons.append(f"Similar existing role: {role}")
            break
        elif overlap == 1:
            score += 10
            reasons.append(f"Partially related role: {role}")
            break

    # Number of existing roles (more roles = more context)
    if len(candidate_roles) >= 3:
        score += 10
        reasons.append("Holds multiple related roles")
    if len(candidate_roles) >= 5:
        score += 10
        reasons.append("Broad role portfolio")

    return {
        "candidate_id": candidate_id,
        "score": score,
        "candidate_category": candidate_category,
        "justification": "; ".join(reasons) if reasons else "General role portfolio alignment",
        "candidate_roles_count": len(candidate_roles),
    }


@tool
def backup_recommendation_tool(role_name: str, environment: str, max_candidates: int = 3) -> str:
    """Recommend backup users for a single-holder critical role.

    Analyzes the session dataset to find eligible candidates based on functional
    category match, existing role overlap, and department alignment.

    Args:
        role_name: The role name to find backup candidates for.
        environment: The environment where the role exists.
        max_candidates: Maximum number of candidates to return (default: 3).
    """
    dataset = get_session_dataset()
    if not dataset:
        return json.dumps({
            "status": "error",
            "message": "Session dataset is empty. Run role_discovery_tool or file_ingestion_tool first.",
        })

    # Find current holder(s) of this role in this environment
    current_holders = set()
    for record in dataset:
        if record["role_name"] == role_name and record["environment"] == environment:
            current_holders.add(record["user_id"])

    if not current_holders:
        return json.dumps({
            "status": "error",
            "message": f"Role '{role_name}' not found in environment '{environment}' in session dataset.",
        })

    # Determine target functional category
    from classify_roles_tool import classify_role_name
    target_category = classify_role_name(role_name)

    # Build candidate pool: all users NOT currently holding this role
    user_roles: dict[str, list[str]] = {}
    for record in dataset:
        uid = record["user_id"]
        user_roles.setdefault(uid, []).append(record["role_name"])

    candidates = []
    for uid, roles in user_roles.items():
        if uid in current_holders:
            continue
        scored = score_backup_candidate(uid, roles, role_name, target_category)
        if scored["score"] > 0:
            candidates.append(scored)

    if not candidates:
        return json.dumps({
            "status": "no_candidates",
            "message": f"No eligible backup candidates found for role '{role_name}' in {environment}. "
                       "Consider training a user from a related role or hiring.",
            "role_name": role_name,
            "environment": environment,
            "current_holders": list(current_holders),
        })

    # Sort by score descending
    candidates.sort(key=lambda c: c["score"], reverse=True)
    top_candidates = candidates[:max_candidates]

    # Generate access request summaries
    access_request_summaries = []
    for candidate in top_candidates:
        access_request_summaries.append({
            "request_for": candidate["candidate_id"],
            "role_to_assign": role_name,
            "environment": environment,
            "justification": f"Backup coverage for single-holder role. {candidate['justification']}",
            "requires_human_approval": True,
            "note": "This is a recommendation only. Role assignment must be executed by an authorized administrator.",
        })

    return json.dumps({
        "status": "success",
        "role_name": role_name,
        "environment": environment,
        "current_holders": list(current_holders),
        "target_category": target_category,
        "backup_candidates": top_candidates,
        "access_request_summaries": access_request_summaries,
        "human_approval_required": True,
    })
