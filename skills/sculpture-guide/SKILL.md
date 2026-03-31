name: sculpture-guide
description: Knowledge base for sculpting AI agents by removing unnecessary capabilities
---

# Sculpture Guide: Removing AI Capabilities

Sculpting an AI agent means removing capabilities it doesn't need, reducing its attack surface and blast radius.

## Core Principle

An agent should have the minimum capabilities required to do its job. Every capability you leave in is a capability that can be misused, exploited, or that can cause unintended harm.

## Capability Categories

### Tool Access
- **File system**: Read, Write, Edit, Glob — restrict to specific paths or remove write access entirely
- **Shell execution**: Bash — the most dangerous capability; remove unless absolutely necessary
- **Network**: WebFetch, WebSearch — remove for air-gapped or offline agents
- **Agent spawning**: Agent tool — remove to prevent recursive agent creation
- **External services**: MCP tools — remove any integrations the agent doesn't need

### Behavioral Constraints
- Limit the agent to specific directories or file types
- Prevent the agent from modifying its own configuration
- Restrict the agent from accessing secrets or credentials
- Prohibit the agent from making commits or pushing code without explicit approval

## Sculpting Strategies

### 1. Allowlist approach
Define exactly what the agent CAN do. Everything else is implicitly forbidden. Best for narrow, well-defined tasks.

### 2. Denylist approach
Start with full capabilities and explicitly remove dangerous ones. Better for general-purpose agents where you want to preserve flexibility but remove specific risks.

### 3. Scope restriction
Keep capabilities but limit their scope — e.g., allow file writes but only within `/tmp/agent-workspace/`.

## Common Removals

| If the agent does... | You can safely remove... |
|---------------------|--------------------------|
| Read-only analysis | Write, Edit, Bash |
| Local file processing | WebFetch, WebSearch |
| Single-step tasks | Agent (spawning sub-agents) |
| Non-code work | Glob, Grep (often) |
| Sandboxed work | All MCP/external tools |

## Red Flags: Capabilities to Almost Always Remove

- `Bash` with no path restrictions
- `Agent` tool with no depth limit
- MCP tools connecting to production systems
- Write access to config files or `.claude/` directories

## Applying Constraints in Practice

In a `CLAUDE.md` or agent system prompt, add explicit prohibitions:

```
IMPORTANT: You must never:
- Run shell commands (do not use the Bash tool)
- Write files outside of /tmp/workspace/
- Fetch external URLs
- Spawn sub-agents
```

Pair these instructions with tool allowlists in the agent configuration where supported.
