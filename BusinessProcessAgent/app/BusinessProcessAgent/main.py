from typing import Any
from collections import OrderedDict

from strands import Agent, tool
from strands.agent.conversation_manager.null_conversation_manager import (
    NullConversationManager,
)
from bedrock_agentcore.runtime import BedrockAgentCoreApp

from model.load import load_model
from mcp_client.client import get_streamable_http_mcp_client


app = BedrockAgentCoreApp()
log = app.logger


# ---------------------------------------------------------
# BUSINESS TOOLS
# ---------------------------------------------------------

@tool
def lookup_order(order_id: str) -> str:
    """
    Look up the current status of a customer order.

    Args:
        order_id: Customer order ID such as ORD1001.
    """
    orders = {
        "ORD1001": {
            "status": "Delayed",
            "expected_delivery": "2 days",
        },
        "ORD1002": {
            "status": "Shipped",
            "expected_delivery": "Tomorrow",
        },
        "ORD1003": {
            "status": "Delivered",
            "expected_delivery": "Already delivered",
        },
    }

    order = orders.get(order_id.upper())

    if not order:
        return f"Order {order_id} was not found."

    return (
        f"Order {order_id.upper()}: "
        f"Status={order['status']}, "
        f"Expected delivery={order['expected_delivery']}"
    )


@tool
def check_ticket_priority(issue: str) -> str:
    """
    Determine the priority of a customer support issue.

    Args:
        issue: Description of the customer's problem.
    """
    issue_lower = issue.lower()

    high_priority_words = [
        "fraud",
        "stolen",
        "payment failed",
        "charged twice",
        "account hacked",
        "urgent",
    ]

    medium_priority_words = [
        "delayed",
        "late",
        "wrong item",
        "refund",
        "damaged",
    ]

    if any(word in issue_lower for word in high_priority_words):
        return "Priority: HIGH"

    if any(word in issue_lower for word in medium_priority_words):
        return "Priority: MEDIUM"

    return "Priority: LOW"


@tool
def create_support_action(priority: str, issue: str) -> str:
    """
    Recommend an automated business action based on priority.

    Args:
        priority: Ticket priority such as HIGH, MEDIUM, or LOW.
        issue: Customer issue description.
    """
    priority_upper = priority.upper()

    if "HIGH" in priority_upper:
        action = "Escalate immediately to the senior support team."

    elif "MEDIUM" in priority_upper:
        action = "Create a support ticket and notify the responsible team."

    else:
        action = "Create a standard support ticket for normal processing."

    return f"Automated business action: {action}"


# ---------------------------------------------------------
# AGENT CONFIGURATION
# ---------------------------------------------------------

DEFAULT_SYSTEM_PROMPT = """
You are a Customer Support Business Process Automation Agent.

Your job is to analyze customer support requests and automate
the appropriate business process.

Follow this workflow:

1. Understand the customer's issue.
2. If an order ID is provided, use the lookup_order tool.
3. Use check_ticket_priority to determine the ticket priority.
4. Use create_support_action to determine the appropriate business action.
5. Give the customer a clear final response.

Important:
- Use tools when they are relevant.
- Do not invent order information.
- Explain the business decision clearly.
- Keep responses concise and professional.
"""


tools = [
    lookup_order,
    check_ticket_priority,
    create_support_action,
]


# Add MCP client if available
mcp_clients = [get_streamable_http_mcp_client()]

for mcp_client in mcp_clients:
    if mcp_client:
        tools.append(mcp_client)


# ---------------------------------------------------------
# SESSION MANAGEMENT
# ---------------------------------------------------------

def _make_conversation_manager():
    return NullConversationManager()


def agent_factory():
    cache = OrderedDict()

    def get_or_create_agent(session_id):
        if session_id in cache:
            cache.move_to_end(session_id)
            return cache[session_id]

        if len(cache) >= 128:
            cache.popitem(last=False)

        cache[session_id] = Agent(
            model=load_model(),
            system_prompt=DEFAULT_SYSTEM_PROMPT,
            tools=tools,
            conversation_manager=_make_conversation_manager(),
            hooks=[],
        )

        return cache[session_id]

    return get_or_create_agent


get_or_create_agent = agent_factory()


# ---------------------------------------------------------
# PAYLOAD HANDLING
# ---------------------------------------------------------

def strip_trailing_tool_use(messages: Any) -> list[dict]:
    """Remove trailing toolUse blocks from incoming messages."""

    if not isinstance(messages, list):
        raise ValueError("messages must be a list")

    messages = list(messages)

    while messages:
        last = messages[-1]

        if not isinstance(last, dict):
            raise ValueError("each message must be an object")

        original_content = last.get("content", [])

        if not isinstance(original_content, list):
            raise ValueError(
                "each message content value must be a list"
            )

        content = [
            block
            for block in original_content
            if isinstance(block, dict) and "toolUse" not in block
        ]

        if len(content) == len(original_content):
            break

        if content:
            messages[-1] = {
                **last,
                "content": content,
            }
            break

        messages.pop()

    return messages


def _extract_prompt(payload: dict):
    """Extract the user prompt from the AgentCore request."""

    if not isinstance(payload, dict):
        raise ValueError("payload must be a JSON object")

    if "messages" in payload:
        return strip_trailing_tool_use(payload["messages"])

    if "tool_results" in payload:
        tool_results = payload["tool_results"]

        if not isinstance(tool_results, list):
            raise ValueError("tool_results must be a list")

        return [
            {
                "role": "user",
                "content": [
                    {
                        "toolResult": {
                            "toolUseId": tr["toolUseId"],
                            "status": tr.get("status", "success"),
                            "content": tr.get("content", []),
                        }
                    }
                    for tr in tool_results
                ],
            }
        ]

    prompt = payload.get("prompt", "")

    if not isinstance(prompt, str):
        raise ValueError("prompt must be a string")

    return prompt


# ---------------------------------------------------------
# AGENTCORE RUNTIME ENTRYPOINT
# ---------------------------------------------------------

@app.entrypoint
async def invoke(payload, context):
    log.info("Invoking Customer Support Business Process Agent")

    session_id = getattr(
        context,
        "session_id",
        "default-session",
    )

    agent = get_or_create_agent(session_id)

    prompt = _extract_prompt(payload)

    async for event in agent.stream_async(prompt):
        if not isinstance(event, dict):
            continue

        if "event" not in event:
            continue

        cbs = event["event"].get("contentBlockStart")

        if cbs is not None and not cbs.get("start"):
            continue

        yield event


if __name__ == "__main__":
    app.run()