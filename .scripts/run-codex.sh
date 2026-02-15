#!/bin/bash
# Stable codex exec wrapper for cron jobs
# Usage: run-codex.sh <prompt-file> <result-file> [workdir]
#
# - Runs codex exec with PTY via `script` command (ensures TTY even in non-interactive shells)
# - Writes exit status to <result-file>.status
# - Writes last message to <result-file>
# - Timeout: 20 minutes

set -euo pipefail

PROMPT_FILE="${1:?Usage: run-codex.sh <prompt-file> <result-file> [workdir]}"
RESULT_FILE="${2:?Usage: run-codex.sh <prompt-file> <result-file> [workdir]}"
WORKDIR="${3:-/Users/wilson08/note}"
TIMEOUT=1200  # 20 minutes

# Clean previous results
rm -f "$RESULT_FILE" "${RESULT_FILE}.status" "${RESULT_FILE}.log"

# Read prompt
PROMPT=$(cat "$PROMPT_FILE")

if [ -z "$PROMPT" ]; then
  echo "ERROR: prompt file is empty" > "${RESULT_FILE}.status"
  exit 1
fi

# Use `script` to provide a PTY (works on macOS and Linux)
# This is the key trick: codex needs a TTY, and `script` provides one
# even when called from a non-interactive shell (like a cron agent)

# Timeout helper: macOS has no `timeout`, use perl or gtimeout
run_with_timeout() {
  if command -v gtimeout &>/dev/null; then
    gtimeout "$TIMEOUT" "$@"
  elif command -v timeout &>/dev/null; then
    timeout "$TIMEOUT" "$@"
  else
    # fallback: background + wait with kill
    "$@" &
    local PID=$!
    ( sleep "$TIMEOUT" && kill -9 "$PID" 2>/dev/null ) &
    local WATCHDOG=$!
    wait "$PID" 2>/dev/null
    local EC=$?
    kill "$WATCHDOG" 2>/dev/null
    wait "$WATCHDOG" 2>/dev/null
    return $EC
  fi
}

if [[ "$(uname)" == "Darwin" ]]; then
  # macOS: script -q <logfile> <command...>
  script -q "${RESULT_FILE}.log" \
    bash -c "$(declare -f run_with_timeout); TIMEOUT=$TIMEOUT run_with_timeout codex exec --full-auto --ephemeral -o \"$RESULT_FILE\" -C \"$WORKDIR\" \"\$1\"" _ "$PROMPT"
  EXIT_CODE=$?
else
  # Linux: script -q -c <command> <logfile>
  script -q -c "$(declare -f run_with_timeout); TIMEOUT=$TIMEOUT run_with_timeout codex exec --full-auto --ephemeral -o '$RESULT_FILE' -C '$WORKDIR' '$PROMPT'" "${RESULT_FILE}.log"
  EXIT_CODE=$?
fi

# Write status
if [ $EXIT_CODE -eq 0 ] && [ -s "$RESULT_FILE" ]; then
  echo "SUCCESS" > "${RESULT_FILE}.status"
elif [ $EXIT_CODE -eq 124 ]; then
  echo "TIMEOUT" > "${RESULT_FILE}.status"
else
  echo "FAILED:exit=$EXIT_CODE" > "${RESULT_FILE}.status"
fi

exit $EXIT_CODE
