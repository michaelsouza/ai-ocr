#!/bin/bash

# Script to update Claude Code CLI, Codex CLI, and Gemini CLI apps
# Run with: bash update-cli-apps.sh

set -e  # Exit on error

echo "==================================="
echo "Updating AI CLI Apps"
echo "==================================="
echo ""

# Update Claude Code CLI
echo "[1/3] Updating Claude Code CLI..."
if command -v claude &> /dev/null; then
    echo "Claude Code found. Current version: $(claude --version 2>/dev/null || echo 'unknown')"
    echo "Updating via npm..."
    npm install -g @anthropic-ai/claude-code@latest
    echo "New version: $(claude --version 2>/dev/null || echo 'unknown')"
else
    echo "Claude Code CLI not found. Skipping."
fi
echo ""

# Update Codex CLI
echo "[2/3] Updating Codex CLI..."
if command -v codex &> /dev/null; then
    echo "Codex CLI found. Current version: $(codex --version 2>/dev/null || echo 'unknown')"

    # Try npm first
    if npm list -g @openai/codex &> /dev/null; then
        echo "Updating via npm..."
        npm install -g @openai/codex@latest
    # Try Homebrew on macOS
    elif command -v brew &> /dev/null && brew list codex &> /dev/null; then
        echo "Updating via Homebrew..."
        brew upgrade codex
    else
        echo "Could not determine installation method. Please update manually."
    fi

    echo "New version: $(codex --version 2>/dev/null || echo 'unknown')"
else
    echo "Codex CLI not found. Skipping."
fi
echo ""

# Update Gemini CLI
echo "[3/3] Updating Gemini CLI..."
if command -v gemini &> /dev/null; then
    echo "Gemini CLI found. Current version: $(gemini --version 2>/dev/null || echo 'unknown')"
    echo "Updating via npm..."
    npm install -g @google/gemini-cli@latest
    echo "New version: $(gemini --version 2>/dev/null || echo 'unknown')"
else
    echo "Gemini CLI not found. Skipping."
fi
echo ""

echo "==================================="
echo "Update process completed!"
echo "==================================="
echo ""
echo "Verify installations:"
echo "  claude --version"
echo "  codex --version"
echo "  gemini --version"
