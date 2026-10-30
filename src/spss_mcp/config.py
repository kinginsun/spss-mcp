"""
Configuration loading and SPSS installation detection for SPSS MCP.

Supports Windows (stats.exe + bundled Python3\\python.exe) and macOS app-bundle
layouts (SPSS Statistics.app/Contents/MacOS/stats + Resources/Python3).
"""

from __future__ import annotations

import os
import shutil
import sys
import tempfile
from pathlib import Path

from dotenv import load_dotenv

_PROJECT_ROOT = Path(__file__).resolve().parents[2]

# Load .env from project root first and let repo-local settings override inherited shell values.
load_dotenv(_PROJECT_ROOT / ".env", override=True)
load_dotenv()


def _stats_binary_name() -> str:
    """Platform-specific SPSS frontend binary name."""
    return "stats.exe" if sys.platform == "win32" else "stats"


def _is_stats_binary(path: Path) -> bool:
    """True when ``path`` looks like the SPSS stats launcher."""
    name = path.name.lower()
    return path.is_file() and name in ("stats", "stats.exe")


def _mac_stats_from_install_root(root: Path) -> Path | None:
    """Resolve ``…/MacOS/stats`` from a Mac install root or app bundle."""
    candidates = [
        root / "SPSS Statistics.app" / "Contents" / "MacOS" / "stats",
        root / "Contents" / "MacOS" / "stats",
        root / "MacOS" / "stats",
        root / "stats",
    ]
    for candidate in candidates:
        if _is_stats_binary(candidate):
            return candidate
    return None


def _resolve_stats_from_install_path(install_path: str) -> str | None:
    """Resolve a stats binary from ``SPSS_INSTALL_PATH`` on any platform."""
    path = Path(install_path).expanduser()
    if _is_stats_binary(path):
        return str(path.resolve())

    # Windows-style: <install>/stats.exe or direct folder containing it
    win_candidate = path / "stats.exe"
    if win_candidate.is_file():
        return str(win_candidate.resolve())

    # macOS app-bundle layouts
    if sys.platform == "darwin":
        mac = _mac_stats_from_install_root(path)
        if mac:
            return str(mac.resolve())

    # PATH-style bare name already handled elsewhere; accept unix ``stats`` under path
    unix_candidate = path / "stats"
    if _is_stats_binary(unix_candidate):
        return str(unix_candidate.resolve())

    return None


def _find_spss_via_registry() -> str | None:
    """Search Windows registry for IBM SPSS Statistics installation path."""
    if sys.platform != "win32":
        return None
    try:
        import winreg

        base_key = r"SOFTWARE\IBM\SPSS Statistics"
        for hive in (winreg.HKEY_LOCAL_MACHINE, winreg.HKEY_CURRENT_USER):
            try:
                with winreg.OpenKey(hive, base_key) as key:
                    i = 0
                    while True:
                        try:
                            version = winreg.EnumKey(key, i)
                            with winreg.OpenKey(key, version) as ver_key:
                                try:
                                    install_dir, _ = winreg.QueryValueEx(
                                        ver_key, "InstallationDirectory"
                                    )
                                    candidate = Path(install_dir) / "stats.exe"
                                    if candidate.exists():
                                        return str(candidate)
                                except FileNotFoundError:
                                    pass
                            i += 1
                        except OSError:
                            break
            except FileNotFoundError:
                continue
    except ImportError:
        pass
    return None


def _find_spss_via_filesystem_windows() -> str | None:
    """Check common SPSS installation paths on Windows."""
    common_roots = [
        r"C:\Program Files\IBM\SPSS Statistics",
        r"C:\Program Files\IBM\SPSS\Statistics",
        r"C:\Program Files (x86)\IBM\SPSS Statistics",
        r"C:\Program Files (x86)\IBM\SPSS\Statistics",
        r"C:\spss",
        r"D:\spss",
        r"E:\spss",
    ]
    versions = list(range(20, 35))
    for root in common_roots:
        for v in reversed(versions):
            candidate = Path(root) / str(v) / "stats.exe"
            if candidate.exists():
                return str(candidate)
        candidate = Path(root) / "stats.exe"
        if candidate.exists():
            return str(candidate)
    return None


def _parse_spss_version_from_name(name: str) -> int:
    """Extract a major version integer from 'IBM SPSS Statistics 27' style names."""
    digits = "".join(ch if ch.isdigit() else " " for ch in name).split()
    for token in digits:
        try:
            value = int(token)
        except ValueError:
            continue
        if 16 <= value <= 99:
            return value
    return 0


def _find_spss_via_filesystem_mac() -> str | None:
    """Locate ``stats`` inside macOS SPSS Statistics.app bundles (newest first)."""
    search_roots = [
        Path("/Applications"),
        Path.home() / "Applications",
    ]
    found: list[tuple[int, Path]] = []
    for root in search_roots:
        if not root.is_dir():
            continue
        for entry in root.iterdir():
            if not entry.is_dir():
                continue
            if not entry.name.startswith("IBM SPSS Statistics"):
                continue
            stats = _mac_stats_from_install_root(entry)
            if stats:
                found.append((_parse_spss_version_from_name(entry.name), stats))

    if not found:
        return None
    found.sort(key=lambda item: item[0], reverse=True)
    return str(found[0][1].resolve())


