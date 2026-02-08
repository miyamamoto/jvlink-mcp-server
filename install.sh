#!/usr/bin/env bash
# JVLink MCP Server — ワンラインインストーラー
# curl -fsSL https://raw.githubusercontent.com/miyamamoto/jvlink-mcp-server/master/install.sh | bash
set -euo pipefail

# ─── 色 ───
RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'; BLUE='\033[0;34m'; BOLD='\033[1m'; NC='\033[0m'
info()  { echo -e "${BLUE}ℹ${NC}  $*"; }
ok()    { echo -e "${GREEN}✓${NC}  $*"; }
warn()  { echo -e "${YELLOW}⚠${NC}  $*"; }
err()   { echo -e "${RED}✗${NC}  $*"; }
header(){ echo -e "\n${BOLD}$*${NC}"; }

# ─── ブラウザで開く ───
open_url() {
    local url="$1"
    if command -v xdg-open &>/dev/null; then
        xdg-open "$url" 2>/dev/null || true
    elif command -v open &>/dev/null; then
        open "$url" 2>/dev/null || true
    elif command -v start &>/dev/null; then
        start "$url" 2>/dev/null || true
    elif [[ -n "${BROWSER:-}" ]]; then
        "$BROWSER" "$url" 2>/dev/null || true
    fi
}

# ─── OS検出 ───
detect_os() {
    case "$(uname -s)" in
        MINGW*|MSYS*|CYGWIN*) echo "windows" ;;
        Darwin*)               echo "macos"   ;;
        Linux*)                echo "linux"   ;;
        *)                     echo "unknown" ;;
    esac
}

OS=$(detect_os)
INSTALL_DIR="${JVLINK_MCP_DIR:-$HOME/jvlink-mcp-server}"
JRVLTSQL_DIR="${JRVLTSQL_DIR:-$HOME/jrvltsql}"

echo -e "${BOLD}"
echo "╔════════════════════════════════════════════╗"
echo "║   JVLink MCP Server インストーラー v0.5.0  ║"
echo "╚════════════════════════════════════════════╝"
echo -e "${NC}"

# ═══════════════════════════════════════════
# 1. 前提条件チェック
# ═══════════════════════════════════════════
header "1/5  前提条件チェック"

# Python
if command -v python3 &>/dev/null; then
    PY=python3
elif command -v python &>/dev/null; then
    PY=python
else
    err "Python が見つかりません"
    echo "    Python 3.11以上をインストールしてください: https://www.python.org/downloads/"
    open_url "https://www.python.org/downloads/"
    exit 1
fi

