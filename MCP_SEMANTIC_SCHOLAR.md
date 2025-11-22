# Semantic Scholar MCP Setup for Claude Code

**Environment:** ChromeOS (Crostini)
**User:** Michael

This guide details how to install and register the Semantic Scholar Model Context Protocol (MCP) server so Claude Code can access academic papers directly.

## 1\. Prerequisites

Ensure you are in your Git repositories folder and your central virtual environment is active.

```bash
# Navigate to your repos
cd /home/michael/gitrepos

# Clone the server repository (if not already done)
git clone https://github.com/benhaotang/mcp-semantic-scholar-server.git semantic-mcp

# Enter the directory
cd semantic-mcp
```

## 2\. Install Dependencies

We need to install the required Python libraries into your specific virtual environment (`.venv`).

```bash
/home/michael/.venv/bin/python -m pip install -r requirements.txt
```

## 3\. Register with Claude Code

Use the `claude mcp add` command to register the tool.

**Note:** The syntax uses a double dash (`--`) to separate the MCP server name from the command Claude needs to execute.

### Option A: Basic Setup (No API Key)

Use this if you just want to test it out.

```bash
claude mcp add semantic-scholar -- /home/michael/.venv/bin/python /home/michael/gitrepos/semantic-mcp/semantic-scholar-plugin.py
```

### Option B: With API Key (Recommended)

Use this to avoid rate limits. Replace `YOUR_KEY` with your actual key.

```bash
claude mcp add semantic-scholar --env SEMANTIC_SCHOLAR_API_KEY=YOUR_KEY -- /home/michael/.venv/bin/python /home/michael/gitrepos/semantic-mcp/semantic-scholar-plugin.py
```

## 4\. Verification

1.  Start Claude Code:
    ```bash
    claude
    ```
2.  Type `/mcp` to view installed servers. You should see `semantic-scholar` listed with a green status.

## 5\. Usage Examples

Once installed, you can ask natural language questions about research:

  * *"Find the most cited papers on 'Chain of Thought' prompting from 2024."*
  * *"Summarize the abstract of the paper with ID [Paper ID]."*
  * *"Who are the co-authors on the latest paper by [Author Name]?"*

-----

## Troubleshooting

  * **"Command not found":** Ensure you are using the absolute paths provided in the commands above (`/home/michael/...`).
  * **"Permission denied":** Run `chmod +x semantic-scholar-plugin.py` in the repository folder.
  * **Rate Limits:** If Claude fails to fetch data frequently, you likely need to register for a free API key and reinstall using **Option B**.

-----

Would you like me to generate a quick test prompt you can paste into Claude to verify it's pulling real data?