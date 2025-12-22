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
    .venv/bin/pip install networkx pydot
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
#    or: just shuffle b013 random
shuffle hash seed:
    #!/usr/bin/env bash
    set -euo pipefail

    # Generate random seed if requested
    if [[ "{{seed}}" == "random" ]]; then
        seed=$({{python}} -c "from lib.seed import generate_random_seed; print(generate_random_seed())")
    else
        seed="{{seed}}"
    fi

    # Shuffle and print seed
    result=$({{python}} bin/rules-engine.py shuffle "output/{{hash}}" "${seed}")
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
