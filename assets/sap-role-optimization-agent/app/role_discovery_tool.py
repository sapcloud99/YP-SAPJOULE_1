"""Tool for discovering SAP business roles via MCP."""
import json
import logging
from typing import Any
from langchain_core.tools import tool

logger = logging.getLogger(__name__)

# In-session role dataset (shared state via module-level dict)
_session_dataset: list[dict] = []

ENVIRONMENT_ALIASES = {
    "on-premise": "S4_ON_PREM",
    "onprem": "S4_ON_PREM",
    "s/4 op": "S4_ON_PREM",
    "s4op": "S4_ON_PREM",
    "s4_on_prem": "S4_ON_PREM",
    "on_premise": "S4_ON_PREM",
    "btp": "BTP",
    "s4_cloud": "S4_CLOUD",
    "s/4 cloud": "S4_CLOUD",
    "s4cloud": "S4_CLOUD",
    "cloud": "S4_CLOUD",
    "multi_tenant": "MULTI_TENANT",
    "multi-tenant": "MULTI_TENANT",
    "multitenant": "MULTI_TENANT",
}

VALID_ENVIRONMENTS = {"BTP", "S4_ON_PREM", "S4_CLOUD", "MULTI_TENANT"}


def normalize_environment(env: str) -> str:
    """Normalize environment name to canonical form."""
    normalized = ENVIRONMENT_ALIASES.get(env.lower().strip(), env.upper().strip())
    if normalized not in VALID_ENVIRONMENTS:
        return env.upper().strip()
    return normalized


def get_session_dataset() -> list[dict]:
    """Return the current in-session role dataset."""
    return _session_dataset


def clear_session_dataset() -> None:
    """Clear the in-session role dataset (used in tests)."""
    _session_dataset.clear()


def merge_records(new_records: list[dict]) -> int:
    """Merge new records into session dataset, deduplicating by (user_id, role_name, environment)."""
    added = 0
    existing_keys = {
        (r["user_id"], r["role_name"], r["environment"]) for r in _session_dataset
    }
    for record in new_records:
        key = (record["user_id"], record["role_name"], record["environment"])
        if key not in existing_keys:
            _session_dataset.append(record)
            existing_keys.add(key)
            added += 1
        else:
            # Tag with additional environments if needed
            for existing in _session_dataset:
                if (
                    existing["user_id"] == record["user_id"]
                    and existing["role_name"] == record["role_name"]
                ):
                    env = record["environment"]
                    if env not in existing.get("environments", [existing["environment"]]):
                        existing.setdefault("environments", [existing["environment"]]).append(env)
    return added


def create_role_discovery_tool(mcp_tools: list) -> Any:
    """Create the role discovery tool, injecting MCP tools."""

    def find_mcp_tool(tools: list, keyword: str):
        for t in tools:
            if keyword.lower() in t.name.lower():
                return t
        return None

    @tool
    async def role_discovery_tool(environment: str = "S4_CLOUD") -> str:
        """Fetch all business roles from S/4HANA via MCP and load into the session dataset.

        Args:
            environment: The environment to query. One of: BTP, S4_ON_PREM, S4_CLOUD, MULTI_TENANT.
        """
        env = normalize_environment(environment)
        business_role_tool = find_mcp_tool(mcp_tools, "businessrole")
        if not business_role_tool:
            business_role_tool = find_mcp_tool(mcp_tools, "business_role")
        if not business_role_tool:
            business_role_tool = find_mcp_tool(mcp_tools, "role")

        if not business_role_tool:
            return json.dumps({
                "status": "error",
                "message": "Business Role MCP tool not available. Please check MCP server configuration.",
                "environment": env,
            })

        try:
            result = await business_role_tool.ainvoke({"top": 100})
            raw = result if isinstance(result, list) else (result.get("value", []) if isinstance(result, dict) else [])

            records = []
            for item in raw:
                role_name = item.get("BusinessRole", item.get("role_name", item.get("id", "UNKNOWN")))
                user_id = item.get("BusinessRoleAssignment", item.get("user_id", ""))
                if isinstance(user_id, list):
                    for uid in user_id:
                        records.append({
                            "user_id": str(uid),
                            "role_name": str(role_name),
                            "environment": env,
                            "source": "api",
                            "source_ref": f"BusinessRole/{role_name}",
                        })
                else:
                    records.append({
                        "user_id": str(user_id) if user_id else f"unassigned_{role_name}",
                        "role_name": str(role_name),
                        "environment": env,
                        "source": "api",
                        "source_ref": f"BusinessRole/{role_name}",
                    })

            added = merge_records(records)
            return json.dumps({
                "status": "success",
                "environment": env,
                "roles_fetched": len(records),
                "records_added": added,
                "total_in_session": len(_session_dataset),
            })
        except Exception as e:
            logger.error("role_discovery_tool error: %s", e)
            return json.dumps({"status": "error", "message": str(e), "environment": env})

    return role_discovery_tool
