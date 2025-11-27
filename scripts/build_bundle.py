#!/usr/bin/env python3
"""
Build platform-specific .mcpb bundles for jvlink-mcp-server.

Usage:
    python scripts/build_bundle.py [--platform PLATFORM] [--version VERSION]

Platforms: win64, macos-arm64, linux-x64
"""

import argparse
import json
import os
import platform
import shutil
import subprocess
import sys
from pathlib import Path


def get_mcpb_command() -> list[str]:
    """Get the command to run mcpb (handles different environments)."""
    # Try direct mcpb first
    try:
        subprocess.run(["mcpb", "--version"], capture_output=True, check=True)
        return ["mcpb"]
    except (subprocess.CalledProcessError, FileNotFoundError):
        pass

    # Try npx mcpb
    try:
        subprocess.run(["npx", "mcpb", "--version"], capture_output=True, check=True)
        return ["npx", "mcpb"]
    except (subprocess.CalledProcessError, FileNotFoundError):
        pass

    # Try common npm global paths on Windows
    if platform.system() == "Windows":
        npm_paths = [
            Path(os.environ.get("APPDATA", "")) / "npm" / "mcpb.cmd",
            Path(os.environ.get("LOCALAPPDATA", "")) / "npm" / "mcpb.cmd",
        ]
        for npm_path in npm_paths:
            if npm_path.exists():
                return [str(npm_path)]

    raise RuntimeError(
        "mcpb not found. Please install it with: npm install -g @anthropic-ai/mcpb"
    )


# Platform configurations
PLATFORM_CONFIG = {
    "win64": {
        "compatibility_platform": "win32",
        "path_separator": ";",
    },
    "macos-arm64": {
        "compatibility_platform": "darwin",
        "path_separator": ":",
    },
    "linux-x64": {
        "compatibility_platform": "linux",
        "path_separator": ":",
    },
}


def detect_platform() -> str:
    """Detect current platform."""
    system = platform.system().lower()
    machine = platform.machine().lower()

    if system == "windows":
        return "win64"
    elif system == "darwin":
        if machine == "arm64":
            return "macos-arm64"
        return "macos-x64"
    elif system == "linux":
        return "linux-x64"
    else:
        raise RuntimeError(f"Unsupported platform: {system} {machine}")


def generate_manifest(version: str, platform_name: str, project_dir: Path) -> dict:
    """Generate platform-specific manifest.json."""
    config = PLATFORM_CONFIG[platform_name]

    manifest = {
        "manifest_version": "0.3",
        "name": "jvlink-mcp-server",
        "display_name": "JVLink 競馬分析",
        "version": version,
        "description": "JRA-VANデータを使った競馬分析MCPサーバー。自然言語で競馬データを分析できます。",
        "long_description": (
            "Claudeに話しかけるだけで、競馬データを自由に分析できるMCPサーバーです。"
            "SQLを書く必要はありません。自然な日本語で質問すれば、過去のレース結果、"
            "騎手成績、血統傾向など、あらゆる競馬データを調べられます。\n\n"
            "例えば:\n"
            "- 「1番人気の勝率はどのくらい？」\n"
            "- 「今年勝ち星が多い騎手は？」\n"
            "- 「東京芝1600mで内枠と外枠、どっちが有利？」"
        ),
        "author": {
            "name": "miyamamoto",
            "url": "https://github.com/miyamamoto"
        },
        "repository": {
            "type": "git",
            "url": "https://github.com/miyamamoto/jvlink-mcp-server"
        },
        "documentation": "https://github.com/miyamamoto/jvlink-mcp-server#readme",
        "license": "Apache-2.0",
        "server": {
            "type": "python",
            "entry_point": "src/jvlink_mcp_server/server.py",
            "mcp_config": {
                "command": "python",
                "args": ["-m", "jvlink_mcp_server.server"],
                "env": {
                    "PYTHONPATH": f"${{__dirname}}/lib{config['path_separator']}${{__dirname}}/src",
                    "DB_TYPE": "sqlite",
                    "DB_PATH": "${user_config.database_path}"
                }
            }
        },
        "user_config": {
            "database_path": {
                "type": "file",
                "title": "競馬データベースファイル",
                "description": "jrvltsqlで作成したSQLiteデータベースファイル（keiba.db）へのパス",
                "required": True
            }
        },
        "compatibility": {
            "claude_desktop": ">=0.10.0",
            "platforms": [config["compatibility_platform"]],
            "runtimes": {
                "python": ">=3.11"
            }
        },
        "tools": [
            {"name": "execute_safe_query", "description": "SQLクエリを実行して競馬データを取得"},
            {"name": "analyze_favorite_performance", "description": "人気別の成績を分析"},
            {"name": "analyze_jockey_stats", "description": "騎手の成績を分析"},
            {"name": "analyze_sire_stats", "description": "種牡馬（父馬）の成績を分析"},
            {"name": "get_horse_race_history", "description": "馬の戦績を取得"},
            {"name": "analyze_frame_stats", "description": "枠番別の成績を分析"}
        ],
        "privacy_policies": ["https://jra-van.jp/info/rule.html"]
    }

    return manifest


