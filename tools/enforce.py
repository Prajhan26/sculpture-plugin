"""
enforce.py — Sculpture enforcement layer

Reads sculpture.yaml and removes listed capabilities from Anthropic API calls.
Three walls of security:
  Wall 1 — strips blocked tools from the request before it reaches the API
  Wall 2 — intercepts the API response and removes any hallucinated tool calls
  Wall 3 — injects constraints into the system prompt so Claude believes it lacks the capability

Usage:
    from tools.enforce import SculptedClient
    client = SculptedClient("sculpture.yaml")
    response = client.create(messages=[...], ...)
"""

import json
import yaml
import anthropic
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


# Maps sculpture.yaml capability names → Anthropic tool type strings
CAPABILITY_TO_TOOLS: dict[str, list[str]] = {
    "web_search":    ["web_search_20260209", "web_search_20250305"],
    "file_read":     ["text_editor_20250728", "text_editor_20250429", "text_editor_20250124"],
    "file_write":    ["text_editor_20250728", "text_editor_20250429", "text_editor_20250124"],
    "file_delete":   ["text_editor_20250728", "text_editor_20250429", "text_editor_20250124"],
    "code_execute":  ["code_execution_20260120", "bash_20250124"],
    "computer_use":  ["computer_use_20250124", "computer_use_20241022"],
    "agent_spawn":   [],  # enforced via system prompt — no tool type to strip
    "web_fetch":     ["web_fetch_20260209"],
}

# Maps tool names that appear in tool_use response blocks → capability names
# Used by Wall 2 to identify hallucinated tool calls in responses
TOOL_NAME_TO_CAPABILITY: dict[str, str] = {
    # web search
    "web_search":               "web_search",
    # web fetch
    "web_fetch":                "web_fetch",
    # text editor (file operations)
    "str_replace_editor":       "file_write",
    "str_replace_based_edit_tool": "file_write",
    "text_editor":              "file_write",
    # code execution
    "bash":                     "code_execute",
    "code_execution":           "code_execute",
    # computer use
    "computer":                 "computer_use",
    "computer_use":             "computer_use",
}


VIOLATION_LOG = "sculpture-violations.log"


def log_violation(tool_name: str, capability: str, spec: dict) -> None:
    """Append a Wall 2 violation to sculpture-violations.log (JSONL format)."""
    if not spec.get("audit", {}).get("log_blocked", True):
        return
    entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "tool_name": tool_name,
        "capability": capability,
        "wall": 2,
        "agent": spec.get("name", "unknown"),
    }
    with open(VIOLATION_LOG, "a") as f:
        f.write(json.dumps(entry) + "\n")


def load_spec(path: str = "sculpture.yaml") -> dict:
    spec_path = Path(path)
    if not spec_path.exists():
        raise FileNotFoundError(f"sculpture.yaml not found at {spec_path.resolve()}")
    with open(spec_path) as f:
        return yaml.safe_load(f)


def get_blocked_tool_types(spec: dict) -> set[str]:
    """Return the set of Anthropic tool type strings that are removed by this spec."""
    blocked: set[str] = set()
    for capability in spec.get("remove", []):
        blocked.update(CAPABILITY_TO_TOOLS.get(capability, []))
    return blocked


def filter_tools(tools: list[dict] | None, blocked: set[str]) -> list[dict] | None:
    """Wall 1 — strip any tool whose type is in the blocked set before the request is sent."""
    if not tools:
        return tools
    filtered = [t for t in tools if t.get("type") not in blocked]
    removed = [t.get("type") for t in tools if t.get("type") in blocked]
    if removed:
        print(f"[sculpture:wall1] Blocked tools removed from request: {removed}")
    return filtered


