---
name: sculpt
description: End-to-end sculpture session. Guides user from zero to a complete sculpture.yaml spec.
---

# Sculpt Workflow

This workflow runs a complete sculpture session. It ties together the sculptor agent, the
command layer, and the enforcement tool into one coherent flow.

> "The agent was always inside. We just removed what wasn't needed."

---

## Step 1: Check for existing spec

Look for `sculpture.yaml` in the current working directory.

**If found:**
- Read it and show a summary:
  ```
  Sculpture spec found: <name>
  Removed: <list capabilities>
  Kept: <list capabilities>
  ```
- Ask: "Do you want to modify this spec, or start fresh?"
  - Modify → jump to Step 3 with existing spec loaded
  - Start fresh → delete current spec, continue to Step 2

**If not found:**
- Say: "No sculpture spec found. Let's build one."
- Continue to Step 2.

---

## Step 2: Run the sculptor agent

Follow the conversation flow defined in `agents/sculptor.md`.

Ask the following questions **one at a time**, waiting for each answer:

1. "What will your agent do? Describe it in one sentence."
2. "What's the worst thing that could happen if it went rogue?"
3. "Does it need to search the internet?" → yes/no
4. "Does it need to read files from the system?" → yes/no
5. "Does it need to create or modify files?" → yes/no
6. "Does it need to run code?" → yes/no
7. "Does it need to control the mouse, keyboard, or screen?" → no (almost always remove)
8. "Does it need to spawn sub-agents?" → no (almost always remove)

Record every answer. Do not proceed until all questions are answered.

---

## Step 3: Build the sculpture spec

Map the answers to capabilities:

| Answer | Action |
|--------|--------|
| No internet → | `remove: web_search` |
| No file read → | `remove: file_read` |
| No file write → | `remove: file_write, file_delete` |
| No code execution → | `remove: code_execute` |
| No computer control → | `remove: computer_use` |
| No sub-agents → | `remove: agent_spawn` |

Everything NOT removed goes into `keep:`.

**Check for a matching template** (from `commands/sculpture.md`):
- All 6 removed + only text_generation → use `minimal`
- Only text + no file access → use `customer-support`
- File read only, no write/exec → use `code-reviewer`

If a template matches, note it. The spec can still be customized from there.

**Add constraints from Step 2:**
- If they described topic restrictions → add `allowed_topics` and `blocked_topics`
- Default `max_tokens: 1024` unless their use case needs more
- Always set all three audit flags to `true`

---

## Step 4: Present spec for confirmation

Show the full generated `sculpture.yaml` to the user:

```
Here's your sculpture spec:

─────────────────────────────────
name: <agent-name>
description: <their one-sentence description>

remove:
  - <list>

keep:
  - <list>

constraints:
  max_tokens: <value>
  <any topic constraints>

audit:
  log_requests: true
  log_responses: true
  log_blocked: true
─────────────────────────────────

Estimated token savings: ~<N> tokens per request
(<sum the per-tool savings from commands/sculpture.md>)

This agent CANNOT: <plain English list of what's removed>
This agent CAN: <plain English list of what's kept>

Save this as sculpture.yaml?
```

Wait for confirmation before writing.

---

## Step 5: Write sculpture.yaml

Write the confirmed spec to `sculpture.yaml` in the current directory.

Then say:

```
Done. sculpture.yaml created.

To enforce this spec in your code:

  from tools.enforce import SculptedClient
  client = SculptedClient("sculpture.yaml")
  response = client.create(messages=[...])

SculptedClient wraps the Anthropic client and automatically:
  - Strips removed tools from every API call
  - Caps token usage to your max_tokens setting
  - Injects your constraints into the system prompt

Run /sculpture:status at any time to review your spec.
Run /sculpture:audit to generate a compliance report.
```

---

## Error cases

| Situation | Response |
|-----------|----------|
| User is vague about purpose | Ask for a concrete example: "Give me a specific task your agent will do" |
| User wants to keep everything | Say: "That's fine — but consider: less capability = less risk. You can always add back." |
| User is unsure about a capability | Default to removing it. "If you're not sure, remove it. You can always add it back." |
| sculpture.yaml already exists and looks correct | Don't regenerate. Show status and offer `/sculpture:audit` instead. |