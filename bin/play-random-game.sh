#!/bin/bash
# Play a random game by choosing actions until game over.
# Strategy: Prefer non-'end' actions, only choose 'end' if nothing else.

set -e

state="${1:-output/b013/b123456.0123456.ab}"
path=""

while true; do
  current="$state$path"

  # Ensure state exists
  .venv/bin/python bin/rules-engine.py play "$current" > /dev/null 2>&1 || true

  # Check if actions exist
  if [ ! -f "$current/actions.txt" ] || [ ! -s "$current/actions.txt" ]; then
    break
  fi

  # Get non-'end' actions (grep out lines with ': end')
  non_end=$(grep '^[0-9]\+:' "$current/actions.txt" | grep -v ': end$' | grep -oP '^[0-9]+' || echo "")

  if [ -n "$non_end" ]; then
    # Pick random non-end action
    action=$(echo "$non_end" | shuf -n 1)
  else
    # Only 'end' available, use it
    action=$(grep -oP '^[0-9]+' "$current/actions.txt" | head -n 1)
  fi

  path="$path/$action"
done

echo "just play $state$path"
