#!/bin/bash
# Usage: run-codex-leetcode.sh <problem-number> [extra-context-file]
# Runs codex exec with the leetcode prompt template.
# Exit code 0 = success, 1 = failure.
# Stdout: codex result text (if any).

set -euo pipefail

PROBLEM_NUM="${1:?Usage: run-codex-leetcode.sh <problem-number> [extra-context-file]}"
EXTRA_CONTEXT_FILE="${2:-}"

REPO_DIR="$HOME/note"
PROMPT_TEMPLATE="$REPO_DIR/00_system/prompts/leetcode.md"
RESULT_FILE="/tmp/codex-result-q${PROBLEM_NUM}.txt"

# Build prompt: template with variable substitution
PROMPT=$(sed "s/q{{today-problem-number}}/q${PROBLEM_NUM}/g" "$PROMPT_TEMPLATE")

# Append extra context (for Hard problems: editorial, best solutions, etc.)
if [[ -n "$EXTRA_CONTEXT_FILE" && -f "$EXTRA_CONTEXT_FILE" ]]; then
    PROMPT="${PROMPT}

$(cat "$EXTRA_CONTEXT_FILE")"
fi

# Clean previous result
rm -f "$RESULT_FILE"

# Run codex exec - NO pty, NO --json, NO stdin pipe, NO wrapper
cd "$REPO_DIR"

# Write prompt to temp file to avoid shell escaping issues
PROMPT_FILE="/tmp/leetcode-codex-prompt-q${PROBLEM_NUM}.txt"
printf '%s' "$PROMPT" > "$PROMPT_FILE"

codex exec --full-auto --ephemeral -o "$RESULT_FILE" "$(cat "$PROMPT_FILE")"
EXIT_CODE=$?

# Check success criteria
if [[ $EXIT_CODE -eq 0 ]]; then
    echo "CODEX_SUCCESS: exit code 0"
    exit 0
fi

if [[ -s "$RESULT_FILE" ]]; then
    echo "CODEX_SUCCESS: result file has content (exit code was $EXIT_CODE)"
    exit 0
fi

CHANGED=$(git -C "$REPO_DIR" diff --name-only 2>/dev/null | head -5)
if [[ -n "$CHANGED" ]]; then
    echo "CODEX_SUCCESS: git has changes (exit code was $EXIT_CODE)"
    echo "$CHANGED"
    exit 0
fi

echo "CODEX_FAILED: exit code $EXIT_CODE, no result file, no git changes"
exit 1
