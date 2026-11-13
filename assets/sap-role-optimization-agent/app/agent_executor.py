import logging
from opentelemetry import trace

from langchain_core.messages import SystemMessage
from langchain_core.messages.utils import count_tokens_approximately

from a2a.server.agent_execution import AgentExecutor as A2AAgentExecutor, RequestContext
from a2a.server.events import EventQueue
from a2a.server.tasks import TaskUpdater
from a2a.types import (
    InternalError,
    Part,
    TaskState,
    TextPart,
    UnsupportedOperationError,
)
from a2a.utils import new_agent_text_message, new_task
from a2a.utils.errors import ServerError

from agent import SampleAgent
from datetime_tool import get_datetime_tool
from load_skill_resources import get_load_skill_resource_tool
from mcp_providers.agw import get_mcp_tools
from prompt_injection_detector import wrap_tool

logger = logging.getLogger(__name__)
tracer = trace.get_tracer(__name__)


def _log_milestone(milestone_id: str, achieved: bool, description: str) -> None:
    """Emit structured milestone log statement."""
    status = "achieved" if achieved else "missed"
    logger.info("[%s.%s]: %s", milestone_id, status, description)


class AgentExecutor(A2AAgentExecutor):
    def __init__(self):
        self.agent = SampleAgent()
        self.skill_tools = [get_datetime_tool(), *get_load_skill_resource_tool()]
        # Domain-specific analysis tools loaded lazily to avoid top-level import issues
        self._domain_tools = None

    def _load_domain_tools(self) -> list:
        """Lazily load domain tools on first execution."""
        if self._domain_tools is None:
            # Import here (not at module level) so peer-level imports resolve
            # correctly at runtime when app/ is on sys.path.
            # pylint: disable=import-error,import-outside-toplevel
            from classify_roles_tool import classify_roles_tool  # type: ignore[import]
            from file_ingestion_tool import file_ingestion_tool  # type: ignore[import]
            from sod_detection_tool import sod_detection_tool  # type: ignore[import]
            from single_holder_detection_tool import single_holder_detection_tool  # type: ignore[import]
            from backup_recommendation_tool import backup_recommendation_tool  # type: ignore[import]
            from role_optimization_tool import role_optimization_tool  # type: ignore[import]
            from report_generation_tool import report_generation_tool  # type: ignore[import]
            # pylint: enable=import-error,import-outside-toplevel
            self._domain_tools = [
                classify_roles_tool,
                file_ingestion_tool,
                sod_detection_tool,
                single_holder_detection_tool,
                backup_recommendation_tool,
                role_optimization_tool,
                report_generation_tool,
            ]
        return self._domain_tools

    async def execute(self, context: RequestContext, event_queue: EventQueue) -> None:
        """Execute the agent and stream results back via A2A protocol.

        Discovers and loads MCP tools from Agent Gateway before each execution.
        The user token is read from the context var set by JWTContextMiddleware.

        Args:
            context: Request context containing user input and task info
            event_queue: Queue for publishing task status updates

        Raises:
            ServerError: On unrecoverable agent execution errors
        """
        query = context.get_user_input()
        task = context.current_task
        if not task:
            assert context.message is not None, "Cannot create task without a message"
            task = new_task(context.message)
            await event_queue.enqueue_event(task)

        # Load MCP tools — user token is read from context var set by JWTContextMiddleware
        tools = []
        try:
            mcp_tools = await get_mcp_tools()
            if not mcp_tools:
                logger.warning("No tools returned from Agent Gateway")
            # Pass MCP tools to factory-created tools that need them
            from role_discovery_tool import create_role_discovery_tool
            from scim_user_tool import create_scim_user_tool
            role_disc_tool = create_role_discovery_tool(mcp_tools)
            scim_tool = create_scim_user_tool(mcp_tools)
            tools = [role_disc_tool, scim_tool, *mcp_tools]
        except Exception as e:
            logger.error(f"Failed to load tools from Agent Gateway: {e}")

        tools = [*tools, *self._load_domain_tools(), *self.skill_tools]

        # Wrap all tools with prompt injection scanning for uniform protection
        tools = [wrap_tool(t) for t in tools]

        from agent import get_system_prompt
        _system_prompt = get_system_prompt()
        _msg_tokens = count_tokens_approximately([SystemMessage(content=_system_prompt)])
        _total_tokens = count_tokens_approximately([SystemMessage(content=_system_prompt)], tools=list(tools))
        logger.info(
            "Loaded %d tool(s); token estimate — prompt: %d, tools: %d, total: %d",
            len(tools), _msg_tokens, _total_tokens - _msg_tokens, _total_tokens,
        )

        updater = TaskUpdater(event_queue, task.id, task.context_id)

        # M1 — Baseline Established instrumentation
        from role_discovery_tool import get_session_dataset
        dataset_before = len(get_session_dataset())

        try:
            async for item in self.agent.stream(query, task.context_id, tools=tools):
                is_task_complete = item["is_task_complete"]
                require_user_input = item["require_user_input"]
                content = item["content"]

                if require_user_input:
                    # Agent requests more input
                    await updater.update_status(
                        TaskState.input_required,
                        new_agent_text_message(content, task.context_id, task.id),
                        final=True,
                    )
                    break
                elif is_task_complete:
                    # Milestone instrumentation post-completion
                    dataset_after = get_session_dataset()
                    n_users = len({r["user_id"] for r in dataset_after})
                    n_roles = len({r["role_name"] for r in dataset_after})
                    n_envs = len({r["environment"] for r in dataset_after})

                    if len(dataset_after) > dataset_before:
                        _log_milestone("M1", True,
                            f"IAM baseline established — {n_users} users, {n_roles} roles, {n_envs} environments ingested")
                    elif dataset_before == 0 and len(dataset_after) == 0:
                        _log_milestone("M1", False,
                            "IAM baseline incomplete — one or more environments returned no data or upload was not provided")

                    # M5 — detect compliance report in content
                    if "IAM GOVERNANCE REPORT" in content or "iam_risk_score" in content.lower():
                        _log_milestone("M5", True,
                            f"compliance report published — delivered via chat")
                    # M2 — detect gap analysis
                    if "sod_conflicts" in content.lower() or "single_holder" in content.lower():
                        _log_milestone("M2", True,
                            "gap analysis complete — SoD conflicts and single-holder roles identified")
                    # M3 — detect classification
                    if "classify" in content.lower() or "functional_category" in content.lower():
                        _log_milestone("M3", True,
                            "role optimization recommendations ready — users classified")
                    # M4 — detect backup recommendations
                    if "backup_candidate" in content.lower() or "backup recommendation" in content.lower():
                        _log_milestone("M4", True,
                            "backup coverage plan complete — backup recommendations generated")

                    # Completed: add artifact and complete task
                    await updater.add_artifact(
                        [Part(root=TextPart(text=content))], name="agent_result"
                    )
                    await updater.complete()
                    break
                else:
                    # Working status update
                    await updater.update_status(
                        TaskState.working,
                        new_agent_text_message(content, task.context_id, task.id),
                    )
        except Exception as e:
            logger.exception("Agent execution error")
            raise ServerError(error=InternalError()) from e

    async def cancel(self, context: RequestContext, event_queue: EventQueue) -> None:
        raise ServerError(error=UnsupportedOperationError())
