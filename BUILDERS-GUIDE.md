# Builder's Guide: AI Code Review Bot using Sculpture Plugin
### For someone brand new to VS Code → Claude Code → Vibe Coding

---

## PART 1: Setting Up VS Code

### Step 1: Install VS Code
Download from: https://code.visualstudio.com
Install it like any normal app. Open it.

### Step 2: Learn the 4 areas of VS Code

```
┌─────────────────────────────────────────────────────┐
│  Activity Bar │  Explorer / Sidebar                  │
│  (left icons) │  (your files)                        │
│               │                                      │
│               │  Editor (where you write code)       │
│               │                                      │
│               ├──────────────────────────────────── │
│               │  Terminal (bottom)                   │
└─────────────────────────────────────────────────────┘
```

- **Activity Bar** (far left) — click the files icon to see your project
- **Explorer** — shows all your files and folders
- **Editor** — click any file to open and edit it
- **Terminal** — where you run commands. Open it: `Ctrl+` ` ` (backtick) or View → Terminal

### Step 3: The only keyboard shortcuts you need right now

| Shortcut | What it does |
|----------|-------------|
| `Ctrl+` ` ` | Open/close terminal |
| `Ctrl+P` | Find any file fast |
| `Ctrl+Shift+P` | Command palette (search any VS Code action) |
| `Ctrl+S` | Save file |
| `Ctrl+Z` | Undo |

That's it. You don't need to memorise more than this to start.

---

## PART 2: Installing Claude Code

Claude Code is an AI assistant that lives in your terminal. It writes code with you.

### Step 1: Install Node.js first
Download from: https://nodejs.org — get the LTS version. Install it.

Check it worked — open VS Code terminal and type:
```bash
node --version
```
Should print something like `v20.x.x`

### Step 2: Install Claude Code
In the VS Code terminal:
```bash
npm install -g @anthropic-ai/claude-code
```

### Step 3: Log in
```bash
claude
```
It will open a browser and ask you to log in with your Anthropic account.
After login, come back to the terminal — you're in.

### Step 4: Install the Sculpture plugin
Still in the terminal, inside Claude Code:
```
/plugin marketplace add github:Prajhan26/sculpture-plugin
/plugin install sculpture@sculpture
```

You'll see a confirmation. Sculpture is now installed.

---

## PART 3: Setting Up Your Project

### Step 1: Create a new folder for the project
In the terminal (outside Claude Code — press Ctrl+C to exit Claude first):
```bash
mkdir pr-review-bot
cd pr-review-bot
```

Then open it in VS Code:
```bash
code .
```

VS Code will open with your new empty folder.

### Step 2: Install Python dependencies
```bash
pip install anthropic pyyaml PyGithub python-dotenv
```

### Step 3: Open Claude Code in this folder
```bash
claude
```

Now you're in Claude Code, inside your project folder. This is where the magic happens.

---

## PART 4: Understanding What We're Building

Before writing a single line of code — understand the architecture.

### The AI Code Review Bot

When someone opens a Pull Request on GitHub, this bot:

1. **Reads the PR diff** (what files changed, what lines changed)
2. **Analyses the code** for bugs, security issues, style problems
3. **Posts a review comment** back on the PR automatically

### The Three-Agent Pipeline (using Sculpture)

```
GitHub PR opened
       │
       ▼
┌─────────────────────────────────────────┐
│  Agent A — The Reader                   │
│  sculpture: file_read only              │
│  Job: fetch PR diff, save to file       │
│  Cannot: write to GitHub, search web   │
└─────────────────┬───────────────────────┘
                  │ passes diff as text
                  ▼
┌─────────────────────────────────────────┐
│  Agent B — The Analyst                  │
│  sculpture: text_generation only        │
│  Job: review the diff, find issues      │
│  Cannot: access internet, touch files  │
└─────────────────┬───────────────────────┘
                  │ passes review as text
                  ▼
┌─────────────────────────────────────────┐
│  Agent C — The Commenter                │
│  sculpture: web_fetch + file_write only │
│  Job: post review comment to GitHub PR │
│  Cannot: read your codebase            │
└─────────────────────────────────────────┘
```