def _find_spss_via_filesystem() -> str | None:
    """Platform filesystem probe for the SPSS launcher."""
    if sys.platform == "darwin":
        return _find_spss_via_filesystem_mac()
    if sys.platform == "win32":
        return _find_spss_via_filesystem_windows()
    return None


def get_spss_executable() -> str | None:
    """
    Return path to the SPSS frontend binary (``stats`` / ``stats.exe``), or None.

    Detection order:
    1. SPSS_NO_SPSS env var (forces file-only mode)
    2. SPSS_INSTALL_PATH env var (install root, Contents, or binary)
    3. Windows registry
    4. Common filesystem paths (Windows / macOS)
    5. PATH scan
    """
    if os.environ.get("SPSS_NO_SPSS", "0").strip() in ("1", "true", "yes"):
        return None

    install_path = os.environ.get("SPSS_INSTALL_PATH", "").strip()
    if install_path:
        resolved = _resolve_stats_from_install_path(install_path)
        if resolved:
            return resolved

    found = _find_spss_via_registry()
    if found:
        return found

    found = _find_spss_via_filesystem()
    if found:
        return found

    found = shutil.which("stats")
    if found:
        return found

    return None


def get_spss_home() -> str | None:
    """
    Return the SPSS backend home directory used by the XD / Python engine.

    * Windows: directory containing ``stats.exe``
    * macOS: ``…/SPSS Statistics.app/Contents``
    """
    stats_exe = get_spss_executable()
    if not stats_exe:
        return None
    path = Path(stats_exe).resolve()
    if sys.platform == "darwin":
        # …/Contents/MacOS/stats → Contents
        if path.parent.name == "MacOS":
            return str(path.parent.parent)
    return str(path.parent)


def get_spss_install_root() -> str | None:
    """
    Return the top-level SPSS installation directory (for env / docs).

    * Windows: same as ``get_spss_home()``
    * macOS: directory that contains ``SPSS Statistics.app``
      (e.g. ``/Applications/IBM SPSS Statistics 27``)
    """
    stats_exe = get_spss_executable()
    if not stats_exe:
        return None
    path = Path(stats_exe).resolve()
    if sys.platform == "darwin":
        # …/<root>/SPSS Statistics.app/Contents/MacOS/stats
        if (
            path.parent.name == "MacOS"
            and path.parent.parent.name == "Contents"
            and path.parent.parent.parent.name.endswith(".app")
        ):
            return str(path.parent.parent.parent.parent)
        home = get_spss_home()
        if home:
            return str(Path(home).parent.parent)
    return str(path.parent)


def get_spss_python() -> str | None:
    """Return path to the SPSS-bundled Python3 interpreter."""
    stats_exe = get_spss_executable()
    if not stats_exe:
        return None

    if sys.platform == "darwin":
        install_root = get_spss_install_root()
        home = get_spss_home()
        candidates: list[Path] = []
        if install_root:
            root = Path(install_root)
            candidates.extend(
                [
                    root / "Resources" / "Python3" / "bin" / "python3.8",
                    root / "Resources" / "Python3" / "bin" / "python3",
                    root / "Resources" / "Python3" / "bin" / "python3.9",
                    root / "Resources" / "Python3" / "bin" / "python3.10",
                    root / "Resources" / "Python3" / "bin" / "python3.11",
                    root / "Resources" / "Python3" / "bin" / "python3.12",
                ]
            )
        if home:
            # Fallback if Resources lives beside Contents (unusual layouts)
            candidates.append(Path(home) / "Python3" / "bin" / "python3")
        for candidate in candidates:
            if candidate.is_file():
                return str(candidate.resolve())
        return None

    python_exe = Path(stats_exe).parent / "Python3" / "python.exe"
    if python_exe.exists():
        return str(python_exe)
    return None


def get_spss_site_packages() -> str | None:
    """Return the ``spss`` package site-packages directory for the bundled Python."""
    python_exe = get_spss_python()
    if not python_exe:
        return None
    py = Path(python_exe)

    if sys.platform == "darwin":
        # …/Resources/Python3/bin/python3.8 → …/lib/python3.X/site-packages
        python3_root = py.parent.parent
        lib = python3_root / "lib"
        if lib.is_dir():
            for child in sorted(lib.glob("python3.*"), reverse=True):
                site = child / "site-packages"
                if (site / "spss").exists():
                    return str(site.resolve())
        return None

    # Windows: <install>/Python3/Lib/site-packages
    site = py.parent / "Lib" / "site-packages"
    if (site / "spss").exists() or site.is_dir():
        return str(site.resolve())
    return None


