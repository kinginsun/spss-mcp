# SPSS Studio MCP (macOS + Windows)

> Turn IBM SPSS Statistics into an Agent-ready stats engine and chart factory.

**English** ｜ [简体中文](README.md)

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)]()
[![Platform](https://img.shields.io/badge/platform-macOS%20%7C%20Windows-blue.svg)]()

An MCP server for **IBM SPSS Statistics**, usable from Cursor / Claude Code / Codex.

This repository is a fork of [`flupke91/spss-studio-mcp`](https://github.com/flupke91/spss-studio-mcp) (MIT) with **macOS / SPSS 27+** engine detection, XD startup fixes, JPEG→PNG chart normalization, path handling, and parser fixes. Verified on **macOS + IBM SPSS Statistics 27**.

## Highlights

- Paper-ready charts (`spss_chart_*`, PNG/TIFF/EMF @300 dpi)
- Deep OMS result parsing (Markdown + JSON + statistical summaries)
- Broad method coverage (t-tests, ANOVA, regression, survival, mixed models, mediation/moderation, …)
- Safety layer (dangerous syntax blocklist, path allowlist, `dry_run`, audit log)
- Cross-platform engine (Windows `stats.exe` and macOS app-bundle + bundled Python3 XD)

## Quick start (macOS)

```bash
pip install -e ".[dev]"
spss-studio-mcp status
```

Optional:

```bash
SPSS_INSTALL_PATH=/Applications/IBM SPSS Statistics 27
```

Cursor `~/.cursor/mcp.json`:

```json
{
  "mcpServers": {
    "spss-studio": {
      "command": "spss-studio-mcp",
      "args": ["serve", "--transport", "stdio"],
      "env": {
        "SPSS_INSTALL_PATH": "/Applications/IBM SPSS Statistics 27"
      }
    }
  }
}
```

## License

MIT. Upstream: [`flupke91/spss-studio-mcp`](https://github.com/flupke91/spss-studio-mcp); earlier: `Exekiel179/SPSS-MCP`.
