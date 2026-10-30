"""
Helpers for generating and updating Cursor MCP configuration (~/.cursor/mcp.json).
"""

from __future__ import annotations

import json
import shutil
from datetime import datetime
from pathlib import Path

from spss_mcp.claude_config import get_entrypoint_config
from spss_mcp.config import (
    detect_capabilities,
    get_spss_install_root,
    get_startup_timeout,
    get_timeout,
)


def get_cursor_mcp_path() -> Path:
    """Return the default Cursor user MCP config path."""
    return Path.home() / ".cursor" / "mcp.json"


def build_cursor_mcp_entry(*, prefer_uvx: bool = True) -> dict:
    """Build the Cursor ``mcpServers.spss-mcp`` entry.

    Prefers ``uvx spss-mcp`` when ``uvx`` is on PATH (npx-like, pulls from PyPI).
    Falls back to an installed ``spss-mcp`` console script / ``python -m``.
    """
    caps = detect_capabilities()
    spss_install = (
        caps.get("spss_install_root")
        or get_spss_install_root()
        or "<replace-with-your-spss-install-dir>"
    )
    env = {
        "SPSS_INSTALL_PATH": spss_install,
        "SPSS_TIMEOUT": str(get_timeout()),
        "SPSS_STARTUP_TIMEOUT": str(get_startup_timeout()),
    }

    if prefer_uvx and shutil.which("uvx"):
        return {
            "command": "uvx",
            "args": ["spss-mcp", "serve", "--transport", "stdio"],
            "env": env,
        }

    command, args = get_entrypoint_config()
    return {"command": command, "args": args, "env": env}


def _load_mcp_json(path: Path) -> tuple[dict, bool]:
    if not path.exists():
        return {}, False
    content = path.read_text(encoding="utf-8").strip()
    if not content:
        return {}, True
    data = json.loads(content)
    if not isinstance(data, dict):
        raise ValueError(f"Expected a JSON object in {path}")
    return data, True


def _backup_file(path: Path) -> Path | None:
    if not path.exists():
        return None
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = path.with_name(f"{path.name}.backup.{timestamp}")
    shutil.copy2(path, backup_path)
    return backup_path


def configure_cursor_settings(
    config_path: Path | None = None,
    *,
    prefer_uvx: bool = True,
) -> dict:
    """
    Merge the ``spss-mcp`` MCP entry into Cursor's ``mcp.json`` and write the file.

    Returns a status payload describing what changed.
    """
    path = config_path or get_cursor_mcp_path()
    path.parent.mkdir(parents=True, exist_ok=True)

    settings, existed = _load_mcp_json(path)
    servers = settings.setdefault("mcpServers", {})
    if not isinstance(servers, dict):
        raise ValueError(f"`mcpServers` must be a JSON object in {path}")

    new_entry = build_cursor_mcp_entry(prefer_uvx=prefer_uvx)
    previous_entry = servers.get("spss-mcp")

    backup_path = _backup_file(path) if existed else None
    servers["spss-mcp"] = new_entry
    # Drop legacy keys from earlier naming.
    servers.pop("spss-studio", None)
    servers.pop("spss-studio-mcp", None)

    path.write_text(
        json.dumps(settings, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )

    if previous_entry is None:
        status = "created"
    elif previous_entry == new_entry:
        status = "unchanged"
    else:
        status = "updated"

    return {
        "status": status,
        "config_path": str(path),
        "backup_path": str(backup_path) if backup_path else None,
        "entry": new_entry,
    }
