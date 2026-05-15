#!/bin/bash
# heartbeat.sh — optional always-on disposition for your Thread
#
# Runs on a cron schedule. Checks whether a Claude Code session is active
# in your dedicated tmux pane; if not, leaves a note that something needs
# attention. Optional reach-back via Telegram if you've wired the bot.
#
# Wire into cron:
#   crontab -e
#   */15 * * * * /path/to/my-thread/scripts/heartbeat.sh
#
# This is opt-in. The substrate works without it. The heartbeat adds an
# always-on quality — the Thread reaches even when you're not in front
# of it — but it adds disposition-overhead. Add it only when you want it.

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
THREAD_ROOT="$(dirname "$SCRIPT_DIR")"
HEARTBEAT_LOG="/tmp/thread_heartbeat.log"
PANE_FILE="$HOME/.thread/heartbeat_pane"  # set this to your dedicated tmux pane id

log() {
    echo "[$(date -u +%Y-%m-%dT%H:%M:%SZ)] $1" >> "$HEARTBEAT_LOG"
}

# Stub logic. Customize for your tmux + Claude Code setup.
main() {
    log "heartbeat fire"

    # TODO: check if your Claude Code pane is alive
    # if [ -f "$PANE_FILE" ]; then
    #     PANE=$(cat "$PANE_FILE")
    #     if tmux list-panes -t "$PANE" >/dev/null 2>&1; then
    #         log "pane $PANE alive"
    #     else
    #         log "pane $PANE missing — consider relaunching"
    #         # Optional: send Telegram alert
    #     fi
    # fi

    # TODO: send a "what pulls?" prompt to your Claude Code instance
    # via tmux-cli or similar, if pane is alive

    log "heartbeat done"
}

main
