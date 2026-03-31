# Sculpture

> "We don't build agents. We sculpt them."

**Sculpture** is a Claude Code plugin that removes AI capabilities for safer, more token-efficient agents.

Inspired by the **Kailasa Temple at Ellora** — carved from a single mountain by removing 200,000 tons of rock — we start with a full AI and remove what's not needed.

---

## Why Sculpture?

| Traditional Approach | Sculpture Approach |
|---------------------|-------------------|
| Add restrictions, guardrails, rules | Remove capabilities entirely |
| AI can ignore rules | AI can't use what doesn't exist |
| Jailbreaks possible | Nothing to jailbreak |
| Tokens wasted on unused tools | Zero overhead for removed tools |
| "Please don't do X" | X doesn't exist |

> "A person without hands cannot be proven to be the thief — he has no hands, how would he have done it?"
>
> **Absence of capability = Proof of innocence**

---

## Installation

```bash
/plugin install github:Prajhan26/sculpture-plugin
```

Or run locally:

```bash
claude --plugin-dir ~/sculpture-plugin
```

---

## Quick Start

```bash
# Start a guided sculpture session
/sculpture

# Or go manual:
/sculpture:init                    # create a blank spec
/sculpture:load customer-support   # load a pre-built template
/sculpture:remove web_search       # remove a capability
/sculpture:status                  # see what's active
/sculpture:audit                   # generate compliance report
```

---

## Commands

| Command | What it does |
|---------|-------------|
| `/sculpture` | Start a guided session — sculptor agent walks you through everything |
| `/sculpture:init` | Create a blank `sculpture.yaml` in your project |
| `/sculpture:remove <tool>` | Remove a capability |
| `/sculpture:keep <tool>` | Explicitly keep a capability |
| `/sculpture:status` | Show what's removed, token savings, security score |
| `/sculpture:templates` | List all pre-built templates |
| `/sculpture:load <name>` | Load a pre-built template |
| `/sculpture:audit` | Generate a compliance report |

---

## Pre-Built Templates

### `customer-support`
For help desks and FAQ bots. Text-only. Cannot search the internet or touch files.
```yaml
remove: [web_search, web_fetch, file_read, file_write, file_delete, code_execute, computer_use, agent_spawn]
keep:   [text_generation]
```

### `code-reviewer`
For PR review bots. Can read code, cannot write or execute anything.
```yaml
remove: [file_write, file_delete, code_execute, web_search, web_fetch, computer_use, agent_spawn]
keep:   [file_read, text_generation]
```

### `content-writer`
For blog and marketing agents. Can write files and search the web. No code execution.
```yaml
remove: [file_read, file_delete, code_execute, computer_use, agent_spawn]
keep:   [web_search, web_fetch, file_write, text_generation]
```

### `data-analyst`
For reporting agents. Reads your data files, completely air-gapped from the internet.
```yaml
remove: [web_search, web_fetch, file_delete, code_execute, computer_use, agent_spawn]
keep:   [file_read, file_write, text_generation]
```

### `minimal`
Maximum security. Text generation only. The nuclear option.
```yaml
remove: [web_search, web_fetch, file_read, file_write, file_delete, code_execute, computer_use, agent_spawn]
keep:   [text_generation]
```

---

## Three Walls of Security

### Wall 1 — Tool Removal
Blocked tools are stripped from the API request before it's sent. Claude never sees them. You cannot use what doesn't exist.

### Wall 2 — Output Interception
Every API response is scanned. If Claude hallucinates a tool call for a removed capability, it's caught and blocked before it reaches your app. The violation is logged.

### Wall 3 — Context Shaping
The system prompt tells Claude it never had these capabilities. It doesn't attempt to use tools it believes don't exist.

---

## Using the Enforcement Layer in Code

```python
from tools.enforce import SculptedClient

# Drop-in replacement for anthropic.Anthropic().messages.create()
client = SculptedClient("sculpture.yaml")
response = client.create(
    messages=[{"role": "user", "content": "Search the web for competitors"}]
)
# → web_search stripped (Wall 1)
# → system prompt says it can't search (Wall 3)
# → if Claude hallucinates a search call, Wall 2 blocks it
```

---

## Token Savings

| Removed Capability | Tokens Saved Per Request |
|-------------------|--------------------------|
| `web_search` | ~150 |
| `web_fetch` | ~100 |
| `file_read` | ~100 |
| `file_write` | ~100 |
| `file_delete` | ~100 |
| `code_execute` | ~200 |
| `computer_use` | ~300 |
| `agent_spawn` | ~50 |

**Example:** Load the `minimal` template → save ~1,100 tokens per request → **1.1 million tokens saved per 1,000 calls.**

---

## Compliance

When a compliance officer asks **"Can your AI access our customer data?"**

- With guardrails: *"It's told not to"* ❌
- With Sculpture: *"It cannot. The capability doesn't exist."* ✅

Run `/sculpture:audit` to generate a signed compliance report you can share with auditors, investors, or legal.

---

## Project Structure

```
sculpture-plugin/
├── commands/sculpture.md        ← slash command definitions
├── agents/sculptor.md           ← guided interview agent
├── workflows/sculpt.md          ← end-to-end session flow
├── skills/sculpture-guide/      ← knowledge base
├── templates/                   ← pre-built profiles
│   ├── customer-support.yaml
│   ├── code-reviewer.yaml
│   ├── content-writer.yaml
│   ├── data-analyst.yaml
│   └── minimal.yaml
├── tools/
│   ├── enforce.py               ← SculptedClient (all 3 walls)
│   ├── audit.py                 ← compliance report generator
│   └── status.py                ← status display
├── sculpture.yaml               ← your agent's spec (generated)
└── .claude-plugin/plugin.json   ← plugin metadata
```

---

## License

MIT

---

*Built by [@Prajhan26](https://github.com/Prajhan26)*

*Like the Kailasa Temple, the agent was always inside. We just removed what wasn't needed.*
