# JVLink MCP Server — ワンラインインストーラー (Windows PowerShell)
# irm https://raw.githubusercontent.com/miyamamoto/jvlink-mcp-server/master/install.ps1 | iex
$ErrorActionPreference = "Stop"

function Write-OK($msg)   { Write-Host "  ✓ " -ForegroundColor Green -NoNewline; Write-Host $msg }
function Write-Info($msg)  { Write-Host "  ℹ " -ForegroundColor Cyan -NoNewline; Write-Host $msg }
function Write-Warn($msg)  { Write-Host "  ⚠ " -ForegroundColor Yellow -NoNewline; Write-Host $msg }
function Write-Err($msg)   { Write-Host "  ✗ " -ForegroundColor Red -NoNewline; Write-Host $msg }
function Write-Header($msg){ Write-Host "`n  $msg" -ForegroundColor White -BackgroundColor DarkBlue }

$InstallDir = if ($env:JVLINK_MCP_DIR) { $env:JVLINK_MCP_DIR } else { "$HOME\jvlink-mcp-server" }
$JrvltsqlDir = if ($env:JRVLTSQL_DIR) { $env:JRVLTSQL_DIR } else { "$HOME\jrvltsql" }

Write-Host ""
Write-Host "  ╔════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "  ║   JVLink MCP Server インストーラー v0.7.0  ║" -ForegroundColor Cyan
Write-Host "  ╚════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""

# ═══════════════════════════════════════════
# 1. 前提条件チェック
# ═══════════════════════════════════════════
Write-Header "1/5  前提条件チェック"

# Python
$py = $null
foreach ($cmd in @("python", "python3", "py")) {
    try {
        $ver = & $cmd -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')" 2>$null
        if ($ver) { $py = $cmd; break }
    } catch {}
}
if (-not $py) {
    Write-Err "Python が見つかりません"
    Write-Host "    Python 3.11以上をインストールしてください"
    Start-Process "https://www.python.org/downloads/"
    exit 1
}
$pyVer = & $py -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')"
$pyParts = $pyVer -split '\.'
if ([int]$pyParts[0] -lt 3 -or ([int]$pyParts[0] -eq 3 -and [int]$pyParts[1] -lt 11)) {
    Write-Err "Python $pyVer ですが、3.11以上が必要です"
    Start-Process "https://www.python.org/downloads/"
    exit 1
}
Write-OK "Python $pyVer"

# Git
try { $gitVer = git --version 2>$null } catch { $gitVer = $null }
if (-not $gitVer) {
    Write-Err "Git が見つかりません"
    Start-Process "https://git-scm.com/downloads"
    exit 1
}
Write-OK "Git $($gitVer -replace 'git version ','')"

# uv
try { $uvVer = uv --version 2>$null } catch { $uvVer = $null }
if (-not $uvVer) {
    Write-Info "uv をインストール中..."
    & $py -m pip install uv --quiet 2>$null
    if ($LASTEXITCODE -ne 0) {
        irm https://astral.sh/uv/install.ps1 | iex
    }
    Write-OK "uv インストール完了"
} else {
    Write-OK "uv $($uvVer -replace 'uv ','')"
}

# ═══════════════════════════════════════════
# 2. MCP サーバーインストール
# ═══════════════════════════════════════════
Write-Header "2/5  MCP サーバーインストール"

if (Test-Path "$InstallDir\.git") {
    Write-Info "既存のインストールを更新中..."
    Push-Location $InstallDir
    git pull --ff-only 2>$null
    if ($LASTEXITCODE -ne 0) { git pull }
    Pop-Location
    Write-OK "最新版に更新しました"
} else {
    Write-Info "リポジトリをクローン中..."
    git clone https://github.com/miyamamoto/jvlink-mcp-server.git $InstallDir
    Write-OK "クローン完了 → $InstallDir"
}

Push-Location $InstallDir
Write-Info "依存パッケージをインストール中..."
uv sync --quiet 2>$null
if ($LASTEXITCODE -ne 0) { uv sync }
Write-OK "依存パッケージ インストール完了"
Pop-Location

# ═══════════════════════════════════════════
# 3. データベース確認
# ═══════════════════════════════════════════
Write-Header "3/5  競馬データベース確認"

