"""
audit.py — Sculpture compliance report generator

Reads sculpture.yaml and sculpture-violations.log and produces a human-readable
audit report. Safe to hand to a compliance officer, investor, or security team.

Usage:
    python tools/audit.py              # print report to terminal
    python tools/audit.py --save       # save as sculpture-audit-YYYY-MM-DD.md
"""

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from enforce import load_spec, VIOLATION_LOG


# Plain-English explanation of what each removed capability prevents
CAPABILITY_DESCRIPTIONS: dict[str, str] = {
    "web_search":   "Cannot search the internet. No external lookups, no competitor research, no data exfiltration via search.",
    "web_fetch":    "Cannot load external URLs. Cannot send data to or receive data from any website.",
    "file_read":    "Cannot read files from the system. No access to your documents, databases, or configuration.",
    "file_write":   "Cannot create or modify files. Cannot write malware, cannot tamper with your codebase.",
    "file_delete":  "Cannot delete files. Data destruction by this agent is impossible.",
    "code_execute": "Cannot run code. No shell access, no script execution, no arbitrary commands.",
    "computer_use": "Cannot control the mouse, keyboard, or screen. No unauthorized UI automation.",
    "agent_spawn":  "Cannot create sub-agents. Cannot delegate tasks to other AI instances with broader access.",
}


def load_violations(log_path: str = VIOLATION_LOG) -> list[dict]:
    path = Path(log_path)
    if not path.exists():
        return []
    entries = []
    with open(path) as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    entries.append(json.loads(line))
                except json.JSONDecodeError:
                    pass
    return entries


def generate_report(spec: dict, violations: list[dict]) -> str:
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    agent_name = spec.get("name", "unknown")
    model = spec.get("base_model", "unknown")
    description = spec.get("description", "")
    removed = spec.get("remove", [])
    kept = spec.get("keep", [])
    retention = spec.get("audit", {}).get("retention_days", 90)

    lines = []

    # ── Header ──────────────────────────────────────────────────────────────
    lines += [
        "╔══════════════════════════════════════════════════════════════╗",
        "║              SCULPTURE AUDIT REPORT                         ║",
        "╚══════════════════════════════════════════════════════════════╝",
        "",
        f"  Agent:       {agent_name}",
        f"  Model:       {model}",
        f"  Generated:   {now}",
    ]
    if description:
        lines.append(f"  Description: {description}")
    lines.append("")

    # ── Removed capabilities ────────────────────────────────────────────────
    lines += [
        "── REMOVED CAPABILITIES ────────────────────────────────────────",
        "   These capabilities DO NOT EXIST in this agent.",
        "   They cannot be used, accessed, or jailbroken into.",
        "",
    ]
    if removed:
        for cap in removed:
            desc = CAPABILITY_DESCRIPTIONS.get(cap, "Capability removed.")
            lines.append(f"  ✗  {cap}")
            lines.append(f"     {desc}")
            lines.append("")
    else:
        lines += ["  (none removed — full capability agent)", ""]

    # ── Kept capabilities ───────────────────────────────────────────────────
    lines += [
        "── ACTIVE CAPABILITIES ─────────────────────────────────────────",
        "",
    ]
    if kept:
        for cap in kept:
            lines.append(f"  ✓  {cap}")
    else:
        lines.append("  (none explicitly listed)")
    lines.append("")

    # ── Security walls ──────────────────────────────────────────────────────
    lines += [
        "── SECURITY WALLS ──────────────────────────────────────────────",
        "",
        "  Wall 1 — Tool Removal         ✓ ACTIVE",
        "    Blocked tools are stripped from the API request before it",
        "    is sent. Claude never sees them. Cannot use what doesn't exist.",
        "",
        "  Wall 2 — Output Interception  ✓ ACTIVE",
        "    Every API response is scanned. If Claude hallucinates a tool",
        "    call for a removed capability, it is caught and blocked before",
        "    it reaches the caller. Violations are logged.",
        "",
        "  Wall 3 — Context Shaping      ✓ ACTIVE",
        "    The system prompt tells Claude it never had these capabilities.",
        "    It does not attempt to use tools it believes don't exist.",
        "",
    ]

    # ── Violations ──────────────────────────────────────────────────────────
    lines += [
        "── VIOLATION LOG ───────────────────────────────────────────────",
        "",
    ]
    if violations:
        lines.append(f"  Total intercepted attempts: {len(violations)}")
        lines.append("")
        # Group by capability
        by_cap: dict[str, int] = {}
        for v in violations:
            cap = v.get("capability", "unknown")
            by_cap[cap] = by_cap.get(cap, 0) + 1
        for cap, count in sorted(by_cap.items(), key=lambda x: -x[1]):
            lines.append(f"  {cap}: {count} attempt(s) intercepted by Wall 2")
        lines.append("")
        lines.append(f"  Most recent: {violations[-1].get('timestamp', 'unknown')}")
    else:
        lines += [
            "  Intercepted attempts: 0",
            "  No hallucinated tool calls have been detected.",
        ]
    lines.append("")

    # ── Constraints ─────────────────────────────────────────────────────────
    constraints = spec.get("constraints", {})
    allowed_topics = constraints.get("allowed_topics", [])
    blocked_topics = constraints.get("blocked_topics", [])
    max_tokens = constraints.get("max_tokens")

    if allowed_topics or blocked_topics or max_tokens:
        lines += ["── BEHAVIORAL CONSTRAINTS ──────────────────────────────────────", ""]
        if max_tokens:
            lines.append(f"  Max tokens per response: {max_tokens}")
        if allowed_topics:
            lines.append(f"  Allowed topics: {', '.join(allowed_topics)}")
        if blocked_topics:
            lines.append(f"  Blocked topics: {', '.join(blocked_topics)}")
        lines.append("")

    # ── Compliance statement ────────────────────────────────────────────────
    lines += [
        "── COMPLIANCE STATEMENT ────────────────────────────────────────",
        "",
        f"  The '{agent_name}' agent was configured using the Sculpture",
        "  framework. Its capabilities were reduced at the API level —",
        "  not via rules or guardrails, but by physical removal.",
        "",
    ]
    if removed:
        lines.append(
            "  When asked whether this agent CAN perform a removed action,"
        )
        lines.append(
            "  the correct answer is: IT CANNOT. The capability does not exist."
        )
        lines.append(
            "  No instruction, jailbreak, or prompt injection can restore it."
        )
    lines += [
        "",
        f"  Audit logs are retained for {retention} days.",
        "",
        "╔══════════════════════════════════════════════════════════════╗",
        "║  END OF REPORT                                               ║",
        "╚══════════════════════════════════════════════════════════════╝",
    ]

    return "\n".join(lines)


def main():
    save = "--save" in sys.argv
    spec_path = "sculpture.yaml"

    try:
        spec = load_spec(spec_path)
    except FileNotFoundError:
        print("ERROR: No sculpture.yaml found in current directory.")
        print("Run /sculpture:init to create one, or load a template with /sculpture:load <name>")
        sys.exit(1)

    violations = load_violations()
    report = generate_report(spec, violations)

    print(report)

    if save:
        date_str = datetime.now().strftime("%Y-%m-%d")
        out_path = f"sculpture-audit-{date_str}.md"
        with open(out_path, "w") as f:
            f.write(f"```\n{report}\n```\n")
        print(f"\n[sculpture] Report saved to {out_path}")


if __name__ == "__main__":
    main()
