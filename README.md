# Google Maps Reviews MCP Server

A simple tool to summarize reviews of a place on Google Maps. Provide the chatbot with the Google Maps link of a place and the number of reviews you want to extract. RAG, save scraped reviews and more features to come!

## Features

- Scrape reviews from Google Maps to summarize
- Save reviews to an Excel file

## Installation

Follow the instructions from this link to install uv package: https://github.com/astral-sh/uv

### Install the project dependencies

```bash
uv sync
```

### Install Playwright dependencies

```bash
playwright install-deps
```

### Usage with Claude Desktop

Add this to your `claude_desktop_config.json`

```json
{
    "mcpServers": {
        "google-maps-reviews": {
            "command": "<path-to-your-venv-python>",
            "args": [
                "<path-to-your-server.py-file>"
            ]
        }
    }
}
```
