# Builder's Guide: Daily News Briefing Bot using Sculpture Plugin
### For someone brand new to VS Code → Claude Code → Vibe Coding

---

## What You're Building

Every morning, this bot:
1. **Fetches** the latest news from RSS feeds (BBC, TechCrunch, whatever you like)
2. **Analyses** the stories — summarises them, spots trends, filters noise
3. **Writes** a clean, readable daily briefing to a file you can open and read

No manual work. Run one command. Get your briefing.

---

## The Three-Agent Pipeline

```
RSS Feeds (internet)
       │
       ▼
┌─────────────────────────────────────────┐
│  Agent A — The Fetcher                  │
│  sculpture: web_fetch + file_write      │
│  Job: pull RSS feeds, save raw XML      │
│  Cannot: read local files, run code    │
└─────────────────┬───────────────────────┘
                  │ saves raw_news.txt
                  ▼
┌─────────────────────────────────────────┐
│  Agent B — The Analyst                  │
│  sculpture: file_read + file_write      │
│  Job: read raw news, summarise it       │
│  Cannot: touch the internet            │
└─────────────────┬───────────────────────┘
                  │ saves briefing_draft.txt
                  ▼
┌─────────────────────────────────────────┐
│  Agent C — The Writer                   │
│  sculpture: file_read + file_write      │
│  Job: format into beautiful briefing   │
│  Cannot: touch the internet            │
└─────────────────────────────────────────┘
                  │
                  ▼
         daily-briefing.md ← open and read this
```

Why split it? Agent B and C are completely air-gapped from the internet. They analyse and write based only on what Agent A saved. Even if someone injected a malicious news story — Agent B cannot phone home, cannot execute code, cannot do anything except read and write text.

---

## PART 1: VS Code Setup

### Install VS Code
Download from: https://code.visualstudio.com — install it like any normal app.

### The 4 areas you need to know

```
┌─────────────────────────────────────────────────────┐
│  Activity Bar │  Explorer (your files)               │
│  (left icons) │                                      │
│               │  Editor (open files here)            │
│               │                                      │
│               ├──────────────────────────────────── │
│               │  Terminal (run commands here)        │
└─────────────────────────────────────────────────────┘
```

**Open the terminal:** Press `Ctrl+` ` ` (the backtick key, top-left of keyboard)

### Keyboard shortcuts — just these four

| Shortcut | What it does |
|----------|-------------|
| `Ctrl+` ` ` | Open/close terminal |
| `Ctrl+P` | Find any file |
| `Ctrl+S` | Save |
| `Ctrl+Z` | Undo |

---

## PART 2: Install Claude Code

### Step 1: Install Node.js
Download from: https://nodejs.org — get the LTS version. Install it.

Check it worked — open terminal in VS Code and type:
```bash
node --version
```
Should print `v20.x.x` or similar.

### Step 2: Install Claude Code
```bash
npm install -g @anthropic-ai/claude-code
```

### Step 3: Log in
```bash
claude
```
Opens a browser. Log in with your Anthropic account. Come back to the terminal — you're in.

### Step 4: Install the Sculpture plugin
Inside Claude Code:
```
/plugin marketplace add github:Prajhan26/sculpture-plugin
/plugin install sculpture@sculpture
```

---

## PART 3: Create Your Project

Press `Ctrl+C` to exit Claude Code first. Then:

```bash
mkdir daily-news-bot
cd daily-news-bot
code .
```

VS Code opens with your new empty project. Now open Claude Code inside it:
```bash
claude
```

You're ready.

---

## PART 4: Vibe Coding — Step by Step

Vibe coding means you describe what you want in plain English. Claude writes the code. You review, test, and ask for changes — also in plain English.

**The rule:** Never try to write code yourself. Just describe outcomes.

---

### Step 1: Set up the project structure

Paste this into Claude Code:

```
I'm building a Daily News Briefing Bot using the Sculpture plugin.

It has three agents in a pipeline:
- Agent A: fetches RSS feeds from the internet, saves raw content to raw_news.txt
- Agent B: reads raw_news.txt, summarises stories, saves to briefing_draft.txt  
- Agent C: reads briefing_draft.txt, formats it beautifully, saves to daily-briefing.md

Each agent has its own folder with a sculpture.yaml:
- Agent A: can use web_fetch and file_write only
- Agent B: can use file_read and file_write only (no internet)
- Agent C: can use file_read and file_write only (no internet)

Please create:
1. The folder structure
2. All three sculpture.yaml files
3. A .env file template with ANTHROPIC_API_KEY
4. A .gitignore that ignores .env

Do not write any Python yet. Just the structure.
```

---

### Step 2: Understand what Claude created

After Claude creates the files, ask:
```
Explain the folder structure you just created. 
One sentence per file. What does each one do?
```

Read the explanation. If anything is confusing, ask Claude to explain it differently.

---

### Step 3: Build Agent A — The Fetcher