$DbPath = ""
$searchPaths = @(
    "$HOME\keiba.db",
    "$HOME\data\keiba.db",
    "$HOME\jrvltsql\data\keiba.db",
    "$JrvltsqlDir\data\keiba.db",
    "$env:USERPROFILE\jrvltsql\data\keiba.db"
)

foreach ($p in $searchPaths) {
    if (Test-Path $p) {
        $DbPath = $p
        break
    }
}

if ($DbPath) {
    $size = (Get-Item $DbPath).Length / 1MB
    Write-OK "データベース検出: $DbPath ($([math]::Round($size, 1)) MB)"
} else {
    Write-Warn "keiba.db が見つかりません"
    Write-Host ""
    Write-Host "    競馬データベースの作成には以下が必要です:"
    Write-Host ""
    Write-Host "    1. JRA-VAN DataLab 契約（中央競馬データ）"
    Write-Host "       → https://jra-van.jp/dlb/"
    Write-Host ""
    Write-Host "    2. 地方競馬DATA 契約（地方競馬データ・任意）"
    Write-Host "       → https://www.keiba-data.com/"
    Write-Host ""
    Write-Host "    3. jrvltsql でデータベースを構築"
    Write-Host "       → https://github.com/miyamamoto/jrvltsql"
    Write-Host ""

    $openJra = Read-Host "JRA-VAN DataLabの契約ページをブラウザで開きますか？ [Y/n]"
    if ($openJra -ne "n") {
        Start-Process "https://jra-van.jp/dlb/"
        Write-Info "ブラウザで JRA-VAN DataLab のページを開きました"
    }

    Write-Host ""
    $installJrvltsql = Read-Host "jrvltsql も一緒にインストールしますか？ [Y/n]"
    if ($installJrvltsql -ne "n") {
        Write-Header "    jrvltsql インストール"
        if ([int]$pyParts[0] -lt 3 -or ([int]$pyParts[0] -eq 3 -and [int]$pyParts[1] -lt 12)) {
            Write-Err "jrvltsql 2.0.0にはPython 3.12以上が必要です（検出: $pyVer）"
            exit 1
        }
        if (Test-Path "$JrvltsqlDir\.git") {
            Push-Location $JrvltsqlDir
            git pull --ff-only 2>$null
            if ($LASTEXITCODE -ne 0) { git pull }
            Pop-Location
            Write-OK "jrvltsql を更新しました"
        } else {
            git clone https://github.com/miyamamoto/jrvltsql.git $JrvltsqlDir
            Write-OK "jrvltsql をクローンしました → $JrvltsqlDir"
        }
        Push-Location $JrvltsqlDir
        uv sync --quiet 2>$null
        if ($LASTEXITCODE -ne 0) { uv sync }
        Pop-Location
        Write-OK "jrvltsql インストール完了"
        Write-Host ""
        Write-Info "データベース構築は以下を実行してください:"
        Write-Host "    cd $JrvltsqlDir"
        Write-Host "    uv run jltsql init"
        Write-Host "    uv run jltsql create-tables --db sqlite"
        Write-Host ""
    }

    $manualDb = Read-Host "keiba.db のパスを入力（後で設定する場合はEnter）"
    if ($manualDb -and (Test-Path $manualDb)) {
        $DbPath = $manualDb
        Write-OK "データベース: $DbPath"
    } elseif ($manualDb) {
        Write-Warn "ファイルが見つかりません: $manualDb"
        $DbPath = $manualDb
    }
}

if (-not $DbPath) {
    $DbPath = "$HOME\keiba.db"
    Write-Info "DB_PATH のデフォルト: $DbPath（後で変更してください）"
}

# ═══════════════════════════════════════════
# 4. MCPクライアント設定
# ═══════════════════════════════════════════
Write-Header "4/5  MCPクライアント設定"

$ClaudeConfig = "$env:APPDATA\Claude\claude_desktop_config.json"

Write-Host ""
Write-Host "  MCPクライアントを選択してください:"
Write-Host ""
Write-Host "    1) Claude Desktop （設定ファイルを自動生成）"
Write-Host "    2) Claude Code CLI （コマンドを表示）"
Write-Host "    3) Cursor / VS Code / Windsurf （JSONを表示）"
Write-Host "    4) スキップ （後で手動設定）"
Write-Host ""

