"""Tool for fetching user identities and role assignments via SCIM MCP."""
import json
import logging
from typing import Any
from langchain_core.tools import tool
from role_discovery_tool import merge_records, normalize_environment, get_session_dataset

logger = logging.getLogger(__name__)


def create_scim_user_tool(mcp_tools: list) -> Any:
    """Create the SCIM user tool, injecting MCP tools."""

    def find_mcp_tool(tools: list, keyword: str):
        for t in tools:
            if keyword.lower() in t.name.lower():
                return t
        return None

    @tool
    async def scim_user_tool(environment: str = "BTP") -> str:
        """Fetch user identities and role/group assignments from S/4HANA SCIM API via MCP.

        Args:
            environment: The environment to query. One of: BTP, S4_ON_PREM, S4_CLOUD, MULTI_TENANT.
        """
        env = normalize_environment(environment)
        scim_tool = find_mcp_tool(mcp_tools, "scim")
        if not scim_tool:
            scim_tool = find_mcp_tool(mcp_tools, "user")

        if not scim_tool:
            return json.dumps({
                "status": "error",
                "message": "SCIM User MCP tool not available. Please check MCP server configuration.",
                "environment": env,
            })

        try:
            result = await scim_tool.ainvoke({"count": 100})
            raw_users = []
            if isinstance(result, dict):
                raw_users = result.get("Resources", result.get("value", []))
            elif isinstance(result, list):
                raw_users = result

            records = []
            for user in raw_users:
                user_id = user.get("id", user.get("userName", "UNKNOWN"))
                groups = user.get("groups", [])
                if not groups:
                    records.append({
                        "user_id": str(user_id),
                        "role_name": "NO_ROLE_ASSIGNED",
                        "environment": env,
                        "source": "scim",
                        "source_ref": f"SCIM/Users/{user_id}",
                        "display_name": user.get("displayName", ""),
                    })
                else:
                    for group in groups:
                        role_name = group.get("display", group.get("value", "UNKNOWN"))
                        records.append({
                            "user_id": str(user_id),
                            "role_name": str(role_name),
                            "environment": env,
                            "source": "scim",
                            "source_ref": f"SCIM/Users/{user_id}/groups/{role_name}",
                            "display_name": user.get("displayName", ""),
                        })

            added = merge_records(records)
            return json.dumps({
                "status": "success",
                "environment": env,
                "users_fetched": len(raw_users),
                "records_added": added,
                "total_in_session": len(get_session_dataset()),
            })
        except Exception as e:
            logger.error("scim_user_tool error: %s", e)
            return json.dumps({"status": "error", "message": str(e), "environment": env})

    return scim_user_tool
