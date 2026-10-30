"""Unit tests for macOS / cross-platform SPSS detection helpers."""

from __future__ import annotations

from pathlib import Path

import pytest

from spss_mcp import config


def _fake_mac_spss_tree(root: Path, version: int = 27) -> Path:
    """Create a minimal Mac SPSS layout under ``root`` and return install root."""
    install = root / f"IBM SPSS Statistics {version}"
    stats = (
        install
        / "SPSS Statistics.app"
        / "Contents"
        / "MacOS"
        / "stats"
    )
    stats.parent.mkdir(parents=True)
    stats.write_text("#!/bin/sh\n", encoding="utf-8")
    stats.chmod(0o755)

    py_bin = install / "Resources" / "Python3" / "bin" / "python3.8"
    py_bin.parent.mkdir(parents=True)
    py_bin.write_text("#!/bin/sh\n", encoding="utf-8")
    py_bin.chmod(0o755)

    site = (
        install
        / "Resources"
        / "Python3"
        / "lib"
        / "python3.8"
        / "site-packages"
        / "spss"
    )
    site.mkdir(parents=True)
    (site / "__init__.py").write_text("# fake\n", encoding="utf-8")

    lib = install / "Resources" / "Python3" / "lib"
    (lib / "libpython3.8.dylib").write_bytes(b"fake")
    return install


@pytest.fixture
def mac_platform(monkeypatch):
    monkeypatch.setattr(config.sys, "platform", "darwin")
    monkeypatch.delenv("SPSS_INSTALL_PATH", raising=False)
    monkeypatch.delenv("SPSS_NO_SPSS", raising=False)
    return monkeypatch


def test_resolve_stats_from_mac_install_root(tmp_path, mac_platform):
    install = _fake_mac_spss_tree(tmp_path, 27)
    resolved = config._resolve_stats_from_install_path(str(install))
    assert resolved is not None
    assert Path(resolved).name == "stats"
    assert Path(resolved).is_file()


def test_resolve_stats_from_mac_contents(tmp_path, mac_platform):
    install = _fake_mac_spss_tree(tmp_path, 27)
    contents = install / "SPSS Statistics.app" / "Contents"
    resolved = config._resolve_stats_from_install_path(str(contents))
    assert resolved is not None
    assert Path(resolved).name == "stats"


def test_get_spss_home_and_python_on_mac(tmp_path, mac_platform, monkeypatch):
    install = _fake_mac_spss_tree(tmp_path, 27)
    monkeypatch.setenv("SPSS_INSTALL_PATH", str(install))

    exe = config.get_spss_executable()
    assert exe and exe.endswith("/stats")

    home = config.get_spss_home()
    assert home == str(install / "SPSS Statistics.app" / "Contents")

    root = config.get_spss_install_root()
    assert root == str(install)

    python = config.get_spss_python()
    assert python and python.endswith("python3.8")

    site = config.get_spss_site_packages()
    assert site and site.endswith("site-packages")
    assert (Path(site) / "spss").is_dir()


def test_build_spss_engine_env_sets_dyld(tmp_path, mac_platform, monkeypatch):
    install = _fake_mac_spss_tree(tmp_path, 27)
    monkeypatch.setenv("SPSS_INSTALL_PATH", str(install))

    env = config.build_spss_engine_env(base={})
    assert env["SPSS_HOME"].endswith("Contents")
    assert "DYLD_FALLBACK_LIBRARY_PATH" in env
    assert "libpython3.8.dylib" not in env["DYLD_FALLBACK_LIBRARY_PATH"]
    assert str(install / "Resources" / "Python3" / "lib") in env[
        "DYLD_FALLBACK_LIBRARY_PATH"
    ]


def test_filesystem_probe_prefers_newest_version(tmp_path, mac_platform, monkeypatch):
    apps = tmp_path / "Applications"
    apps.mkdir()
    _fake_mac_spss_tree(apps, 26)
    newest = _fake_mac_spss_tree(apps, 27)

    def _probe_tmp_apps():
        found = []
        for entry in apps.iterdir():
            if not entry.name.startswith("IBM SPSS Statistics"):
                continue
            stats = config._mac_stats_from_install_root(entry)
            if stats:
                found.append(
                    (config._parse_spss_version_from_name(entry.name), stats)
                )
        found.sort(key=lambda item: item[0], reverse=True)
        return str(found[0][1].resolve()) if found else None

    monkeypatch.setattr(config, "_find_spss_via_filesystem_mac", _probe_tmp_apps)
    resolved = config._find_spss_via_filesystem_mac()
    assert resolved == str(
        (newest / "SPSS Statistics.app" / "Contents" / "MacOS" / "stats").resolve()
    )
    assert config._parse_spss_version_from_name("IBM SPSS Statistics 27") == 27
    assert config._parse_spss_version_from_name("IBM SPSS Statistics") == 0


def test_make_engine_script_inserts_mac_site_packages():
    from spss_mcp.spss_engine import _make_engine_script

    script = _make_engine_script(
        "/Applications/IBM SPSS Statistics 27/SPSS Statistics.app/Contents",
        "/Applications/IBM SPSS Statistics 27/Resources/Python3/lib/python3.8/site-packages",
    )
    assert "SPSS Statistics.app/Contents" in script
    assert "site-packages" in script
    assert 'os.environ["SPSS_HOME"] = SPSS_HOME' in script