def get_spss_python_lib_dir() -> str | None:
    """Return directory containing ``libpython*.dylib`` (macOS DYLD helper)."""
    python_exe = get_spss_python()
    if not python_exe or sys.platform != "darwin":
        return None
    lib_dir = Path(python_exe).parent.parent / "lib"
    if lib_dir.is_dir():
        return str(lib_dir.resolve())
    return None


def build_spss_engine_env(base: dict | None = None) -> dict:
    """
    Environment for launching the SPSS-bundled Python / XD engine.

    On macOS this injects ``DYLD_*`` so the SPSS Python binary can resolve
    ``libpython3.x.dylib`` (often hard-coded to ``/Applications/Python3/lib``).
    """
    env = dict(base if base is not None else os.environ)
    home = get_spss_home()
    if home:
        env["SPSS_HOME"] = home
        env["PATH"] = home + os.pathsep + env.get("PATH", "")
        if sys.platform == "darwin":
            # Prefer Contents/bin (StartXD, spssengine) then MacOS (stats)
            bin_dir = str(Path(home) / "bin")
            macos_dir = str(Path(home) / "MacOS")
            env["PATH"] = os.pathsep.join(
                [bin_dir, macos_dir, home, env.get("PATH", "")]
            )
            native_lib = str(Path(home) / "lib")
            py_lib = get_spss_python_lib_dir()
            lib_parts = [p for p in (py_lib, native_lib) if p]
            if lib_parts:
                joined = os.pathsep.join(lib_parts)
                for key in ("DYLD_LIBRARY_PATH", "DYLD_FALLBACK_LIBRARY_PATH"):
                    existing = env.get(key, "")
                    env[key] = (
                        joined
                        if not existing
                        else joined + os.pathsep + existing
                    )
    return env


def _get_positive_int_env(name: str, default: int) -> int:
    """Return a positive integer env var value or a default."""
    try:
        value = int(os.environ.get(name, str(default)))
    except ValueError:
        return default
    return value if value > 0 else default


def get_timeout() -> int:
    """Return SPSS analysis timeout in seconds (default 120)."""
    return _get_positive_int_env("SPSS_TIMEOUT", 120)


def get_startup_timeout() -> int:
    """
    Return SPSS engine startup timeout in seconds.

    Startup is often slower than a normal analysis request because SPSS may need
    to initialize licensing, Python integration, and the persistent XD engine.
    Default to 300 seconds unless explicitly overridden.
    """
    return _get_positive_int_env("SPSS_STARTUP_TIMEOUT", 300)


def get_runtime_config() -> dict:
    """Return the effective runtime configuration used for SPSS execution."""
    return {
        "timeout": get_timeout(),
        "startup_timeout": get_startup_timeout(),
        "temp_dir": str(get_temp_dir()),
        "results_dir": str(get_results_dir()),
        "spss_path": get_spss_executable(),
        "spss_home": get_spss_home(),
        "spss_install_root": get_spss_install_root(),
        "spss_python": get_spss_python(),
        "platform": sys.platform,
    }


def get_temp_dir() -> Path:
    """Return the directory for temporary SPSS files, creating it if needed."""
    default = Path(tempfile.gettempdir()) / "spss-studio-mcp"
    temp_dir = Path(os.environ.get("SPSS_TEMP_DIR", str(default)))
    temp_dir.mkdir(parents=True, exist_ok=True)
    return temp_dir


def get_results_dir() -> Path:
    """Return directory where persistent SPSS viewer output files (.spv) are saved."""
    default = get_temp_dir() / "results"
    out_dir = Path(os.environ.get("SPSS_RESULTS_DIR", str(default)))
    out_dir.mkdir(parents=True, exist_ok=True)
    return out_dir


def detect_capabilities() -> dict:
    """
    Detect what capabilities are available on this machine.

    Returns a dict with:
        pyreadstat: bool
        spss: bool
        spss_path: str | None
        pyreadstat_version: str | None
        pandas_version: str | None
    """
    caps: dict = {
        "pyreadstat": False,
        "pyreadstat_version": None,
        "pandas_version": None,
        "spss": False,
        "spss_path": None,
        "spss_home": None,
        "spss_install_root": None,
        "spss_python": None,
        "platform": sys.platform,
    }

    try:
        import pyreadstat

        caps["pyreadstat"] = True
        caps["pyreadstat_version"] = getattr(pyreadstat, "__version__", "unknown")
    except ImportError:
        pass

    try:
        import pandas as pd

        caps["pandas_version"] = pd.__version__
    except ImportError:
        pass

    spss_exe = get_spss_executable()
    if spss_exe:
        caps["spss"] = True
        caps["spss_path"] = spss_exe
        caps["spss_home"] = get_spss_home()
        caps["spss_install_root"] = get_spss_install_root()
        caps["spss_python"] = get_spss_python()
    else:
        caps["spss_python"] = None

    return caps
