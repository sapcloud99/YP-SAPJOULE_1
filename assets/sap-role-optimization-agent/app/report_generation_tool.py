"""Tool for generating statistical IAM reports (graphical + tabular)."""
import json
import logging
from langchain_core.tools import tool
from role_discovery_tool import get_session_dataset  # type: ignore[import]

logger = logging.getLogger(__name__)

LARGE_DATASET_THRESHOLD = 100


def calculate_iam_risk_score(
    sod_conflicts: int,
    single_holder_roles: int,
    over_privileged_users: int,
    total_users: int,
) -> float:
    """Calculate the overall IAM risk score as a percentage (capped at 100%)."""
    if total_users == 0:
        return 0.0
    raw = (sod_conflicts * 2 + single_holder_roles * 3 + over_privileged_users) / total_users * 100
    return round(min(raw, 100.0), 2)


def build_ascii_bar_chart(data: dict, title: str, width: int = 30) -> str:
    """Build a simple ASCII bar chart."""
    if not data:
        return f"\n{title}\n  (no data)\n"
    max_val = max(data.values()) if data.values() else 1
    lines = [f"\n{title}"]
    for label, value in data.items():
        bar_len = int((value / max_val) * width) if max_val > 0 else 0
        bar = "█" * bar_len
        lines.append(f"  {label:<25} {bar} {value}")
    return "\n".join(lines)


@tool
def report_generation_tool(
    sod_conflicts_json: str = "{}",
    single_holder_json: str = "{}",
    optimization_json: str = "{}",
    delivery_channel: str = "chat",
) -> str:
    """Generate a comprehensive IAM statistical report (graphical + tabular).

    Combines findings from SoD detection, single-holder analysis, and role optimization
    into a unified report with ASCII charts and tabular summaries.

    Args:
        sod_conflicts_json: JSON string output from sod_detection_tool (optional).
        single_holder_json: JSON string output from single_holder_detection_tool (optional).
        optimization_json: JSON string output from role_optimization_tool (optional).
        delivery_channel: Where to deliver the report: 'chat', 'email', or 'dashboard'.
    """
    dataset = get_session_dataset()
    total_records = len(dataset)

    sod_data = {}
    single_holder_data = {}
    optimization_data = {}
    try:
        if sod_conflicts_json and sod_conflicts_json != "{}":
            sod_data = json.loads(sod_conflicts_json)
    except Exception:
        pass
    try:
        if single_holder_json and single_holder_json != "{}":
            single_holder_data = json.loads(single_holder_json)
    except Exception:
        pass
    try:
        if optimization_json and optimization_json != "{}":
            optimization_data = json.loads(optimization_json)
    except Exception:
        pass

    unique_users = len({r["user_id"] for r in dataset})
    unique_roles = len({r["role_name"] for r in dataset})
    unique_envs = len({r["environment"] for r in dataset})

    sod_total = sod_data.get("total_conflicts", 0)
    sod_risk_breakdown = sod_data.get("risk_breakdown", {})
    single_holder_total = single_holder_data.get("total_single_holder_roles", 0)
    single_holder_breakdown = single_holder_data.get("criticality_breakdown", {})
    over_priv = optimization_data.get("over_privileged_count", 0)
    under_priv = optimization_data.get("under_privileged_count", 0)
    optimal = optimization_data.get("optimal_count", 0)

    category_dist: dict[str, int] = {}
    for r in dataset:
        cat = r.get("functional_category", "Unclassified")
        category_dist[cat] = category_dist.get(cat, 0) + 1

    env_dist: dict[str, int] = {}
    for r in dataset:
        env = r["environment"]
        env_dist[env] = env_dist.get(env, 0) + 1

    iam_risk_score = calculate_iam_risk_score(sod_total, single_holder_total, over_priv, unique_users)

    sod_chart = build_ascii_bar_chart(sod_risk_breakdown, "SoD Conflicts by Risk Level")
    single_holder_chart = build_ascii_bar_chart(single_holder_breakdown, "Single-Holder Roles by Criticality")
    category_chart = build_ascii_bar_chart(category_dist, "Users by Functional Category")
    env_chart = build_ascii_bar_chart(env_dist, "Role Records by Environment")

    table_lines = [
        "\n╔══════════════════════════════════════════════════════════╗",
        "║          SAP IAM GOVERNANCE REPORT — SUMMARY            ║",
        "╠══════════════════════════════════════════════════════════╣",
        f"║  Total Users Analyzed          : {unique_users:<27}║",
        f"║  Total Roles Analyzed          : {unique_roles:<27}║",
        f"║  Total Environments            : {unique_envs:<27}║",
        f"║  Total Records                 : {total_records:<27}║",
        "╠══════════════════════════════════════════════════════════╣",
        f"║  SoD Conflicts (Total)         : {sod_total:<27}║",
        f"║    ├─ High Risk                : {sod_risk_breakdown.get('High', 0):<27}║",
        f"║    ├─ Medium Risk              : {sod_risk_breakdown.get('Medium', 0):<27}║",
        f"║    └─ Low Risk                 : {sod_risk_breakdown.get('Low', 0):<27}║",
        "╠══════════════════════════════════════════════════════════╣",
        f"║  Single-Holder Roles (Total)   : {single_holder_total:<27}║",
        f"║    ├─ High Criticality         : {single_holder_breakdown.get('High', 0):<27}║",
        f"║    ├─ Medium Criticality       : {single_holder_breakdown.get('Medium', 0):<27}║",
        f"║    └─ Low Criticality          : {single_holder_breakdown.get('Low', 0):<27}║",
        "╠══════════════════════════════════════════════════════════╣",
        f"║  Role Optimization                                       ║",
        f"║    ├─ Over-Privileged Users    : {over_priv:<27}║",
        f"║    ├─ Under-Privileged Users   : {under_priv:<27}║",
        f"║    └─ Optimally Assigned Users : {optimal:<27}║",
        "╠══════════════════════════════════════════════════════════╣",
        f"║  ★ OVERALL IAM RISK SCORE      : {str(iam_risk_score) + '%':<27}║",
        "╚══════════════════════════════════════════════════════════╝",
    ]

    tabular_summary = "\n".join(table_lines)
    visual_charts = sod_chart + "\n" + single_holder_chart + "\n" + category_chart + "\n" + env_chart

    report_payload = {
        "report_type": "IAM_GOVERNANCE_REPORT",
        "metrics": {
            "total_users": unique_users,
            "total_roles": unique_roles,
            "total_environments": unique_envs,
            "total_records": total_records,
            "sod_conflicts": sod_total,
            "sod_risk_breakdown": sod_risk_breakdown,
            "single_holder_roles": single_holder_total,
            "single_holder_breakdown": single_holder_breakdown,
            "over_privileged_users": over_priv,
            "under_privileged_users": under_priv,
            "optimal_users": optimal,
            "iam_risk_score_pct": iam_risk_score,
        },
        "distributions": {
            "by_functional_category": category_dist,
            "by_environment": env_dist,
        },
        "delivery_channel": delivery_channel,
    }

    return json.dumps({
        "status": "success",
        "iam_risk_score": iam_risk_score,
        "delivery_channel": delivery_channel,
        "tabular_summary": tabular_summary,
        "visual_charts": visual_charts,
        "report_payload": report_payload,
        "auto_triggered": total_records >= LARGE_DATASET_THRESHOLD,
    })
