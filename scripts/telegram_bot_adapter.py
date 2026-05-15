#!/usr/bin/env python3
"""
telegram_bot_adapter.py — bridges Telegram messages to local Claude Code.

User DMs the Telegram bot from their phone. Bot adapter receives the
message, routes it to a local Claude Code invocation that has access
to spine + mem, returns the response to the user via Telegram.

This is a STUB. Fill in the bot token loading (from keychain, NEVER from
a file in this repo), the message routing to Claude Code (via shell out
or Claude API directly), and the response delivery.

Privacy notes:
- Bot token comes from OS keychain, NEVER from a config file
- Messages route through Telegram's servers (this is unavoidable for the
  bot interface; see DATA_FLOW.md)
- Allow-list which Telegram user IDs can interact with the bot (default:
  only the owner). Bots are public by default — restrict on first run.
"""

import os
import sys
import subprocess


def load_bot_token_from_keychain() -> str:
    """
    Load bot token from OS keychain. macOS implementation:
        security find-generic-password -a "thread-bot" -s "telegram-token" -w

    Linux: use libsecret via secret-tool or similar.
    Returns the token string. Raises if not found.
    """
    # TODO: implement keychain access for current OS
    raise NotImplementedError("Fill in keychain access for your OS")


def authorized_users() -> set[int]:
    """
    Allow-list of Telegram user IDs permitted to interact with this bot.
    Configure via local config or environment, NEVER hardcoded in repo.
    Default empty = bot refuses everyone until configured.
    """
    raw = os.environ.get("THREAD_BOT_ALLOWED_USERS", "")
    return {int(x) for x in raw.split(",") if x.strip().isdigit()}


def route_to_claude(message_text: str) -> str:
    """
    Route an incoming message to Claude Code locally and return the response.

    Two viable patterns:
    1. `claude -p "..."` with --output-format=text (one-shot, fresh context)
    2. Persistent Claude Code session via tmux + capture (continuity, more setup)

    Pattern 1 is simpler to start with. Pattern 2 gives the
    consistent-running-instance property that makes substrate feel alive.
    """
    # TODO: implement
    raise NotImplementedError("Choose pattern 1 or 2, implement accordingly")


def main():
    """
    Run the bot. Long-running process; consider running under systemd / launchd
    so it restarts on reboot.

    Skeleton:
        bot = telegram.Bot(token=load_bot_token_from_keychain())
        allowed = authorized_users()
        async for update in bot.poll_updates():
            if update.from_user.id not in allowed:
                continue
            response = route_to_claude(update.message.text)
            await bot.send_message(update.chat.id, response)
    """
    # TODO: pick a Telegram library (python-telegram-bot, aiogram, etc.)
    # and implement the update loop
    print("STUB: telegram_bot_adapter not yet implemented")
    print("See module docstring for design.")


if __name__ == "__main__":
    main()
