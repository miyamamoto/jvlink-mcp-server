# JVLink MCP Server

**Claudeに話しかけるだけで、競馬データを自由に分析できます。**

SQLを書く必要はありません。自然な日本語で質問すれば、過去のレース結果、騎手成績、血統傾向など、あらゆる競馬データを調べられます。

## こんな質問ができます

### レース・成績について
```
今年のG1レース一覧を見せて
日本ダービーの過去10年の結果を教えて
東京競馬場の芝1600mで行われたレースを調べて
```

### 人気・オッズの傾向
```
1番人気の勝率はどのくらい？
G1レースで1番人気が飛んだレースを教えて
10番人気以下で勝った馬の共通点は？
```

### 騎手・調教師
```
ルメール騎手の今年の成績を教えて
東京競馬場で勝率が高い騎手は誰？
藤沢和雄厩舎の重賞成績を調べて
```

### 血統・種牡馬
```
ディープインパクト産駒の芝での成績は？
キズナ産駒の距離別成績を教えて
母父サンデーサイレンスの馬の成績は？
```

### コース・距離・馬場
```
中山芝2000mで内枠と外枠、どっちが有利？
重馬場で強い種牡馬を教えて
阪神の外回りコースの傾向は？
```

### 馬体重・上がりタイム
```
馬体重500kg以上の馬の成績は？
上がり3F最速で勝った馬を調べて
前走から馬体重が10kg以上増えた馬の成績は？
```

### 複合条件・予想に役立つ分析
```
東京芝1600mで、1番人気×内枠×前走1着の馬の勝率は？
休み明け（中10週以上）の1番人気の信頼度は？
前走G1で負けた馬が次走G2以下で巻き返した例を教えて
```

## セットアップ

### 必要なもの

1. **競馬データベース** - [jrvltsql](https://github.com/miyamamoto/jrvltsql) で作成
2. **Claude Desktop** または **Claude Code**

### Claude Desktopで使う

`claude_desktop_config.json` に追加:

```json
{
  "mcpServers": {
    "jvlink": {
      "command": "uv",
      "args": [
        "run",
        "--directory",
        "C:\Users\yourname\jvlink-mcp-server",
        "python",
        "-m",
        "jvlink_mcp_server.server"
      ],
      "env": {
        "DB_TYPE": "sqlite",
        "DB_PATH": "C:/Users/yourname/jrvltsql/data/keiba.db"
      }
    }
  }
}
```

パスは環境に合わせて変更してください。Claude Desktopを再起動すれば使えます。

### Claude Codeで使う

```bash
claude mcp add jvlink \
  -e DB_TYPE=sqlite \
  -e DB_PATH=/path/to/keiba.db \
  -- uv run --directory /path/to/jvlink-mcp-server python -m jvlink_mcp_server.server
```

## 使い方のコツ

### 1. まずは気軽に質問
思いついたことをそのまま聞いてみてください。Claudeが適切なデータを探して回答します。

### 2. 具体的な条件を追加
「東京の」「芝の」「1600mの」「G1の」など、条件を追加するとより詳細な分析ができます。

### 3. 比較を依頼
「AとBを比較して」「年度別に推移を見せて」など、比較分析も得意です。

### 4. 深掘りする
回答を見て気になったことがあれば、続けて質問してください。会話の流れで分析を深められます。

## もっと詳しく

### 質問例をもっと見たい
→ [サンプル質問集](docs/SAMPLE_QUESTIONS.md)

初級から上級まで、200以上の質問例があります。

### 技術的な詳細を知りたい
→ [データベース構成](docs/DATABASE_SETUP.md) / [クエリガイドライン](QUERY_GUIDELINES.md)

開発者向けの技術情報です。

## ライセンス

Apache License 2.0
