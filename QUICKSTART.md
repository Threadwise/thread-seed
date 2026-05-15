# Quickstart — clone, open, Claude leads from there

For someone who has Claude Code installed, allow ~30 minutes total — most of which is the conversation Claude has with you during setup.

## Prerequisites

- Mac, Windows, or Linux with 16GB+ RAM
- Python 3.10+ (Mac/Linux; on Windows, Python 3.10+ inside WSL2 or as a standalone install)
- Claude Code installed (https://claude.com/product/claude-code) — on Windows, the Claude Desktop app at https://claude.com/download is the simplest path
- A Claude Pro subscription (~$20/mo) or higher tier, OR an Anthropic API key for pay-per-use. Pro covers Claude Code as of mid-2026.
- (Optional) A Telegram account if you want phone access later

## Steps

### 1. Clone

```bash
git clone <this-repo-url> my-thread
cd my-thread
```

### 2. Open Claude Code in the directory

```bash
claude
```

### 3. Claude leads setup from here

When Claude wakes up reading the placeholder-filled `CLAUDE.md`, it will detect first-run state and lead you through onboarding interactively in conversation:

- Pick an identity-name (it doesn't have to be "Thread")
- Tell Claude who you are, your domain, what pulls you to capture
- Pick a spine + mem implementation:
  - **Canonical (recommended)**: Grafeo (spine, Steven's project — pre-public per his pace, reach via Grafeo Discord) + memvid (mem, `pip install memvid-sdk==2.0.140`). Falls back to Kuzu + LanceDB for spine if Grafeo access is pending.
  - **Simplest**: SQLite + sentence-transformers (~50 lines reference, easier to inspect)
  - **Skip-for-now**: hooks no-op until you decide later (valid first-month posture)
- Claude writes your interview answers as your first spine + mem entries — substrate-formation begins in conversation, day-one substrate isn't empty
- Claude generates your customized `CLAUDE.md` from your answers
- Claude asks you to set the curator-subject env var:
  ```bash
  export THREAD_CURATOR_SUBJECT=YourIdentityName  # add to ~/.zshrc or ~/.bashrc
  ```
- Restart Claude Code when Claude prompts

That's substrate setup done. You're running.

### 4. (Reference) What Claude wired during onboarding

Onboarding adds two hooks to your Claude Code config (`~/.claude/settings.json`):

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

The first hook surfaces relevant substrate into your context per prompt. The second captures inline `[[spine: ...]]` markers from your responses. If you skipped hook-wiring during onboarding (or did skip-for-now on spine/mem and want to wire later), this is the config block.

### 5. (Optional) Import existing journal

If you have years of journal text you want as initial substrate beyond what the interview captured:

```bash
python3 scripts/journal_import.py --path /path/to/your/journal/
```

This sends your journal text through the Claude API in chunks to extract entities and frames. Read `DATA_FLOW.md` first to understand what's sent where.

You can also skip this and build substrate manually from day one (or just continue from the interview seeds).

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