Why three agents? Each one can only do its job. If any stage gets weird input or a jailbreak attempt — it's contained. Agent B cannot post to GitHub even if it wanted to. Agent A cannot modify anything.

---

## PART 5: Vibe Coding with Claude Code

"Vibe coding" means: you describe what you want in plain English, Claude writes it, you review and iterate.

You don't need to know how to code. You need to know what you want.

### The mindset

- Don't try to write code yourself
- Describe the outcome, not the implementation
- Read what Claude writes — understand it at a high level
- Ask "why" if something confuses you
- Ask Claude to change things by describing the change, not by editing code

### Step 1: Tell Claude what you're building

In Claude Code, type:

```
I'm building a three-agent AI code review bot for GitHub PRs using the 
Sculpture plugin. 

Here's the architecture:
- Agent A: reads the PR diff from GitHub using PyGithub, saves it to a temp file
- Agent B: reads the diff file, analyses it for bugs/security issues, outputs a review
- Agent C: posts the review as a comment on the GitHub PR

Each agent should have its own sculpture.yaml with only the capabilities it needs.
Agent A: file_write only (to save the diff)
Agent B: text_generation only (air-gapped analysis)
Agent C: web_fetch only (to post to GitHub API)

Start by creating the project structure and the three sculpture.yaml files.
```

### Step 2: Watch and review

Claude will create files. Don't panic — just read what it creates.

After it's done, ask:
```
Walk me through what you just created. Explain each file in one sentence.
```

### Step 3: Build Agent A — The Reader

Ask Claude:
```
Now build agent_a.py. It should:
- Take a GitHub PR URL as input (e.g. https://github.com/owner/repo/pull/123)
- Use PyGithub to fetch the list of changed files and the diff
- Save the diff to a file called pr_diff.txt
- Use SculptedClient with agent_a/sculpture.yaml

The GitHub token should come from a .env file.
```

### Step 4: Build Agent B — The Analyst

Ask Claude:
```
Now build agent_b.py. It should:
- Read pr_diff.txt
- Send it to Claude with a system prompt that says: 
  "You are a senior code reviewer. Review this diff for: bugs, security vulnerabilities,
   performance issues, and code quality problems. Be specific about line numbers.
   Format your review in markdown."
- Save the review to pr_review.txt
- Use SculptedClient with agent_b/sculpture.yaml
- Agent B has no internet access and no file write — text generation only
```

### Step 5: Build Agent C — The Commenter

Ask Claude:
```
Now build agent_c.py. It should:
- Read pr_review.txt
- Post it as a review comment on the GitHub PR using PyGithub
- Use SculptedClient with agent_c/sculpture.yaml
- The GitHub token comes from .env
```

### Step 6: Build the Pipeline Runner

Ask Claude:
```
Now build pipeline.py that runs all three agents in sequence:
1. Run agent_a.py with the PR URL
2. Run agent_b.py 
3. Run agent_c.py

Take the PR URL as a command line argument.
Print status after each step.
```

### Step 7: Test it

Ask Claude:
```
How do I test this? Walk me through getting a GitHub token, setting up .env, 
and running the pipeline on a real PR.
```

---

## PART 6: The Sculpture Files

These are the three `sculpture.yaml` files for each agent. Claude will create them, but here's what they should look like so you understand them:

**agent_a/sculpture.yaml** — can only write files:
```yaml
name: pr-reader-agent
description: Reads GitHub PR diffs and saves them locally

base_model: claude-sonnet-4-6

remove:
  - web_search
  - web_fetch
  - file_read
  - file_delete
  - code_execute
  - computer_use
  - agent_spawn

keep:
  - file_write

audit:
  log_requests: true
  log_responses: true
  log_blocked: true
```

