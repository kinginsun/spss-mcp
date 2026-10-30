import json
from pathlib import Path

from spss_mcp import cursor_config


def test_configure_cursor_creates_new_mcp_json(monkeypatch, tmp_path):
    monkeypatch.setattr(
        cursor_config,
        "build_cursor_mcp_entry",
        lambda prefer_uvx=True: {
            "command": "uvx",
            "args": ["spss-mcp", "serve", "--transport", "stdio"],
            "env": {
                "SPSS_INSTALL_PATH": "/Applications/IBM SPSS Statistics 27",
                "SPSS_TIMEOUT": "120",
                "SPSS_STARTUP_TIMEOUT": "300",
            },
        },
    )

    config_path = tmp_path / "mcp.json"
    result = cursor_config.configure_cursor_settings(config_path)

    saved = json.loads(config_path.read_text(encoding="utf-8"))
    assert result["status"] == "created"
    assert result["backup_path"] is None
    assert saved["mcpServers"]["spss-mcp"]["command"] == "uvx"
    assert saved["mcpServers"]["spss-mcp"]["args"][0] == "spss-mcp"


def test_configure_cursor_merges_and_drops_legacy_keys(monkeypatch, tmp_path):
    monkeypatch.setattr(
        cursor_config,
        "build_cursor_mcp_entry",
        lambda prefer_uvx=True: {
            "command": "spss-mcp",
            "args": ["serve", "--transport", "stdio"],
            "env": {"SPSS_INSTALL_PATH": "/Applications/IBM SPSS Statistics 27"},
        },
    )

    config_path = tmp_path / "mcp.json"
    config_path.write_text(
        json.dumps(
            {
                "mcpServers": {
                    "other": {"command": "node", "args": ["x.js"]},
                    "spss-studio": {"command": "old"},
                    "spss-mcp": {"command": "stale"},
                }
            },
            indent=2,
        ),
        encoding="utf-8",
    )

    result = cursor_config.configure_cursor_settings(config_path, prefer_uvx=False)
    saved = json.loads(config_path.read_text(encoding="utf-8"))

    assert result["status"] == "updated"
    assert result["backup_path"] is not None
    assert Path(result["backup_path"]).exists()
    assert saved["mcpServers"]["other"]["command"] == "node"
    assert saved["mcpServers"]["spss-mcp"]["command"] == "spss-mcp"
    assert "spss-studio" not in saved["mcpServers"]


def test_build_cursor_mcp_entry_prefers_uvx(monkeypatch):
    monkeypatch.setattr(cursor_config.shutil, "which", lambda name: "/usr/bin/uvx")
    monkeypatch.setattr(
        cursor_config,
        "detect_capabilities",
        lambda: {"spss_install_root": "/Applications/IBM SPSS Statistics 27"},
    )
    monkeypatch.setattr(cursor_config, "get_timeout", lambda: 120)
    monkeypatch.setattr(cursor_config, "get_startup_timeout", lambda: 300)

    entry = cursor_config.build_cursor_mcp_entry(prefer_uvx=True)
    assert entry["command"] == "uvx"
    assert entry["args"] == ["spss-mcp", "serve", "--transport", "stdio"]
    assert (
        entry["env"]["SPSS_INSTALL_PATH"]
        == "/Applications/IBM SPSS Statistics 27"
    )