$choice = Read-Host "選択 [1-4]"

$installDirEscaped = $InstallDir -replace '\\', '/'
$dbPathEscaped = $DbPath -replace '\\', '/'

switch ($choice) {
    "1" {
        $claudeDir = Split-Path $ClaudeConfig
        if (-not (Test-Path $claudeDir)) { New-Item -ItemType Directory -Path $claudeDir -Force | Out-Null }

        $mcpEntry = @{
            command = "uv.exe"
            args = @("run", "--directory", $installDirEscaped, "python", "-m", "jvlink_mcp_server.server")
            env = @{ DB_TYPE = "sqlite"; DB_PATH = $dbPathEscaped }
        }

        if (Test-Path $ClaudeConfig) {
            $cfg = Get-Content $ClaudeConfig -Raw | ConvertFrom-Json
            if (-not $cfg.mcpServers) {
                $cfg | Add-Member -NotePropertyName mcpServers -NotePropertyValue @{} -Force
            }
            if ($cfg.mcpServers.PSObject.Properties.Name -contains "jvlink") {
                Write-OK "Claude Desktop 設定に jvlink は既に存在します"
            } else {
                $cfg.mcpServers | Add-Member -NotePropertyName jvlink -NotePropertyValue $mcpEntry -Force
                $cfg | ConvertTo-Json -Depth 10 | Set-Content $ClaudeConfig -Encoding UTF8
                Write-OK "Claude Desktop 設定に jvlink を追加しました"
            }
        } else {
            @{ mcpServers = @{ jvlink = $mcpEntry } } | ConvertTo-Json -Depth 10 | Set-Content $ClaudeConfig -Encoding UTF8
            Write-OK "Claude Desktop 設定ファイルを作成しました"
        }
        Write-Info "設定ファイル: $ClaudeConfig"
    }
    "2" {
        Write-Host ""
        Write-Host "  以下のコマンドを実行してください:" -ForegroundColor Green
        Write-Host ""
        Write-Host "  claude mcp add jvlink ``"
        Write-Host "    -e DB_TYPE=sqlite ``"
        Write-Host "    -e DB_PATH=$dbPathEscaped ``"
        Write-Host "    -- uv run --directory $installDirEscaped python -m jvlink_mcp_server.server"
        Write-Host ""
    }
    "3" {
        Write-Host ""
        Write-Host "  以下のJSONを設定ファイルに追加してください:" -ForegroundColor Green
        Write-Host ""
        Write-Host "  Cursor:   .cursor/mcp.json"
        Write-Host "  VS Code:  .vscode/mcp.json"
        Write-Host "  Windsurf: ~/.codeium/windsurf/mcp_config.json"
        Write-Host ""
        @{
            mcpServers = @{
                jvlink = @{
                    command = "uv.exe"
                    args = @("run", "--directory", $installDirEscaped, "python", "-m", "jvlink_mcp_server.server")
                    env = @{ DB_TYPE = "sqlite"; DB_PATH = $dbPathEscaped }
                }
            }
        } | ConvertTo-Json -Depth 10
        Write-Host ""
    }
    default {
        Write-Info "スキップしました。READMEを参考に手動設定してください。"
    }
}

# ═══════════════════════════════════════════
# 5. 完了
# ═══════════════════════════════════════════
Write-Header "5/5  インストール完了！"

Write-Host ""
Write-Host "  JVLink MCP Server のインストールが完了しました 🎉" -ForegroundColor Green
Write-Host ""
Write-Host "  📁 インストール先: $InstallDir"
Write-Host "  🗄️  データベース:   $DbPath"
Write-Host ""

if (-not (Test-Path $DbPath)) {
    Write-Warn "keiba.db がまだ作成されていません。"
    Write-Host "    jrvltsql の quickstart を実行してデータベースを構築してください。"
    Write-Host "    → https://github.com/miyamamoto/jrvltsql#quickstart"
    Write-Host ""
}

Write-Host "  📖 ドキュメント: https://github.com/miyamamoto/jvlink-mcp-server"
Write-Host "  🐛 バグ報告:     https://github.com/miyamamoto/jvlink-mcp-server/issues"
Write-Host ""
