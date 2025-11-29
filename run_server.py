#!/usr/bin/env python3
"""
JVLink MCP Server - Auto-dependency wrapper

This wrapper ensures all dependencies are installed correctly for the
user's Python version before starting the MCP server.

On first run, it will automatically install the required packages using pip.
This typically takes 30-60 seconds.
"""

import importlib
import subprocess
import sys
from pathlib import Path

# Dependencies with version constraints
REQUIRED_PACKAGES = [
    "duckdb>=1.1.0",
    "mcp[cli]>=1.1.0",
    "pandas>=2.0.0",
    "python-dotenv>=1.0.0",
]

# Key native modules to test import (if these work, everything should work)
TEST_IMPORTS = [
    "pydantic_core._pydantic_core",
    "duckdb",
    "pandas",
]


def log(msg: str) -> None:
    """Log to stderr (stdout is reserved for MCP protocol)."""
    print(msg, file=sys.stderr, flush=True)


def setup_paths() -> Path:
    """Add lib and src directories to Python path."""
    bundle_dir = Path(__file__).parent.resolve()
    lib_dir = bundle_dir / "lib"
    src_dir = bundle_dir / "src"

    # Ensure lib exists
    lib_dir.mkdir(exist_ok=True)

    # Add to path (lib first so installed packages take precedence)
    for path in [lib_dir, src_dir]:
        path_str = str(path)
        if path_str not in sys.path:
            sys.path.insert(0, path_str)

    return lib_dir


def check_dependencies() -> bool:
    """Check if all native dependencies are available and compatible."""
    for module in TEST_IMPORTS:
        try:
            importlib.import_module(module)
        except ImportError:
            return False
    return True


def check_pip_available() -> bool:
    """Check if pip is available."""
    try:
        subprocess.run(
            [sys.executable, "-m", "pip", "--version"],
            capture_output=True,
            check=True,
        )
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False


def install_dependencies(lib_dir: Path) -> None:
    """Install dependencies to the lib directory."""
    log("")
    log("=" * 50)
    log("JVLink MCP Server - 初回セットアップ")
    log("=" * 50)
    log("")
    log(f"Python {sys.version.split()[0]} 用の依存パッケージを")
    log("インストールしています...")
    log("")
    log("これには30〜60秒かかる場合があります。")
    log("しばらくお待ちください...")
    log("")

    # Check pip is available
    if not check_pip_available():
        log("エラー: pip が見つかりません")
        log("")
        log("Python に pip がインストールされていることを確認してください。")
        log("通常は Python と一緒にインストールされています。")
        sys.exit(1)

    try:
        # Run pip install
        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "pip",
                "install",
                "--target",
                str(lib_dir),
                "--upgrade",
                *REQUIRED_PACKAGES,
            ],
            capture_output=True,
            text=True,
            check=True,
        )

        log("✓ インストール完了!")
        log("")

        # Clear import caches so new packages are found
        importlib.invalidate_caches()

    except subprocess.CalledProcessError as e:
        log("✗ インストールに失敗しました")
        log("")
        if e.stderr:
            # Show last few lines of error
            error_lines = e.stderr.strip().split("\n")[-5:]
            for line in error_lines:
                log(f"  {line}")
            log("")
        log("以下を確認してください:")
        log("  - インターネット接続があること")
        log("  - pip が正しく動作すること")
        log("")
        log("手動でインストールする場合:")
        log(f"  pip install --target \"{lib_dir}\" " + " ".join(REQUIRED_PACKAGES))
        log("")
        sys.exit(1)


def main():
    """Main entry point."""
    # Setup paths
    lib_dir = setup_paths()

    # Check if dependencies are available and compatible
    if not check_dependencies():
        install_dependencies(lib_dir)

        # Verify installation worked
        if not check_dependencies():
            log("✗ 依存関係のインストール後もインポートに失敗しました")
            log("")
            log("手動で以下を実行してみてください:")
            log(f"  pip install --target \"{lib_dir}\" " + " ".join(REQUIRED_PACKAGES))
            log("")
            sys.exit(1)

    # Import and run the server
    from jvlink_mcp_server.server import mcp

    mcp.run()


if __name__ == "__main__":
    main()
