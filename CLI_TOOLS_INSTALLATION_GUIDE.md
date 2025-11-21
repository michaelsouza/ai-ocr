# AI CLI Tools - Installation & Version Guide

Complete guide for installing, updating, and tracking versions of Gemini CLI, OpenAI Codex CLI, and Claude Code CLI.

---

## Prerequisites

### Node.js Requirements

Each CLI tool has specific Node.js version requirements. Check the official documentation:
- **Gemini CLI**: [github.com/google-gemini/gemini-cli#requirements](https://github.com/google-gemini/gemini-cli#requirements)
- **Codex CLI**: [github.com/openai/codex#requirements](https://github.com/openai/codex#requirements)
- **Claude Code**: [github.com/anthropics/claude-code#requirements](https://github.com/anthropics/claude-code#requirements)

**General recommendation**: Use the latest Node.js LTS version.

### Installing Node.js with nvm (recommended)

```bash
# Install nvm (check https://github.com/nvm-sh/nvm for latest instructions)
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/master/install.sh | bash

# Or visit: https://github.com/nvm-sh/nvm#installing-and-updating

# Install latest Node.js LTS
nvm install --lts
nvm alias default node

# Verify
node --version
npm --version
```

---

## Quick Installation

### Install All Three Tools
```bash
npm install -g @google/gemini-cli@latest @openai/codex@latest @anthropic-ai/claude-code@latest
```

### Verify Installations
```bash
gemini --version
codex --version
claude --version
```

---

## Individual Tool Details

### Gemini CLI (Google)
```bash
# Install latest
npm install -g @google/gemini-cli@latest

# Check current version
gemini --version
npm view @google/gemini-cli version
```

**Where to Find Version Information:**
- **GitHub Releases**: [github.com/google-gemini/gemini-cli/releases](https://github.com/google-gemini/gemini-cli/releases) - Latest stable, preview, and nightly releases
- **npm Package**: [npmjs.com/package/@google/gemini-cli](https://www.npmjs.com/package/@google/gemini-cli) - Current published version
- **Documentation**: [google-gemini.github.io/gemini-cli](https://google-gemini.github.io/gemini-cli/) - Official docs and changelog

**Release Channels:**
- `@latest` - Stable releases (Weekly Tuesdays 20:00 UTC)
- `@preview` - Preview releases (Weekly Tuesdays 23:59 UTC)
- `@nightly` - Nightly builds (Daily 00:00 UTC)

---

### OpenAI Codex CLI
```bash
# Install latest
npm install -g @openai/codex@latest

# Check current version
codex --version
npm view @openai/codex version
```

**Where to Find Version Information:**
- **GitHub Releases**: [github.com/openai/codex/releases](https://github.com/openai/codex/releases) - Official release announcements and notes
- **npm Package**: [npmjs.com/package/@openai/codex](https://www.npmjs.com/package/@openai/codex) - Current version and stats
- **Official Changelog**: [developers.openai.com/codex/changelog](https://developers.openai.com/codex/changelog/) - Detailed version history
- **Documentation**: [developers.openai.com/codex/cli](https://developers.openai.com/codex/cli) - Installation and usage guides

---

### Claude Code CLI (Anthropic)
```bash
# Install latest
npm install -g @anthropic-ai/claude-code@latest

# Check current version
claude --version
npm view @anthropic-ai/claude-code version
```

**Where to Find Version Information:**
- **CHANGELOG.md**: [github.com/anthropics/claude-code/blob/main/CHANGELOG.md](https://github.com/anthropics/claude-code/blob/main/CHANGELOG.md) - **Primary source** (no GitHub Releases)
- **npm Package**: [npmjs.com/package/@anthropic-ai/claude-code](https://www.npmjs.com/package/@anthropic-ai/claude-code) - Current version
- **Third-party**: [claudelog.com/claude-code-changelog](https://claudelog.com/claude-code-changelog/) - User-friendly changelog viewer

**Note**: Anthropic uses CHANGELOG.md instead of GitHub Releases for version tracking.

---

## Version Management

### Check Current Versions
```bash
# Check installed versions
gemini --version
codex --version
claude --version

# Check latest available on npm
npm view @google/gemini-cli version
npm view @openai/codex version
npm view @anthropic-ai/claude-code version

# Check if updates are available
npm outdated -g @google/gemini-cli @openai/codex @anthropic-ai/claude-code
```

### Update Tools
```bash
# Update all to latest
npm update -g @google/gemini-cli @openai/codex @anthropic-ai/claude-code

# Or update individually
npm update -g @google/gemini-cli
npm update -g @openai/codex
npm update -g @anthropic-ai/claude-code

# Force reinstall latest version
npm install -g @google/gemini-cli@latest
npm install -g @openai/codex@latest
npm install -g @anthropic-ai/claude-code@latest
```

### Check Detailed Package Info
```bash
# See full package metadata (version, publish date, dependencies)
npm view @google/gemini-cli
npm view @openai/codex
npm view @anthropic-ai/claude-code
```

---

## Staying Updated

### GitHub Notifications

Watch repositories for new releases:
1. Visit the repository
2. Click "Watch" → "Custom" → Check "Releases"
3. Get notified when new versions are published

- [google-gemini/gemini-cli](https://github.com/google-gemini/gemini-cli)
- [openai/codex](https://github.com/openai/codex)
- [anthropics/claude-code](https://github.com/anthropics/claude-code)

### RSS Feeds

Subscribe to release feeds in your RSS reader:
```
Gemini:  https://github.com/google-gemini/gemini-cli/releases.atom
Codex:   https://github.com/openai/codex/releases.atom
Claude:  https://github.com/anthropics/claude-code/commits/main.atom
```

### Automated Version Checks

Create a script to check for updates:
```bash
#!/bin/bash
# check-cli-updates.sh

echo "=== Installed Versions ==="
echo "Gemini: $(gemini --version 2>&1 | head -1)"
echo "Codex:  $(codex --version 2>&1 | head -1)"
echo "Claude: $(claude --version 2>&1 | head -1)"
echo ""
echo "=== Latest on npm ==="
echo "Gemini: $(npm view @google/gemini-cli version)"
echo "Codex:  $(npm view @openai/codex version)"
echo "Claude: $(npm view @anthropic-ai/claude-code version)"
echo ""
echo "=== Checking for updates ==="
npm outdated -g @google/gemini-cli @openai/codex @anthropic-ai/claude-code
```

---

## Troubleshooting

### Node.js version too old

**Symptom**: "Invalid regular expression flags" or SyntaxError

**Solution**:
```bash
# Update to latest Node.js LTS
nvm install --lts
nvm use --lts
nvm alias default node

# Reinstall CLI tools
npm install -g @google/gemini-cli@latest @openai/codex@latest @anthropic-ai/claude-code@latest
```

### Command not found after installation

**Symptom**: `command not found: gemini` (or codex/claude)

**Solution**:
```bash
# Check npm global bin directory
npm config get prefix

# Add to PATH in ~/.bashrc or ~/.zshrc
export PATH="$PATH:$(npm config get prefix)/bin"

# Reload shell configuration
source ~/.bashrc  # or source ~/.zshrc
```

### Permission errors during installation

**Best solution**: Use nvm instead of system Node.js

**Alternative**:
```bash
# Configure npm to use user directory
mkdir ~/.npm-global
npm config set prefix '~/.npm-global'

# Add to PATH in ~/.bashrc or ~/.zshrc
export PATH="~/.npm-global/bin:$PATH"

# Reload and reinstall
source ~/.bashrc
npm install -g @google/gemini-cli@latest @openai/codex@latest @anthropic-ai/claude-code@latest
```

### npm prefix conflicts with nvm

**Solution**:
```bash
nvm use --delete-prefix node
```

---

## Quick Reference

### Package Names
| Tool | npm Package | Primary Version Source |
|------|-------------|------------------------|
| **Gemini CLI** | `@google/gemini-cli` | [GitHub Releases](https://github.com/google-gemini/gemini-cli/releases) |
| **Codex CLI** | `@openai/codex` | [GitHub Releases](https://github.com/openai/codex/releases) |
| **Claude Code** | `@anthropic-ai/claude-code` | [CHANGELOG.md](https://github.com/anthropics/claude-code/blob/main/CHANGELOG.md) |

### Essential Commands
```bash
# Install all
npm install -g @google/gemini-cli@latest @openai/codex@latest @anthropic-ai/claude-code@latest

# Update all
npm update -g @google/gemini-cli @openai/codex @anthropic-ai/claude-code

# Check versions
gemini --version && codex --version && claude --version

# Check for updates
npm outdated -g

# Uninstall all
npm uninstall -g @google/gemini-cli @openai/codex @anthropic-ai/claude-code
```

---

## Additional Resources

### Official Documentation
- **Gemini CLI**: [google-gemini.github.io/gemini-cli](https://google-gemini.github.io/gemini-cli/)
- **Codex CLI**: [developers.openai.com/codex/cli](https://developers.openai.com/codex/cli)
- **Claude Code**: [github.com/anthropics/claude-code](https://github.com/anthropics/claude-code)

### Issue Trackers
- **Gemini CLI**: [github.com/google-gemini/gemini-cli/issues](https://github.com/google-gemini/gemini-cli/issues)
- **Codex CLI**: [github.com/openai/codex/issues](https://github.com/openai/codex/issues)
- **Claude Code**: [github.com/anthropics/claude-code/issues](https://github.com/anthropics/claude-code/issues)
