"""
status.py — Sculpture status display

Shows what's active in the current sculpture.yaml at a glance:
what's removed, what's kept, estimated token savings, and security score.

Usage:
    python tools/status.py
"""

import sys
from pathlib import Path

from enforce import load_spec, VIOLATION_LOG


# Token savings per removed capability (per API request)
TOKEN_SAVINGS: dict[str, int] = {
    "web_search":   150,
    "web_fetch":    100,
    "file_read":    100,
    "file_write":   100,
    "file_delete":  100,
    "code_execute": 200,
    "computer_use": 300,
    "agent_spawn":   50,
}

# Max possible score = all 8 capabilities removed + all 3 walls active
MAX_SCORE = len(TOKEN_SAVINGS) + 3


def security_score(removed: list[str]) -> tuple[int, int]:
    """Return (score, max_score). Walls are always active so always add 3."""
    capability_points = len(removed)
    wall_points = 3  # walls 1, 2, 3 are always on
    return capability_points + wall_points, MAX_SCORE


def score_label(score: int, max_score: int) -> str:
    ratio = score / max_score
    if ratio == 1.0:
        return "MAXIMUM"
    if ratio >= 0.75:
        return "HIGH"
    if ratio >= 0.5:
        return "MEDIUM"
    return "LOW"


def violation_count(log_path: str = VIOLATION_LOG) -> int:
    path = Path(log_path)
    if not path.exists():
        return 0
    count = 0
    with open(path) as f:
        for line in f:
            if line.strip():
                count += 1
    return count


def main():
    try:
        spec = load_spec("sculpture.yaml")
    except FileNotFoundError:
        print("No sculpture.yaml found in this directory.")
        print()
        print("To get started:")
        print("  /sculpture:init               — create a blank spec")
        print("  /sculpture:load customer-support  — load a template")
        sys.exit(0)

    name        = spec.get("name", "unnamed")
    model       = spec.get("base_model", "unknown")
    description = spec.get("description", "")
    removed     = spec.get("remove", [])
    kept        = spec.get("keep", [])
    max_tokens  = spec.get("constraints", {}).get("max_tokens")

    score, max_score      = security_score(removed)
    label                 = score_label(score, max_score)
    total_savings         = sum(TOKEN_SAVINGS.get(cap, 0) for cap in removed)
    savings_per_1k        = total_savings * 1000
    violations            = violation_count()

    lines = []

    # ── Header ──────────────────────────────────────────────────────────────
    lines += [
        "┌─────────────────────────────────────────────────────────┐",
        f"│  SCULPTURE STATUS — {name:<37}│",
        "└─────────────────────────────────────────────────────────┘",
        "",
    ]
    if description:
        lines += [f"  {description}", ""]
    lines += [f"  Model: {model}", ""]

    # ── Security score ───────────────────────────────────────────────────────
    bar_filled = round((score / max_score) * 20)
    bar        = "█" * bar_filled + "░" * (20 - bar_filled)
    lines += [
        f"  Security Score   [{bar}]  {score}/{max_score} — {label}",
        "",
    ]

    # ── Removed capabilities ─────────────────────────────────────────────────
    lines += ["  ── REMOVED (cannot be used) " + "─" * 29]
    if removed:
        for cap in removed:
            savings = TOKEN_SAVINGS.get(cap, 0)
            lines.append(f"    ✗  {cap:<20}  saves ~{savings} tokens/request")
    else:
        lines.append("    (nothing removed — full capability)")
    lines.append("")

    # ── Kept capabilities ────────────────────────────────────────────────────
    lines += ["  ── ACTIVE (agent can use these) " + "─" * 25]
    if kept:
        for cap in kept:
            lines.append(f"    ✓  {cap}")
    else:
        lines.append("    (none explicitly listed)")
    lines.append("")

    # ── Walls ────────────────────────────────────────────────────────────────
    lines += [
        "  ── SECURITY WALLS " + "─" * 38,
        "    Wall 1  Tool Removal         ✓",
        "    Wall 2  Output Interception  ✓",
        "    Wall 3  Context Shaping      ✓",
        "",
    ]

    # ── Token savings ────────────────────────────────────────────────────────
    lines += [
        "  ── TOKEN SAVINGS " + "─" * 39,
        f"    Per request:     ~{total_savings} tokens",
        f"    Per 1,000 calls: ~{savings_per_1k:,} tokens",
    ]
    if max_tokens:
        lines.append(f"    Max per response: {max_tokens} tokens (capped)")
    lines.append("")

    # ── Violations ───────────────────────────────────────────────────────────
    lines += ["  ── VIOLATIONS " + "─" * 42]
    if violations == 0:
        lines.append("    0 hallucinated tool calls intercepted  ✓")
    else:
        lines.append(f"    {violations} hallucinated tool call(s) intercepted by Wall 2")
        lines.append("    Run /sculpture:audit for the full breakdown.")
    lines.append("")

    # ── Next steps ───────────────────────────────────────────────────────────
    lines += [
        "  ── COMMANDS " + "─" * 45,
        "    /sculpture:audit       — generate compliance report",
        "    /sculpture:remove <x>  — remove another capability",
        "    /sculpture:load <name> — switch to a different template",
        "",
    ]

    print("\n".join(lines))


if __name__ == "__main__":
    main()
