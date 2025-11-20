# AI CLI Tools Installation Guide

Complete guide for installing and updating the latest versions of Gemini CLI, OpenAI Codex CLI, and Claude Code CLI.

---

## Table of Contents

- [Prerequisites](#prerequisites)
- [Gemini CLI](#gemini-cli)
- [OpenAI Codex CLI](#openai-codex-cli)
- [Claude Code CLI](#claude-code-cli)
- [Updating All Tools](#updating-all-tools)
- [Troubleshooting](#troubleshooting)

---

## Prerequisites

### Node.js Requirements

All three CLI tools require **Node.js v20 or higher**. We recommend using **nvm (Node Version Manager)** for managing Node.js versions.

#### Installing nvm

```bash
# Install nvm
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.1/install.sh | bash

# Load nvm (or restart your terminal)
export NVM_DIR="$HOME/.config/nvm"
[ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"
```

#### Installing Node.js v24 (Latest LTS)

```bash
# Install Node.js LTS
nvm install --lts

# Set as default
nvm alias default v24

# Verify installation
node --version  # Should show v24.x.x
npm --version   # Should show v11.x.x
```

---

## Gemini CLI

### About
Official Google Gemini CLI - An open-source AI agent that brings the power of Gemini directly into your terminal.

### Latest Version
- **Stable**: v0.16.0 (November 2025)
- **Features**: Gemini 3 support

### Installation

#### Install Latest Stable
```bash
npm install -g @google/gemini-cli@latest
```

#### Install Preview Version
```bash
npm install -g @google/gemini-cli@preview
```

#### Install Nightly Build
```bash
npm install -g @google/gemini-cli@nightly
```

### Verify Installation
```bash
gemini --version
```

### Release Information

**Release Schedule:**
- **Stable releases**: Weekly on Tuesdays at 20:00 UTC
- **Preview releases**: Weekly on Tuesdays at 23:59 UTC
- **Nightly releases**: Daily at 00:00 UTC

**Resources:**
- GitHub Repository: https://github.com/google-gemini/gemini-cli
- Releases Page: https://github.com/google-gemini/gemini-cli/releases
- npm Package: https://www.npmjs.com/package/@google/gemini-cli

### Update to Latest
```bash
npm update -g @google/gemini-cli@latest
```

---

## OpenAI Codex CLI

### About
OpenAI's official coding agent that runs locally on your computer. Included with ChatGPT Plus, Pro, Business, Edu, and Enterprise plans.

### Latest Version
- **Stable**: v0.60.1 (November 19, 2025)
- **Features**: GPT-5.1-Codex-Max model, native compaction support

### Installation

#### Install via npm (Recommended)
```bash
npm install -g @openai/codex@latest
```

#### Install via Homebrew (macOS/Linux)
```bash
brew install --cask codex
```

### Verify Installation
```bash
codex --version
```

### Configuration
Configuration is stored in `~/.codex/config.toml`

### Default Model
- **GPT-5.1-Codex-Max**: Frontier agentic coding model
- Alternative models: gpt-5.1-codex, gpt-5.1-codex-mini

**Resources:**
- GitHub Repository: https://github.com/openai/codex
- Releases Page: https://github.com/openai/codex/releases
- npm Package: https://www.npmjs.com/package/@openai/codex
- Official Docs: https://developers.openai.com/codex/cli
- Changelog: https://developers.openai.com/codex/changelog/

### Update to Latest
```bash
npm update -g @openai/codex@latest
```

---

## Claude Code CLI

### About
Anthropic's official CLI for Claude - An agentic coding tool that lives in your terminal, understands your codebase, and helps you code faster.

### Latest Version
- **Stable**: v2.0.47 (November 20, 2025)
- **Features**: Azure AI Foundry support, PermissionRequest hooks, improved teleport functionality

### Installation

```bash
npm install -g @anthropic-ai/claude-code@latest
```

### Verify Installation
```bash
claude --version
```

### Key Features (2025)
- Automatic checkpoint system (saves code state before changes)
- Subagents, hooks, and background tasks
- MCP "project" scope for repository-level MCP servers
- Thinking mode (`think` or `think harder`)
- Claude Sonnet 4.5 as default model

**Resources:**
- GitHub Repository: https://github.com/anthropics/claude-code
- CHANGELOG: https://github.com/anthropics/claude-code/blob/main/CHANGELOG.md
- npm Package: https://www.npmjs.com/package/@anthropic-ai/claude-code
- Detailed Changelog: https://claudelog.com/claude-code-changelog/

### Update to Latest
```bash
npm update -g @anthropic-ai/claude-code@latest
```

---

## Updating All Tools

### Update All at Once
```bash
npm install -g @google/gemini-cli@latest @openai/codex@latest @anthropic-ai/claude-code@latest
```

### Check All Versions
```bash
echo "Node.js: $(node --version)"
echo "npm: $(npm --version)"
echo "Gemini CLI: $(gemini --version)"
echo "Codex CLI: $(codex --version)"
echo "Claude Code: $(claude --version)"
```

### List All Global Packages
```bash
npm list -g --depth=0
```

---

## Troubleshooting

### Common Issues

#### 1. "Invalid regular expression flags" or SyntaxError

**Problem**: Node.js version is too old (< v20)

**Solution**:
```bash
# Install Node.js v24
nvm install --lts
nvm use --delete-prefix v24
nvm alias default v24

# Reinstall CLI tools
npm install -g @google/gemini-cli@latest @openai/codex@latest @anthropic-ai/claude-code@latest
```

#### 2. npm prefix/globalconfig conflicts with nvm

**Problem**: `.npmrc` file has incompatible settings

**Solution**:
```bash
nvm use --delete-prefix v24
```

#### 3. Command not found after installation

**Problem**: npm global bin directory not in PATH

**Solution**:
```bash
# Find npm global bin directory
npm config get prefix

# Add to PATH (add to ~/.bashrc or ~/.zshrc)
export PATH="$PATH:$(npm config get prefix)/bin"
```

#### 4. Permission errors during installation

**Problem**: Installing globally without proper permissions

**Solution**:
Use nvm (recommended) instead of system Node.js, or:
```bash
# Use npm with --unsafe-perm flag (not recommended)
npm install -g @google/gemini-cli@latest --unsafe-perm

# Better: Configure npm to use different directory
mkdir ~/.npm-global
npm config set prefix '~/.npm-global'
echo 'export PATH=~/.npm-global/bin:$PATH' >> ~/.bashrc
source ~/.bashrc
```

---

## Version Comparison Table

| CLI Tool | Latest Stable | Released | Key Feature |
|----------|---------------|----------|-------------|
| Gemini CLI | v0.16.0 | Nov 2025 | Gemini 3 support |
| Codex CLI | v0.60.1 | Nov 19, 2025 | GPT-5.1-Codex-Max |
| Claude Code | v2.0.47 | Nov 20, 2025 | Checkpoints & Hooks |

---

## Quick Reference

### Installation Commands
```bash
# Install all three
npm install -g @google/gemini-cli@latest @openai/codex@latest @anthropic-ai/claude-code@latest

# Or individually
npm install -g @google/gemini-cli@latest
npm install -g @openai/codex@latest
npm install -g @anthropic-ai/claude-code@latest
```

### Update Commands
```bash
# Update all
npm update -g @google/gemini-cli @openai/codex @anthropic-ai/claude-code

# Or individually
npm update -g @google/gemini-cli
npm update -g @openai/codex
npm update -g @anthropic-ai/claude-code
```

### Uninstall Commands
```bash
# Uninstall all
npm uninstall -g @google/gemini-cli @openai/codex @anthropic-ai/claude-code

# Or individually
npm uninstall -g @google/gemini-cli
npm uninstall -g @openai/codex
npm uninstall -g @anthropic-ai/claude-code
```

---

## Additional Resources

### Learning & Documentation
- **Gemini CLI Docs**: https://google-gemini.github.io/gemini-cli/
- **Codex CLI Docs**: https://developers.openai.com/codex/cli
- **Claude Code Docs**: https://platform.claude.com/docs/en/release-notes/claude-code

### Community & Support
- **Gemini CLI Issues**: https://github.com/google-gemini/gemini-cli/issues
- **Codex CLI Issues**: https://github.com/openai/codex/issues
- **Claude Code Issues**: https://github.com/anthropics/claude-code/issues

---

**Last Updated**: November 20, 2025

**Note**: Version numbers and features are current as of the last update date. Always check the official repositories and npm packages for the most current information.
