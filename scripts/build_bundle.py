#!/usr/bin/env python3
"""
Build universal .mcpb bundle for jvlink-mcp-server.

This creates a single bundle that works on all platforms (Windows, macOS, Linux)
and all Python versions (3.11+). Dependencies are installed automatically on
first run using pip.

Usage:
    python scripts/build_bundle.py [--version VERSION]
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
    is_windows = platform.system() == "Windows"

    # Try direct mcpb first (with shell=True on Windows for .cmd files)
    try:
        subprocess.run(
            ["mcpb", "--version"],
            capture_output=True,
            check=True,
            shell=is_windows
        )
        return ["mcpb"]
    except (subprocess.CalledProcessError, FileNotFoundError):
        pass

    # Try npx mcpb (with shell=True on Windows)
    try:
        subprocess.run(
            ["npx", "mcpb", "--version"],
            capture_output=True,
            check=True,
            shell=is_windows
        )
        return ["npx", "mcpb"]
    except (subprocess.CalledProcessError, FileNotFoundError):
        pass

    # Try common npm global paths on Windows
    if is_windows:
        npm_paths = [
            Path(os.environ.get("APPDATA", "")) / "npm" / "mcpb.cmd",
            Path(os.environ.get("LOCALAPPDATA", "")) / "npm" / "mcpb.cmd",
        ]
        for npm_path in npm_paths:
            if npm_path.exists():
                return [str(npm_path)]

        # Try to get npm prefix dynamically
        try:
            result = subprocess.run(
                ["npm", "config", "get", "prefix"],
                capture_output=True,
                text=True,
                check=True,
                shell=True
            )
            npm_prefix = Path(result.stdout.strip())
            mcpb_cmd = npm_prefix / "mcpb.cmd"
            if mcpb_cmd.exists():
                return [str(mcpb_cmd)]
        except (subprocess.CalledProcessError, FileNotFoundError):
            pass

    raise RuntimeError(
        "mcpb not found. Please install it with: npm install -g @anthropic-ai/mcpb"
    )


def generate_manifest(version: str, project_dir: Path) -> dict:
    """Generate universal manifest.json."""

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
            "- 「東京芝1600mで内枠と外枠、どっちが有利？」\n\n"
            "初回起動時に依存パッケージを自動インストールします（30〜60秒）。"
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
            "entry_point": "run_server.py",
            "mcp_config": {
                "command": "python",
                "args": ["${__dirname}/run_server.py"],
                "env": {
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
            "platforms": ["win32", "darwin", "linux"],
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


def prepare_bundle_directory(project_dir: Path) -> None:
    """Prepare the project directory for bundling."""
    lib_dir = project_dir / "lib"

    # Clean existing lib directory (dependencies will be installed at runtime)
    if lib_dir.exists():
        shutil.rmtree(lib_dir)

    # Create empty lib directory with .gitkeep
    lib_dir.mkdir(parents=True, exist_ok=True)
    (lib_dir / ".gitkeep").touch()

    print("Prepared lib/ directory (dependencies will be installed at runtime)")


def build_bundle(project_dir: Path, version: str) -> Path:
    """Build the universal .mcpb bundle."""

    # Get mcpb command
    mcpb_cmd = get_mcpb_command()
    print(f"Using mcpb: {' '.join(mcpb_cmd)}")

    # Generate manifest
    manifest = generate_manifest(version, project_dir)
    manifest_path = project_dir / "manifest.json"

    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, ensure_ascii=False, indent=2)
    print("Generated universal manifest.json")

    # On Windows, use shell=True for .cmd files
    use_shell = platform.system() == "Windows"

    # Validate manifest
    print("Validating manifest...")
    subprocess.run([*mcpb_cmd, "validate", str(manifest_path)], check=True, cwd=project_dir, shell=use_shell)

    # Build bundle
    print("Building bundle...")
    subprocess.run([*mcpb_cmd, "pack", "."], check=True, cwd=project_dir, shell=use_shell)

    # Rename with version (no platform suffix for universal bundle)
    default_name = project_dir / "jvlink-mcp-server.mcpb"
    final_name = project_dir / f"jvlink-mcp-server-{version}.mcpb"

    if final_name.exists():
        final_name.unlink()

    default_name.rename(final_name)
    print(f"Created: {final_name.name}")

    # Show bundle info
    subprocess.run([*mcpb_cmd, "info", str(final_name)], cwd=project_dir, shell=use_shell)

    return final_name


def main():
    parser = argparse.ArgumentParser(description="Build universal jvlink-mcp-server .mcpb bundle")
    parser.add_argument(
        "--version",
        default="0.1.0",
        help="Version string (default: 0.1.0)"
    )

    args = parser.parse_args()

    # Project directory
    project_dir = Path(__file__).parent.parent.resolve()

    print("=" * 50)
    print("Building Universal MCPB Bundle")
    print("=" * 50)
    print(f"Project directory: {project_dir}")
    print(f"Version: {args.version}")
    print()
    print("This bundle works on all platforms (Windows, macOS, Linux)")
    print("and all Python versions (3.11+).")
    print()

    # Prepare bundle directory
    prepare_bundle_directory(project_dir)
    print()

    # Build bundle
    bundle_path = build_bundle(project_dir, args.version)

    print()
    print("=" * 50)
    print(f"Build complete: {bundle_path.name}")
    print(f"Size: {bundle_path.stat().st_size / 1024 / 1024:.1f} MB")
    print("=" * 50)
    print()
    print("Note: Dependencies will be automatically installed on first run.")


if __name__ == "__main__":
    main()
