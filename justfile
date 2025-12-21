# Dotcana - Lorcana game state engine

set shell := ["bash", "-uc"]

# Use venv python
python := ".venv/bin/python"

# Show available commands
default:
    @just --list

# Clear all output
clear:
    rm -rf output/*
    @echo "Cleared output/"

# Create a matchup from two deck files
# Usage: just match data/decks/bs01.txt data/decks/rp01.txt
match deck1 deck2:
    #!/usr/bin/env bash
    set -euo pipefail

    # Generate 4-char hash from deck filenames
    hash=$(echo "{{deck1}}{{deck2}}" | md5 | cut -c1-4)
    outdir="output/${hash}"

    echo "Creating matchup: ${hash}"
    mkdir -p "${outdir}"

    # Convert decks to dot
    {{python}} data/decks/txt_to_dot.py 1 "{{deck1}}" > "${outdir}/deck1.dot"
    {{python}} data/decks/txt_to_dot.py 2 "{{deck2}}" > "${outdir}/deck2.dot"

    # Create base game.dot (template + decks, unshuffled)
    {{python}} bin/rules-engine.py init "${outdir}"

    echo "  ${outdir}/deck1.dot"
    echo "  ${outdir}/deck2.dot"
    echo "  ${outdir}/game.dot"
    echo "Done. Use: just play ${hash} <seed>"

# Play actions (slash separated). First action is typically a seed (shuffle).
# Usage: just play abc1 99281/a0/b2/c1
play hash actions="":
    #!/usr/bin/env bash
    set -euo pipefail

    base="output/{{hash}}"

    if [[ ! -f "${base}/game.dot" ]]; then
        echo "Error: Matchup {{hash}} not found. Run 'just match' first."
        exit 1
    fi

    # If no actions, show current base state
    if [[ -z "{{actions}}" ]]; then
        echo "Current state: ${base}/game.dot"
        {{python}} bin/rules-engine.py show "${base}/game.dot"
        exit 0
    fi

    # Walk the action path
    current="${base}"
    for action in $(echo "{{actions}}" | tr '/' ' '); do
        current="${current}/${action}"

        if [[ -f "${current}/game.dot" ]]; then
            echo "  [skip] ${current}/game.dot exists"
            continue
        fi

        echo "  [play] ${action} -> ${current}/game.dot"
        {{python}} bin/rules-engine.py "${current}"
    done

    echo "Final state: ${current}/game.dot"
    {{python}} bin/rules-engine.py show "${current}/game.dot"