PY_VER=$($PY -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
PY_MAJOR=$($PY -c 'import sys; print(sys.version_info.major)')
PY_MINOR=$($PY -c 'import sys; print(sys.version_info.minor)')

if [[ "$PY_MAJOR" -lt 3 ]] || [[ "$PY_MAJOR" -eq 3 && "$PY_MINOR" -lt 11 ]]; then
    err "Python $PY_VER が検出されましたが、3.11以上が必要です"
    open_url "https://www.python.org/downloads/"
    exit 1
fi
ok "Python $PY_VER"

# Git
if ! command -v git &>/dev/null; then
    err "Git が見つかりません"
    echo "    https://git-scm.com/downloads"
    open_url "https://git-scm.com/downloads"
    exit 1
fi
ok "Git $(git --version | awk '{print $3}')"

# uv
if ! command -v uv &>/dev/null; then
    info "uv をインストール中..."
    if command -v pip3 &>/dev/null; then
        pip3 install uv --quiet
    elif command -v pip &>/dev/null; then
        pip install uv --quiet
    else
        curl -LsSf https://astral.sh/uv/install.sh | sh
        export PATH="$HOME/.cargo/bin:$PATH"
    fi
    ok "uv インストール完了"
else
    ok "uv $(uv --version 2>/dev/null | awk '{print $2}' || echo '')"
fi

# ═══════════════════════════════════════════
# 2. MCP サーバーインストール
# ═══════════════════════════════════════════
header "2/5  MCP サーバーインストール"

if [[ -d "$INSTALL_DIR/.git" ]]; then
    info "既存のインストールを更新中..."
    cd "$INSTALL_DIR"
    git pull --ff-only 2>/dev/null || git pull
    ok "最新版に更新しました"
else
    info "リポジトリをクローン中..."
    git clone https://github.com/miyamamoto/jvlink-mcp-server.git "$INSTALL_DIR"
    cd "$INSTALL_DIR"
    ok "クローン完了 → $INSTALL_DIR"
fi

info "依存パッケージをインストール中..."
uv sync --quiet 2>/dev/null || uv sync
ok "依存パッケージ インストール完了"

# ═══════════════════════════════════════════
# 3. データベース確認
# ═══════════════════════════════════════════
header "3/5  競馬データベース確認"

DB_PATH=""

# 既知のパスを探索
SEARCH_PATHS=(
    "$HOME/keiba.db"
    "$HOME/data/keiba.db"
    "$HOME/jrvltsql/data/keiba.db"
    "$JRVLTSQL_DIR/data/keiba.db"
)

if [[ "$OS" == "windows" ]]; then
    SEARCH_PATHS+=(
        "$USERPROFILE/jrvltsql/data/keiba.db"
        "C:/Users/$USERNAME/jrvltsql/data/keiba.db"
    )
fi

for p in "${SEARCH_PATHS[@]}"; do
    if [[ -f "$p" ]]; then
        DB_PATH="$p"
        break
    fi
done

if [[ -n "$DB_PATH" ]]; then
    DB_SIZE=$(du -h "$DB_PATH" 2>/dev/null | awk '{print $1}' || echo "?")
    ok "データベース検出: $DB_PATH ($DB_SIZE)"
else
    warn "keiba.db が見つかりません"
    echo ""
    echo "    競馬データベースの作成には以下が必要です:"
    echo ""
    echo "    1. JRA-VAN DataLab 契約（中央競馬データ）"
    echo "       → https://jra-van.jp/dlb/"
    echo ""
    echo "    2. 地方競馬DATA 契約（地方競馬データ・任意）"
    echo "       → https://www.keiba-data.com/"
    echo ""
    echo "    3. jrvltsql でデータベースを構築"
    echo "       → https://github.com/miyamamoto/jrvltsql"
    echo ""

    # ブラウザで開く
    read -rp "$(echo -e "${YELLOW}JRA-VAN DataLabの契約ページをブラウザで開きますか？ [Y/n]${NC} ")" OPEN_JRA
    if [[ "${OPEN_JRA,,}" != "n" ]]; then
        open_url "https://jra-van.jp/dlb/"
        info "ブラウザで JRA-VAN DataLab のページを開きました"
    fi

    echo ""
    read -rp "$(echo -e "${YELLOW}jrvltsql も一緒にインストールしますか？ [Y/n]${NC} ")" INSTALL_JRVLTSQL
    if [[ "${INSTALL_JRVLTSQL,,}" != "n" ]]; then
        header "    jrvltsql インストール"
        if [[ -d "$JRVLTSQL_DIR/.git" ]]; then
            cd "$JRVLTSQL_DIR"
            git pull --ff-only 2>/dev/null || git pull
            ok "jrvltsql を更新しました"
        else
            git clone https://github.com/miyamamoto/jrvltsql.git "$JRVLTSQL_DIR"
            ok "jrvltsql をクローンしました → $JRVLTSQL_DIR"
        fi
        cd "$JRVLTSQL_DIR"
        if command -v pip3 &>/dev/null; then
            pip3 install -e . --quiet 2>/dev/null || pip3 install -e .
        else
            pip install -e . --quiet 2>/dev/null || pip install -e .
        fi
        ok "jrvltsql インストール完了"
        echo ""
        info "データベース構築は Windows 上で以下を実行してください:"
        echo "    cd $JRVLTSQL_DIR"
        echo "    python scripts/quickstart.py"
        echo ""
    fi

    # DBパスを手動入力
    read -rp "$(echo -e "${YELLOW}keiba.db のパスを入力（後で設定する場合はEnter）:${NC} ")" MANUAL_DB
    if [[ -n "$MANUAL_DB" && -f "$MANUAL_DB" ]]; then
        DB_PATH="$MANUAL_DB"
        ok "データベース: $DB_PATH"
    elif [[ -n "$MANUAL_DB" ]]; then
        warn "ファイルが見つかりません: $MANUAL_DB"
        DB_PATH="$MANUAL_DB"  # 設定ファイルには書く
    fi
fi

# DBパスのデフォルト
if [[ -z "$DB_PATH" ]]; then
    DB_PATH="$HOME/keiba.db"
    info "DB_PATH のデフォルト: $DB_PATH（後で変更してください）"
fi

# ═══════════════════════════════════════════
# 4. MCPクライアント設定
# ═══════════════════════════════════════════
header "4/5  MCPクライアント設定"

# Claude Desktop 設定
if [[ "$OS" == "macos" ]]; then
    CLAUDE_CONFIG="$HOME/Library/Application Support/Claude/claude_desktop_config.json"
elif [[ "$OS" == "windows" ]]; then
    CLAUDE_CONFIG="${APPDATA:-$HOME/AppData/Roaming}/Claude/claude_desktop_config.json"
else
    CLAUDE_CONFIG="$HOME/.config/claude/claude_desktop_config.json"
fi

UV_CMD="uv"
[[ "$OS" == "windows" ]] && UV_CMD="uv.exe"

generate_mcp_config() {
    cat <<JSONEOF
{
  "mcpServers": {
    "jvlink": {
      "command": "$UV_CMD",
      "args": ["run", "--directory", "$INSTALL_DIR", "python", "-m", "jvlink_mcp_server.server"],
      "env": {
        "DB_TYPE": "sqlite",
        "DB_PATH": "$DB_PATH"
      }
    }
  }
}
JSONEOF
}

echo ""
echo "  MCPクライアントを選択してください:"
echo ""
echo "    1) Claude Desktop （設定ファイルを自動生成）"
echo "    2) Claude Code CLI （コマンドを表示）"
echo "    3) Cursor / VS Code / Windsurf （JSONを表示）"
echo "    4) スキップ （後で手動設定）"
echo ""

read -rp "$(echo -e "${YELLOW}選択 [1-4]:${NC} ")" CLIENT_CHOICE

case "${CLIENT_CHOICE:-1}" in
    1)
        # Claude Desktop
        CLAUDE_DIR=$(dirname "$CLAUDE_CONFIG")
        mkdir -p "$CLAUDE_DIR"

        if [[ -f "$CLAUDE_CONFIG" ]]; then
            # 既存の設定ファイルがある場合
            if $PY -c "