Paste this:
```
Now build agent_a.py. It should:

1. Fetch RSS feeds from these URLs using the requests library:
   - http://feeds.bbci.co.uk/news/rss.xml (BBC News)
   - https://techcrunch.com/feed/ (TechCrunch)
   - https://feeds.reuters.com/reuters/topNews (Reuters)

2. Parse each feed and extract for each story:
   - Title
   - Summary/description
   - Published date
   - Source name

3. Save everything to raw_news.txt in a clean format like:
   SOURCE: BBC News
   TITLE: Story title here
   DATE: 2026-04-01
   SUMMARY: The story summary here
   ---

4. Use SculptedClient with agent_a/sculpture.yaml
5. Print how many stories were fetched when done

The Anthropic API key should come from a .env file using python-dotenv.
Use feedparser library to parse RSS.
```

---

### Step 4: Test Agent A

Ask Claude:
```
What pip packages do I need to install to run agent_a.py?
Give me the exact pip install command.
```

Run what it tells you. Then:
```
How do I run agent_a.py? Give me the exact command.
```

Run it. You should see `raw_news.txt` appear with news stories. Open it and check it looks right.

If you get an error, paste the full error back to Claude:
```
I got this error when running agent_a.py:
[paste error here]
Fix it.
```

---

### Step 5: Build Agent B — The Analyst

Paste this:
```
Now build agent_b.py. It should:

1. Read raw_news.txt
2. Send the content to Claude with this system prompt:
   "You are a senior news analyst. Read these news stories and:
   - Group them by topic (Politics, Technology, Business, Science, etc.)
   - For each group, write 2-3 sentence summaries of the key stories
   - Identify the top 3 most important stories of the day and explain why
   - Note any common themes or trends across multiple stories
   - Keep the total length under 800 words"

3. Save Claude's analysis to briefing_draft.txt
4. Use SculptedClient with agent_b/sculpture.yaml (no internet access)
5. Print "Analysis complete" when done
```

Run it the same way. Check `briefing_draft.txt` — it should have a structured analysis.

---

### Step 6: Build Agent C — The Writer

Paste this:
```
Now build agent_c.py. It should:

1. Read briefing_draft.txt
2. Send it to Claude with this system prompt:
   "You are a professional newsletter writer. Take this news analysis and 
   format it as a beautiful daily briefing with:
   - A header with today's date
   - An opening line that captures the mood of the day's news
   - Clean sections with emoji icons for each topic
   - A 'Quote of the Day' (invent an appropriate one)
   - A closing line
   Format it in clean markdown."

3. Save the final briefing to daily-briefing.md with today's date in the filename
   e.g. briefing-2026-04-01.md

4. Use SculptedClient with agent_c/sculpture.yaml (no internet access)
5. Print the filename when done
```

---

### Step 7: Build the Pipeline Runner

Paste this:
```
Now build pipeline.py that:
1. Runs Agent A (fetch news)
2. Prints "News fetched. Analysing..."
3. Runs Agent B (analyse)
4. Prints "Analysis done. Writing briefing..."
5. Runs Agent C (format)
6. Prints "Done! Your briefing is ready: briefing-YYYY-MM-DD.md"

Each agent should run as a subprocess using Python's subprocess module.
Add a total time taken at the end.
Handle errors: if any agent fails, print what went wrong and stop.
```

---

### Step 8: Run the full pipeline

Ask Claude:
```
How do I run the full pipeline? Give me the exact command.
```

Run it. Wait about 30 seconds. Open your `briefing-2026-04-01.md` file.

You should have a fully formatted daily news briefing.

---

## PART 5: The Sculpture Files Explained

Here's what each `sculpture.yaml` does and why:

**agent_a/sculpture.yaml** — can only fetch and save:
```yaml
name: news-fetcher-agent
description: Fetches RSS feeds from the internet and saves raw content locally.

base_model: claude-sonnet-4-6

remove:
  - file_read       # cannot read your local files
  - file_delete     # cannot delete anything
  - code_execute    # cannot run code
  - computer_use    # cannot control your computer
  - agent_spawn     # cannot create sub-agents

keep:
  - web_fetch       # can access the internet (RSS feeds only)
  - file_write      # can save raw_news.txt

audit:
  log_requests: true
  log_responses: true
  log_blocked: true
```

**agent_b/sculpture.yaml** — completely air-gapped:
```yaml
name: news-analyst-agent
description: Analyses news stories. No internet. Cannot leak data externally.

base_model: claude-sonnet-4-6

remove:
  - web_search      # no internet
  - web_fetch       # no internet
  - file_delete     # cannot delete
  - code_execute    # cannot run code
  - computer_use    # cannot control computer
  - agent_spawn     # cannot spawn sub-agents

keep:
  - file_read       # reads raw_news.txt
  - file_write      # writes briefing_draft.txt

audit:
  log_requests: true
  log_responses: true
  log_blocked: true
```

