# 🪨 Sculpture

> "We don't build agents. We sculpt them."

**Sculpture** is a Claude Code plugin that lets you remove AI capabilities for safer, more token-efficient agents.

Inspired by the **Kailasa Temple at Ellora** - carved from a single mountain by removing 200,000 tons of rock - we start with a full AI and remove what's not needed.

## Why Sculpture?

| Traditional Approach | Sculpture Approach |
|---------------------|-------------------|
| Add restrictions, guardrails, rules | Remove capabilities entirely |
| AI can ignore rules | AI can't use what doesn't exist |
| Jailbreaks possible | Nothing to jailbreak |
| Tokens wasted on unused tools | Zero overhead for removed tools |
| "Please don't do X" | X doesn't exist |

## Installation

```bash
/plugin install github:Prajhan26/sculpture-plugin
```

Or test locally:

```bash
claude --plugin-dir ~/sculpture-plugin
```

## Quick Start

```bash
# Create a new sculpture spec
/sculpture:init

# Remove capabilities
/sculpture:remove web_search
/sculpture:remove file_write
/sculpture:remove code_execute

# Check status
/sculpture:status

# Or load a template
/sculpture:load customer-support
```

## Commands

| Command | Description |
|---------|-------------|
| `/sculpture` | Show status or start setup |
| `/sculpture:init` | Create sculpture.yaml |
| `/sculpture:remove <tool>` | Remove a capability |
| `/sculpture:keep <tool>` | Keep a capability |
| `/sculpture:status` | Show what's removed/kept |
| `/sculpture:templates` | List pre-built templates |
| `/sculpture:load <name>` | Load a template |
| `/sculpture:audit` | Generate audit report |

## Templates

### customer-support
For support bots. Only answers questions.
```yaml
remove: [web_search, file_write, file_delete, code_execute, computer_use]
keep: [text_generation]
```

### code-reviewer
For PR review bots. Reads but doesn't write.
```yaml
remove: [file_write, file_delete, code_execute, web_search]
keep: [file_read, text_generation]
```

### content-writer
For content creation. Writes files, no code.
```yaml
remove: [code_execute, file_read, file_delete, computer_use]
keep: [web_search, file_write, text_generation]
```

### minimal
Maximum security. Text only.
```yaml
remove: [web_search, file_read, file_write, file_delete, code_execute, computer_use, mcp_tools]
keep: [text_generation]
```

## Sculpture Spec Format

```yaml
# sculpture.yaml

name: my-agent
version: 1.0.0
description: What this agent does

base_model: claude-sonnet-4-20250514

remove:
  - web_search
  - file_write
  - code_execute

keep:
  - file_read
  - text_generation

audit:
  log_requests: true
  log_responses: true
  retention_days: 90
```

## Three Walls of Security

### Wall 1: Tool Removal
Tools removed from API call. Claude never sees them.

### Wall 2: Output Interception  
Catches hallucinated tool calls before user sees them.

### Wall 3: Context Shaping
Claude believes it never had the capability.

## Token Savings

| Removed Tool | Tokens Saved Per Request |
|--------------|-------------------------|
| web_search | ~150 |
| file_read | ~100 |
| file_write | ~100 |
| code_execute | ~200 |
| computer_use | ~300 |

**Example:** Remove 5 tools = save ~650 tokens per request = 650,000 tokens saved over 1000 requests.

## The Sculptor Agent

Need help deciding what to remove? Use the Sculptor agent:

```
/sculpture

> What will your agent do?
"Answer customer questions"

> Does it need web search?
"No"

> Does it need file access?
"No"

Here's your sculpture spec...
```

## Philosophy

> "A person without hands cannot be proven to be the thief - he has no hands, how would he have done it?"

**Absence of capability = Proof of innocence**

When compliance asks "Can your AI access customer data?"
- With guardrails: "It's told not to" ❌
- With Sculpture: "It cannot. The capability doesn't exist." ✅

## Use Cases

- **Startups**: Prove to investors your AI is safe
- **Enterprises**: Meet compliance requirements
- **Developers**: Save tokens, stay focused
- **Agencies**: Client-specific restricted agents

## Contributing

PRs welcome. See [CONTRIBUTING.md](CONTRIBUTING.md).

## License

MIT

---

**Built by [@hijaborprajhaan](https://twitter.com/hijaborprajhaan)**

*Like the Kailasa Temple, the agent was always inside. We just removed what wasn't needed.*
