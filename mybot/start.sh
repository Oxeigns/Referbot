#!/bin/bash
# Ensure script runs from repository root
cd "$(dirname "$0")"/..

# Launch the bot using module notation so package imports resolve
python3 -m mybot.main