def intercept_response(
    response: anthropic.types.Message,
    removed_capabilities: list[str],
    spec: dict | None = None,
) -> anthropic.types.Message:
    """
    Wall 2 — scan the API response for hallucinated tool_use blocks.

    Even though blocked tools were stripped from the request (Wall 1),
    Claude can occasionally hallucinate a tool call for a tool it believes it has.
    This function catches those attempts in the response before they reach the caller.

    If a hallucinated tool_use block is found:
    - It is removed from the response content
    - A text block is inserted explaining the capability was blocked
    - The violation is logged
    - stop_reason is corrected to "end_turn" if all tool_use blocks were removed
    """
    if not response.content:
        return response

    clean_blocks = []
    violations = []

    for block in response.content:
        if block.type == "tool_use":
            # Check if this tool's name maps to a removed capability
            capability = TOOL_NAME_TO_CAPABILITY.get(block.name)
            if capability and capability in removed_capabilities:
                violations.append((block.name, capability))
                # Insert a text explanation in place of the blocked tool call
                replacement = anthropic.types.TextBlock(
                    type="text",
                    text=(
                        f"[Sculpture] Blocked: attempted to use '{block.name}' "
                        f"({capability} is removed in this agent's spec). "
                        f"This capability does not exist in this agent."
                    ),
                )
                clean_blocks.append(replacement)
            else:
                clean_blocks.append(block)
        else:
            clean_blocks.append(block)

    if violations:
        for tool_name, capability in violations:
            print(
                f"[sculpture:wall2] VIOLATION — hallucinated tool call intercepted: "
                f"'{tool_name}' (capability: {capability})"
            )
            if spec:
                log_violation(tool_name, capability, spec)

        # Rebuild the response with clean content
        # We use object.__setattr__ because Message is a Pydantic model (immutable fields)
        import copy
        clean_response = copy.copy(response)
        object.__setattr__(clean_response, "content", clean_blocks)

        # If all content was tool_use and we replaced them all, fix stop_reason
        all_were_tool_use = all(b.type == "tool_use" for b in response.content)
        if all_were_tool_use:
            object.__setattr__(clean_response, "stop_reason", "end_turn")

        return clean_response

    return response


def build_system_prompt(spec: dict, existing_system: str | None = None) -> str:
    """Prepend sculpture constraints to any existing system prompt."""
    lines = ["[Sculpture constraints — enforced at runtime]"]

    removed = spec.get("remove", [])
    if removed:
        lines.append(f"You CANNOT use these capabilities: {', '.join(removed)}")

    behavior = spec.get("constraints", {}).get("behavior", [])
    for rule in behavior:
        lines.append(f"- {rule}")

    blocked_topics = spec.get("constraints", {}).get("blocked_topics", [])
    if blocked_topics:
        lines.append(f"Never discuss: {', '.join(blocked_topics)}")

    allowed_topics = spec.get("constraints", {}).get("allowed_topics", [])
    if allowed_topics:
        lines.append(f"Only respond to topics related to: {', '.join(allowed_topics)}")

    constraint_block = "\n".join(lines)
    if existing_system:
        return f"{constraint_block}\n\n{existing_system}"
    return constraint_block


class SculptedClient:
    """
    Wraps anthropic.Anthropic and enforces sculpture.yaml on every messages.create() call.

    Removed capabilities are stripped from the tools list before the request is sent.
    Topic constraints and behavioral rules are injected into the system prompt.
    The model specified in sculpture.yaml is used unless overridden.
    """

    def __init__(self, spec_path: str = "sculpture.yaml", **anthropic_kwargs):
        self.spec = load_spec(spec_path)
        self.blocked = get_blocked_tool_types(self.spec)
        self.client = anthropic.Anthropic(**anthropic_kwargs)
        self._model = self.spec.get("base_model", "claude-opus-4-6")

        removed = self.spec.get("remove", [])
        if removed:
            print(f"[sculpture] Loaded '{self.spec.get('name', 'unknown')}' — "
                  f"removed capabilities: {removed}")

    def create(self, **kwargs: Any) -> anthropic.types.Message:
        """
        Drop-in replacement for client.messages.create().
        Enforces all three walls of the sculpture spec on every call.
        """
        # Use model from spec unless caller explicitly passes one
        kwargs.setdefault("model", self._model)

        # Wall 1 — strip blocked tools from the request
        if "tools" in kwargs:
            kwargs["tools"] = filter_tools(kwargs["tools"], self.blocked)
            if not kwargs["tools"]:
                del kwargs["tools"]  # API rejects an empty tools list

        # Enforce max_tokens from spec
        spec_max = self.spec.get("constraints", {}).get("max_tokens")
        if spec_max and kwargs.get("max_tokens", 0) > spec_max:
            print(f"[sculpture] max_tokens capped from {kwargs['max_tokens']} to {spec_max}")
            kwargs["max_tokens"] = spec_max
        kwargs.setdefault("max_tokens", spec_max or 1024)

        # Wall 3 — inject constraints into system prompt
        kwargs["system"] = build_system_prompt(self.spec, kwargs.get("system"))

        # Send request
        response = self.client.messages.create(**kwargs)

        # Wall 2 — intercept hallucinated tool calls in the response
        response = intercept_response(response, self.spec.get("remove", []), self.spec)

        return response


if __name__ == "__main__":
    # Quick smoke test — reads sculpture.yaml in cwd and makes one call
    client = SculptedClient()
    response = client.create(
        messages=[{"role": "user", "content": "Hello, what can you help me with?"}],
    )
    for block in response.content:
        if block.type == "text":
            print(block.text)