def install_dependencies(lib_dir: Path) -> None:
    """Install Python dependencies to lib directory."""
    print(f"Installing dependencies to {lib_dir}...")

    # Clean existing lib directory
    if lib_dir.exists():
        shutil.rmtree(lib_dir)
    lib_dir.mkdir(parents=True)

    # Install dependencies
    dependencies = [
        "duckdb>=1.1.0",
        "mcp[cli]>=1.1.0",
        "pandas>=2.0.0",
        "python-dotenv>=1.0.0",
    ]

    cmd = [
        sys.executable, "-m", "pip", "install",
        "--target", str(lib_dir),
        "--quiet",
        *dependencies
    ]

    subprocess.run(cmd, check=True)
    print(f"Dependencies installed to {lib_dir}")

    # Clean up unnecessary files
    cleanup_patterns = ["__pycache__", "*.pyc", "*.pyo", "tests", "test"]
    for pattern in cleanup_patterns:
        for path in lib_dir.rglob(pattern):
            if path.is_dir():
                shutil.rmtree(path, ignore_errors=True)
            elif path.is_file():
                path.unlink(missing_ok=True)

    # Calculate size
    total_size = sum(f.stat().st_size for f in lib_dir.rglob("*") if f.is_file())
    print(f"Dependencies size: {total_size / 1024 / 1024:.1f} MB")


def build_bundle(project_dir: Path, platform_name: str, version: str) -> Path:
    """Build the .mcpb bundle."""

    # Get mcpb command
    mcpb_cmd = get_mcpb_command()
    print(f"Using mcpb: {' '.join(mcpb_cmd)}")

    # Generate manifest
    manifest = generate_manifest(version, platform_name, project_dir)
    manifest_path = project_dir / "manifest.json"

    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, ensure_ascii=False, indent=2)
    print(f"Generated manifest.json for {platform_name}")

    # On Windows, use shell=True for .cmd files
    use_shell = platform.system() == "Windows"

    # Validate manifest
    print("Validating manifest...")
    subprocess.run([*mcpb_cmd, "validate", str(manifest_path)], check=True, cwd=project_dir, shell=use_shell)

    # Build bundle
    print("Building bundle...")
    subprocess.run([*mcpb_cmd, "pack", "."], check=True, cwd=project_dir, shell=use_shell)

    # Rename with platform suffix
    default_name = project_dir / "jvlink-mcp-server.mcpb"
    final_name = project_dir / f"jvlink-mcp-server-{version}-{platform_name}.mcpb"

    if final_name.exists():
        final_name.unlink()

    default_name.rename(final_name)
    print(f"Created: {final_name.name}")

    # Show bundle info
    subprocess.run([*mcpb_cmd, "info", str(final_name)], cwd=project_dir, shell=use_shell)

    return final_name


def main():
    parser = argparse.ArgumentParser(description="Build jvlink-mcp-server .mcpb bundle")
    parser.add_argument(
        "--platform",
        choices=list(PLATFORM_CONFIG.keys()),
        default=None,
        help="Target platform (default: auto-detect)"
    )
    parser.add_argument(
        "--version",
        default="0.1.0",
        help="Version string (default: 0.1.0)"
    )
    parser.add_argument(
        "--skip-deps",
        action="store_true",
        help="Skip installing dependencies (use existing lib/)"
    )

    args = parser.parse_args()

    # Detect platform if not specified
    platform_name = args.platform or detect_platform()
    print(f"Building for platform: {platform_name}")

    # Project directory
    project_dir = Path(__file__).parent.parent.resolve()
    lib_dir = project_dir / "lib"

    print(f"Project directory: {project_dir}")
    print(f"Version: {args.version}")
    print()

    # Install dependencies
    if not args.skip_deps:
        install_dependencies(lib_dir)
    else:
        print("Skipping dependency installation (--skip-deps)")

    print()

    # Build bundle
    bundle_path = build_bundle(project_dir, platform_name, args.version)

    print()
    print("=" * 50)
    print(f"Build complete: {bundle_path.name}")
    print(f"Size: {bundle_path.stat().st_size / 1024 / 1024:.1f} MB")
    print("=" * 50)


if __name__ == "__main__":
    main()
