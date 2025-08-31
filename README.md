# Azure OpenAI Deep Research Sample

Azure OpenAI Deep Researchを使用して自然言語クエリで調査を実行するPythonスクリプトです。

このプログラムは、Microsoftの公式ドキュメント「[Azure AI Foundry でエージェント ツールの Deep Research サンプルを試す](https://learn.microsoft.com/ja-jp/azure/ai-foundry/agents/how-to/tools/deep-research-samples?pivots=python)」を参考に作成されています。

## 機能

- ✅ .envファイルから環境変数を自動読み取り  
- ✅ コマンドライン引数で自然言語クエリを受け取り  
- ✅ 日本語でのメッセージとコメント  
- ✅ 環境設定の自動検証  

## セットアップ

### 1. 依存関係のインストール

```bash
pip install -r requirements.txt
```

### 2. 環境変数の設定

.env.exampleファイルを参考に.envファイルを作成して、必要な環境変数を設定してください：

```bash
# .env.exampleをコピーして.envファイルを作成
cp .env.example .env
```

その後、.envファイルを編集して適切な値を設定してください：

```bash
# Azure AI Project エンドポイント
PROJECT_ENDPOINT=https://your-project-name.region.api.azureml.ms

# Bing Grounding 接続リソース名
BING_RESOURCE_NAME=your-bing-connection-name

# メインモデルのデプロイメント名
MODEL_DEPLOYMENT_NAME=your-main-model-deployment

# Deep Research モデルのデプロイメント名
DEEP_RESEARCH_MODEL_DEPLOYMENT_NAME=o3-deepresearch
```

## 使用方法

```bash
# 基本的な使用方法
python main.py "調査したい内容"
```

### 使用例

```bash
# 市場調査
python main.py "日本のEV市場について調査してください"

# 技術動向分析
python main.py "AIの最新技術動向を分析してください"

# 企業分析
python main.py "株式会社ヘッドウォータースの株価から見た会社の成長度合いを調査してください"
```

## ファイル構成

```
azure-openai-deep-research-sample/
├── main.py              # メインスクリプト
├── requirements.txt     # 依存関係
├── README.md           # このファイル
└── .env                # 環境変数設定ファイル（要作成）
```

## 主な改良点

元のコードからの主な変更内容：

1. **環境変数の読み込み**: `python-dotenv`を使用して.envファイルから自動読み取り
2. **CLIインターフェース**: コマンドライン引数で調査クエリを指定可能
3. **日本語化**: コメントとメッセージをすべて日本語に変更
4. **エラーハンドリング**: 環境変数の不足時に適切な日本語メッセージを表示
5. **最小限の変更**: コア機能は変更せず、必要最低限の改修のみ実施

## 動作確認状況

**最終確認日**: 2025年8月31日

### 動作確認済み環境
- ✅ Python 3.12
- ✅ Windows 11
- ✅ Azure AI Foundry

## エラーメッセージ

- **引数不足**: 使用方法を日本語で表示
- **環境変数不足**: 必要な変数と設定方法を日本語で案内
- **Azure接続エラー**: 適切なエラーメッセージを表示