import json, sys
with open('$CLAUDE_CONFIG') as f:
    cfg = json.load(f)
servers = cfg.setdefault('mcpServers', {})
if 'jvlink' in servers:
    print('EXISTS')
    sys.exit(0)
servers['jvlink'] = {
    'command': '$UV_CMD',
    'args': ['run', '--directory', '$INSTALL_DIR', 'python', '-m', 'jvlink_mcp_server.server'],
    'env': {'DB_TYPE': 'sqlite', 'DB_PATH': '$DB_PATH'}
}
with open('$CLAUDE_CONFIG', 'w') as f:
    json.dump(cfg, f, indent=2, ensure_ascii=False)
print('ADDED')
" 2>/dev/null | grep -q "ADDED"; then
                ok "Claude Desktop 設定に jvlink を追加しました"
            elif $PY -c "
import json
with open('$CLAUDE_CONFIG') as f:
    cfg = json.load(f)
if 'jvlink' in cfg.get('mcpServers', {}):
    print('EXISTS')
" 2>/dev/null | grep -q "EXISTS"; then
                ok "Claude Desktop 設定に jvlink は既に存在します"
            fi
        else
            generate_mcp_config > "$CLAUDE_CONFIG"
            ok "Claude Desktop 設定ファイルを作成しました"
        fi
        info "設定ファイル: $CLAUDE_CONFIG"
        ;;
    2)
        # Claude Code
        echo ""
        echo -e "${GREEN}以下のコマンドを実行してください:${NC}"
        echo ""
        echo "  claude mcp add jvlink \\"
        echo "    -e DB_TYPE=sqlite \\"
        echo "    -e DB_PATH=$DB_PATH \\"
        echo "    -- uv run --directory $INSTALL_DIR python -m jvlink_mcp_server.server"
        echo ""
        ;;
    3)
        # JSON表示
        echo ""
        echo -e "${GREEN}以下のJSONを設定ファイルに追加してください:${NC}"
        echo ""
        echo "  Cursor:   .cursor/mcp.json"
        echo "  VS Code:  .vscode/mcp.json"
        echo "  Windsurf: ~/.codeium/windsurf/mcp_config.json"
        echo ""
        generate_mcp_config
        echo ""
        ;;
    4)
        info "スキップしました。READMEを参考に手動設定してください。"
        ;;
esac

# ═══════════════════════════════════════════
# 5. 完了
# ═══════════════════════════════════════════
header "5/5  インストール完了！"

echo ""
echo -e "  ${GREEN}${BOLD}JVLink MCP Server のインストールが完了しました 🎉${NC}"
echo ""
echo "  📁 インストール先: $INSTALL_DIR"
echo "  🗄️  データベース:   $DB_PATH"
echo ""

if [[ ! -f "$DB_PATH" ]]; then
    echo -e "  ${YELLOW}⚠ keiba.db がまだ作成されていません。${NC}"
    echo "    Windows上で jrvltsql の quickstart を実行してデータベースを構築してください。"
    echo "    → https://github.com/miyamamoto/jrvltsql#quickstart"
    echo ""
fi

echo "  📖 ドキュメント: https://github.com/miyamamoto/jvlink-mcp-server"
echo "  🐛 バグ報告:     https://github.com/miyamamoto/jvlink-mcp-server/issues"
echo ""
