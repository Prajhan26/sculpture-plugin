# Sculpture Plugin — SPEC v1.0

## Vision
"It's easier to know what's NOT needed than what IS needed."

Start with a complete AI. Sculpt away everything that isn't your agent.
What remains is solid, complete, and inherently secure — not because 
rules prevent misuse, but because removed capabilities cease to exist.

## Problem
Every AI agent today is built additively:
- Start with nothing
- Wire up tools
- Bolt on memory
- Add guardrails
- Hope nothing breaks

Rules can be ignored. Guardrails can be jailbroken.
Absence cannot be faked.

## Solution
Sculpture: a Claude Code plugin that removes AI capabilities
instead of restricting them.

## Who Is It For?
- Developers building focused agents
- Startups proving AI safety to investors
- Enterprises meeting compliance requirements
- Anyone who wants less risk and fewer tokens

## Core Commands
- /sculpture → show current status
- /sculpture:init → create sculpture.yaml
- /sculpture:remove <tool> → remove a capability
- /sculpture:status → what's removed/kept
- /sculpture:templates → pre-built profiles
- /sculpture:audit → generate security report

## WAT Structure
workflows/
└── sculpt.md          ← how to run a sculpture session

agents/
└── sculptor.md        ← guides user on what to remove

skills/
└── sculpture-guide/
    └── SKILL.md       ← knowledge about subtractive AI

tools/                 ← future: Python enforcement scripts

CLAUDE.md              ← brain: always knows this project
SPEC.md                ← this file

## What Does Done Look Like?
1. User runs /sculpture in any project
2. Sculptor agent asks smart questions
3. Generates sculpture.yaml automatically
4. Claude Code enforces the spec
5. Agent is safer, cheaper, focused

## What Success Looks Like
- Someone installs it from GitHub in one command
- They run /sculpture and get a working spec in 5 minutes
- Their agent uses 40% fewer tokens
- They can prove to compliance: "It cannot. The capability doesn't exist."