**agent_c/sculpture.yaml** — same as B, formatting only:
```yaml
name: news-writer-agent
description: Formats news analysis into a readable briefing. No internet access.

base_model: claude-sonnet-4-6

remove:
  - web_search      # no internet
  - web_fetch       # no internet
  - file_delete     # cannot delete
  - code_execute    # cannot run code
  - computer_use    # cannot control computer
  - agent_spawn     # cannot spawn sub-agents

keep:
  - file_read       # reads briefing_draft.txt
  - file_write      # writes daily-briefing.md

audit:
  log_requests: true
  log_responses: true
  log_blocked: true
```

---

## PART 6: Making It Better — Vibe Iterations

Once it works, ask Claude for these upgrades one at a time:

**Add more news sources:**
```
Add 3 more RSS feeds to agent_a.py:
- Hacker News: https://news.ycombinator.com/rss
- The Verge: https://www.theverge.com/rss/index.xml
- Wired: https://www.wired.com/feed/rss
```

**Filter by topics you care about:**
```
Add a TOPICS variable at the top of agent_b.py that I can customise.
Default: ["AI", "startups", "technology", "science"]
Agent B should prioritise stories related to these topics.
```

**Add a "skip list" for boring stories:**
```
Add a way to skip stories that contain certain keywords.
Let me define SKIP_KEYWORDS = ["celebrity", "sports", "weather"] at the top.
Stories with these keywords should be filtered out before analysis.
```

**Schedule it to run every morning:**
```
How do I set this up to run automatically every morning at 7am on my Mac?
```

**Send it to your email:**
```
Add an optional step after agent_c that emails the briefing to me.
Use Python's smtplib with Gmail. The email address and app password 
should come from .env.
```

**Make a simple web page:**
```
Add a step that converts daily-briefing.md to a simple HTML page
so I can open it in my browser instead of a text editor.
```

---

## PART 7: Project Structure When Done

```
daily-news-bot/
├── agent_a/
│   └── sculpture.yaml       ← web_fetch + file_write only
├── agent_b/
│   └── sculpture.yaml       ← file_read + file_write only (no internet)
├── agent_c/
│   └── sculpture.yaml       ← file_read + file_write only (no internet)
├── agent_a.py               ← fetches RSS feeds
├── agent_b.py               ← analyses stories
├── agent_c.py               ← writes the briefing
├── pipeline.py              ← runs all three in order
├── raw_news.txt             ← generated, Agent A's output
├── briefing_draft.txt       ← generated, Agent B's output
├── briefing-2026-04-01.md   ← your daily briefing (open this!)
├── .env                     ← your API key (never share this)
└── .gitignore               ← ignores .env and generated files
```

---

## PART 8: Common Errors and Fixes

| Error | Fix |
|-------|-----|
| `ModuleNotFoundError: feedparser` | `pip install feedparser` |
| `ModuleNotFoundError: dotenv` | `pip install python-dotenv` |
| `ModuleNotFoundError: anthropic` | `pip install anthropic` |
| `FileNotFoundError: sculpture.yaml` | Make sure you're running from `daily-news-bot/` folder |
| `AuthenticationError` from Anthropic | Check ANTHROPIC_API_KEY in your `.env` file |
| `raw_news.txt not found` | Run agent_a.py first before agent_b.py |
| RSS feed URL gives error | The feed might be down — try a different one |

---

## PART 9: When You're Stuck — What to Paste into Claude

```
I'm building a Daily News Briefing Bot with the Sculpture plugin.

My project structure:
[paste output of: ls -la]

The error I'm getting:
[paste the full error message]

The file that's failing:
[paste the contents of the broken file]

Fix it.
```

Claude will fix it. Every time.

---

## PART 10: Run the Compliance Audit

Once it's working, run this from inside the `daily-news-bot` folder:
```bash
python ../sculpture-plugin/tools/audit.py --save
```

Or copy `tools/audit.py` into your project. It generates a report like:

```
✗  web_search   — Agent B cannot search the internet
✗  web_fetch    — Agent B cannot load external URLs  
✗  code_execute — Agent B cannot run any code

Results: 40/40 tests passing. ALL WALLS HOLDING.
```

You can show this to anyone and say: "This AI analyses your news but provably 
cannot leak it, cannot phone home, cannot do anything except read and write local files."

---

## Quick Reference: Useful Claude Prompts

| Situation | What to type |
|-----------|-------------|
| Something broke | `I got this error: [paste it]. Fix it.` |
| Want to understand code | `Explain agent_b.py line by line in plain English` |
| Want a new feature | `Add [feature] to [file]. Here's what it should do: [describe it]` |
| Want to test something | `How do I test that Agent B is actually air-gapped?` |
| Want to go further | `What's the next most useful thing to add to this bot?` |

---

*Built with Sculpture — github.com/Prajhan26/sculpture-plugin*
*"We don't build agents. We sculpt them."*
