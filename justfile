# Dotcana - Lorcana game state engine

set shell := ["bash", "-uc"]

# Use venv python
python := ".venv/bin/python"

# Show available commands
default:
    @just --list

# Set up development environment
setup:
    python3 -m venv .venv
    .venv/bin/pip install --upgrade pip
    .venv/bin/pip install networkx pydot flask
    @echo "Environment ready. Dependencies installed."

# Clear all output
clear:
    rm -rf output/*
    @echo "Cleared output/"

# Create a matchup from two deck files
# Usage: just match data/decks/bs01.txt data/decks/rp01.txt
match deck1 deck2:
    #!/usr/bin/env bash
    set -euo pipefail

    # rules-engine generates hash from deck contents and returns it
    hash=$({{python}} bin/rules-engine.py init "{{deck1}}" "{{deck2}}")

    echo "Created matchup: ${hash}"
    echo "  output/${hash}/deck1.txt"
    echo "  output/${hash}/deck2.txt"
    echo "  output/${hash}/game.dot"
    echo "Done. Use: just show ${hash}"

# Shuffle decks and draw starting hands
# Usage: just shuffle b013 "0123456.abcdefg.xy"
shuffle hash seed:
    #!/usr/bin/env bash
    set -euo pipefail

    # Shuffle and print seed
    result=$({{python}} bin/rules-engine.py shuffle "output/{{hash}}" "{{seed}}")
    echo "Shuffled: ${result}"
    echo "  output/{{hash}}/${result}/deck1.dek"
    echo "  output/{{hash}}/${result}/deck2.dek"
    echo "  output/{{hash}}/${result}/game.dot"
    echo "Done. Use: just show {{hash}} ${result}"

# Show game state and available actions
# Usage: just show b013 [seed]
show hash seed="":
    #!/usr/bin/env bash
    if [[ -z "{{seed}}" ]]; then
        {{python}} bin/rules-engine.py show "output/{{hash}}/game.dot"
    else
        {{python}} bin/rules-engine.py show "output/{{hash}}/{{seed}}/game.dot"
    fi

# Navigate to state and apply action if needed
# Usage: just play output/b013/b123456.0123456.ab/i49/
play path:
    {{python}} bin/rules-engine.py play "{{path}}"

# Start web viewer
# Usage: just serve
serve:
    @echo "Starting web viewer at http://localhost:5000"
    @echo "Press Ctrl+C to stop"
    {{python}} web/app.py

# Set up deterministic test game
test:
    #!/usr/bin/env bash
    set -euo pipefail

    just clear
    just match data/decks/bs01.txt data/decks/rp01.txt >/dev/null
    just shuffle b013 "b123456.0123456.ab" >/dev/null
    just play output/b013/b123456.0123456.ab/i49 >/dev/null
    just play output/b013/b123456.0123456.ab/i49/e35 >/dev/null

    echo "Test game ready:"
    echo "  just play output/b013/b123456.0123456.ab/i49/e35"
