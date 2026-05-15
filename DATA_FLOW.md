# Data Flow

This document is for understanding **where your data goes** when you use thread-seed. Privacy-first design means: nothing surprising leaves your machine.

## What lives where

```
┌──────────────────────────────────────────────────────────────┐
│                     YOUR MACHINE                              │
│                                                               │
│  ┌──────────────┐  ┌──────────────┐  ┌────────────────────┐ │
│  │   spine/     │  │    mem/      │  │  journal/          │ │
│  │  (Kuzu graph │  │ (episodic    │  │  (your raw text)   │ │
│  │  + LanceDB)  │  │  frames)     │  │                    │ │
│  └──────┬───────┘  └──────┬───────┘  └─────────┬──────────┘ │
│         │                 │                     │             │
│         │     ┌───────────▼─────────────┐      │             │
│         └────►│   Claude Code (CLI)     │◄─────┘             │
│               │   reads + writes locally │                    │
│               └─────────────┬────────────┘                    │
│                             │                                 │
│  ┌──────────────────────────┼────────────────────────────┐  │
│  │  Bot token in keychain   │                            │  │
│  │  (NEVER in repo)         │                            │  │
│  └──────────────────────────┼────────────────────────────┘  │
│                             │                                 │
└─────────────────────────────┼─────────────────────────────────┘
                              │
              ┌───────────────┴───────────────┐
              ▼                               ▼
   ┌────────────────────┐         ┌────────────────────┐
   │  Anthropic API     │         │  Telegram          │
   │                    │         │                    │
   │  Receives:         │         │  Receives:         │
   │  - your current    │         │  - bot messages    │
   │    prompt          │         │    (your typed     │
   │  - retrieved       │         │    side + bot's    │
   │    context (spine  │         │    responses)      │
   │    excerpts)       │         │                    │
   │                    │         │  Their TOS         │
   │  Their privacy     │         │  applies.          │
   │  policy applies.   │         │                    │
   └────────────────────┘         └────────────────────┘
```

## What leaves your machine

| What | When | Where |
|---|---|---|
| Your current prompt + retrieved context | Each time you query | Anthropic API |
| Bot messages (both directions) | When using Telegram interface | Telegram servers |

That's it.

## What does NOT leave your machine

- The full content of your spine. Ever.
- The full content of your mem. Ever.
- Your journal source files. Ever.
- Your customized CLAUDE.md. Ever.
- Anything in `memory/handoffs/`. Ever.
- The bot token. Ever (it lives in your OS keychain, not a file).

## Storage and retention

- **Your local databases** persist until you delete them. They're files on your disk. Back them up if you care about them.
- **Anthropic** retains API request data per their privacy policy. Read it: https://www.anthropic.com/legal/privacy
- **Telegram** retains messages per their privacy policy. Read it: https://telegram.org/privacy

## Things to know

### About retrieved context

When you query, the system pulls relevant entries from your spine + mem to send alongside your prompt. The amount sent depends on the query — typically a few hundred lines of context max. This is what makes the AI "remember" — but it does mean that whatever's relevant to your current query *does* get sent to Anthropic's API for that one call.

**Implication:** If you have content in your spine/mem you would NEVER want sent to Anthropic, even in aggregated retrieval, don't put it in your spine/mem. Use a separate private notebook for that.

### About bot tokens

The Telegram bot token is the credential for your bot. If someone else gets it, they can impersonate it. Store it in your OS keychain, never in a file in this repo.

### About journal import

If you run `scripts/journal_import.py` on your existing journal, the script reads your journal locally and makes Claude API calls to extract entities + frames. **Your journal text DOES get sent to the Claude API during import**, in chunks. If you don't want that, don't run the import; populate substrate manually instead.

## Reversibility

Everything here is reversible:
- Delete spine + mem → start fresh
- Revoke bot token via @BotFather → that bot identity is dead
- Uninstall Claude Code → no remote state to clean up
- Delete the repo → nothing left

There's no cloud account to delete. There's no remote subscription tied to your substrate. The seed runs locally; you own all of it.