**agent_b/sculpture.yaml** — completely air-gapped:
```yaml
name: pr-analyst-agent
description: Analyses code diffs for issues. No network. No file access.

base_model: claude-sonnet-4-6

remove:
  - web_search
  - web_fetch
  - file_read
  - file_write
  - file_delete
  - code_execute
  - computer_use
  - agent_spawn

keep:
  - text_generation

audit:
  log_requests: true
  log_responses: true
  log_blocked: true
```

**agent_c/sculpture.yaml** — can only post to GitHub:
```yaml
name: pr-commenter-agent
description: Posts review comments to GitHub PRs. Cannot read your codebase.

base_model: claude-sonnet-4-6

remove:
  - file_read
  - file_write
  - file_delete
  - code_execute
  - computer_use
  - agent_spawn

keep:
  - web_fetch
  - text_generation

audit:
  log_requests: true
  log_responses: true
  log_blocked: true
```

---

## PART 7: Iterating with Claude

Once the basic pipeline works, here's how to make it better — just ask:

**Make the review smarter:**
```
Update agent_b to also check for: missing error handling, hardcoded secrets,
SQL injection risks, and functions over 50 lines. Add a severity level 
(HIGH / MEDIUM / LOW) to each finding.
```

**Add a summary:**
```
Make agent_b produce a one-line summary at the top of the review:
"Found 3 issues: 1 HIGH, 1 MEDIUM, 1 LOW"
```

**Make it only comment if issues found:**
```
Update pipeline.py to skip agent_c if agent_b's review says "No issues found"
```

**Add a webhook so it runs automatically:**
```
Add a simple Flask webhook server that listens for GitHub PR events and 
automatically runs the pipeline when a new PR is opened.
```

---

## PART 8: Running the Compliance Audit

Once everything works, run this:
```bash
python tools/audit.py --save
```

This generates a report you can show anyone:
- "Agent B cannot access the internet" — provable
- "Agent A cannot post to GitHub" — provable
- "No data was transmitted beyond what's in the log" — provable

This is what makes this more than a demo. It's enterprise-ready on day one.

---

## PART 9: Useful Claude Code Commands

When you get stuck, use these inside Claude Code:

| What you want | What to type |
|---------------|-------------|
| See what changed | `what files did you just create?` |
| Something broke | `I got this error: [paste error]. Fix it.` |
| Understand the code | `explain agent_b.py to me like I'm new to Python` |
| Change something | `update agent_b to also check for hardcoded passwords` |
| Run a file | `how do I run pipeline.py?` |
| Start over on a file | `rewrite agent_a.py from scratch, keep the same goal` |

---

## PART 10: Project Structure When Done

```
pr-review-bot/
├── agent_a/
│   └── sculpture.yaml        ← file_write only
├── agent_b/
│   └── sculpture.yaml        ← text_generation only
├── agent_c/
│   └── sculpture.yaml        ← web_fetch only
├── agent_a.py                ← reads PR diff
├── agent_b.py                ← analyses diff
├── agent_c.py                ← posts review
├── pipeline.py               ← runs all three
├── .env                      ← GITHUB_TOKEN + ANTHROPIC_API_KEY
└── .gitignore                ← includes .env
```

---

## Quick Reference: Common Errors

| Error | Fix |
|-------|-----|
| `ModuleNotFoundError: anthropic` | Run `pip install anthropic` |
| `ModuleNotFoundError: github` | Run `pip install PyGithub` |
| `FileNotFoundError: sculpture.yaml` | Make sure you're running from the right folder |
| `401 Unauthorized` from GitHub | Check your GITHUB_TOKEN in .env |
| `401` from Anthropic | Check your ANTHROPIC_API_KEY in .env |

---

## What to Ask Claude When You're Completely Stuck

```
I'm building a PR review bot using the Sculpture plugin. Here's my project structure:
[paste your file list]

Here's the error I'm getting:
[paste the full error]

Here's the file that's failing:
[paste the file contents]

Fix it.
```

Claude will fix it. That's the whole point.

---

*Built with Sculpture — github.com/Prajhan26/sculpture-plugin*
