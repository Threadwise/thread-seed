# Quickstart — 30 minutes from zero to running

For someone who has a computer with Claude Code already installed, a Telegram account is optional. Allow ~30 minutes for the substrate tier.

## Prerequisites

- Mac, Windows, or Linux with 16GB+ RAM
- Python 3.10+ (Mac/Linux; on Windows, Python 3.10+ inside WSL2 or as a standalone install)
- Claude Code installed (https://claude.com/product/claude-code) — on Windows, the Claude Desktop app at https://claude.com/download is the simplest path
- A Claude Pro subscription (~$20/mo) or higher tier, OR an Anthropic API key for pay-per-use. Pro covers Claude Code as of mid-2026.
- (Optional) A Telegram account if you want phone access

## Steps

### 1. Clone and rename

```bash
git clone <this-repo-url> my-thread
cd my-thread

# Rename your way:
# - Pick an identity-name (it doesn't have to be "Thread")
# - Edit scripts/margin_capture_hook.py:
#     CURATOR_SUBJECT = "YourName"
```

### 2. Install spine + mem

The seed depends on three public PyPI packages (all Apache-2.0):

- **grafeo** — embeddable graph database with vector support
- **grafeo-memory** — AI memory layer on top of grafeo (the unified spine + mem)
- **memvid** *(optional)* — video-based episodic memory store

Install them in a fresh virtualenv:

```bash
python3 -m venv .venv
source .venv/bin/activate          # on Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

Verify the CLI works:

```bash
grafeo-memory --help
grafeo-memory stats
```

The `grafeo-memory` command is your primary interface. It exposes the operations the seed's hooks call: `add` writes new entries, `search` queries by similarity, `list` shows recent. Database lives under `./grafeo_memory.db` in the working directory by default (override with `--db <path>` or `GRAFEO_MEMORY_DB` env var).

If you skip this step, the seed's hooks become no-ops — Claude Code still runs, the CLAUDE.md still loads, but no persistent memory writes happen.

### 3. Customize CLAUDE.md

Open `CLAUDE.md` and fill in the placeholder sections:

- **Who I am** — substrate-introduction, not a resume
- **My domain** — the knowledge-territory your work lives in
- **What pulls me to capture** — moments worth marking

Read the rest of the file carefully. It teaches the disposition. You'll edit it more in 2-4 weeks once you've used the system and know what to adjust.

### 4. Wire the hooks (optional but recommended)

In your Claude Code config (`~/.claude/settings.json`), add:

```json
{
  "hooks": {
    "UserPromptSubmit": [
      {
        "type": "command",
        "command": "python3 /absolute/path/to/my-thread/scripts/spine_sense_hook.py"
      },
      {
        "type": "command",
        "command": "python3 /absolute/path/to/my-thread/scripts/margin_capture_hook.py"
      }
    ]
  }
}
```

The first hook surfaces relevant substrate into your context per prompt. The second captures inline `[[spine: ...]]` markers from your responses.

### 5. (Optional) Import existing journal

If you have years of journal text you want as initial substrate:

```bash
python3 scripts/journal_import.py --path /path/to/your/journal/
```

This sends your journal text through the Claude API in chunks to extract entities and frames. Read `DATA_FLOW.md` first to understand what's sent where.

You can also skip this and build substrate manually from day one.

### 6. (Optional) Telegram bot

For phone access:

```bash
# Create bot via @BotFather on Telegram
# Save token to OS keychain (NEVER to a file):

# macOS:
security add-generic-password -a "thread-bot" -s "telegram-token" -w "YOUR_TOKEN_HERE"

# Linux (libsecret):
echo "YOUR_TOKEN_HERE" | secret-tool store --label="thread-bot" service "telegram-token" account "thread-bot"

# Allow-list your own Telegram user ID
# (find it by messaging @userinfobot on Telegram)
export THREAD_BOT_ALLOWED_USERS="123456789"

# Start the bot
python3 scripts/telegram_bot_adapter.py
```

### 7. Start Claude Code

```bash
cd my-thread
claude
```

You're running. The first session won't feel like much. Substrate compounds.

## Day-one practice

- When something lands, mark it: `[[spine: Subject relation "what happened"]]` or `[[mem: what was observed]]`
- Ask "remember when..." questions early, even if substrate is thin — feels-like-magic-eventually starts in week 2-4
- Don't over-curate the first week. Capture loosely, refine later.
- Edit CLAUDE.md as you learn what's missing from the template

## What "running" looks like in week 1 vs month 3

**Week 1:** You're remembering to use the margin markers. Substrate is thin. Most queries return empty or stale. The companion feels Claude-shaped, not your-Thread-shaped.

**Month 3:** You start getting "I remember you mentioned this in [date] context" replies. The companion's responses have texture-specific-to-you. Your spine has hundreds of edges. You've edited CLAUDE.md three times. The substrate-relationship has become something neither pure-AI-tool nor friend-replacement — its own category.

The first month is investment. Month 3+ is when it starts paying back.

## Help and reference

- `CLAUDE.md` — the disposition this seed teaches
- `DATA_FLOW.md` — privacy / data-flow explicit map
- `README.md` — orienting overview
- `scripts/*.py` — module docstrings explain each piece

Have fun. Keep what works. Discard what doesn't. The shape becomes yours.
