import os, time, sys
from typing import Optional
from dotenv import load_dotenv

# .envファイルから環境変数を読み込み
load_dotenv()

# コマンドライン引数の処理
if len(sys.argv) < 2:
    print("使用法: python main.py \"調査したい内容\"")
    print("例: python main.py \"株式会社ヘッドウォータースの株価から見た会社の成長度合いを調査してください。\"")
    sys.exit(1)

query = sys.argv[1]

# 必要な環境変数の確認
required_vars = ["PROJECT_ENDPOINT", "BING_RESOURCE_NAME", "DEEP_RESEARCH_MODEL_DEPLOYMENT_NAME", "MODEL_DEPLOYMENT_NAME"]
missing_vars = [var for var in required_vars if not os.getenv(var)]

if missing_vars:
    print("必要な環境変数が設定されていません:")
    for var in missing_vars:
        print(f"  {var}")
    print("\n.envファイルを作成して必要な変数を設定してください。")
    print("(.env.exampleを参考にしてください)")
    sys.exit(1)

# Azure関連のインポート
from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential
from azure.ai.agents import AgentsClient
from azure.ai.agents.models import DeepResearchTool, MessageRole, ThreadMessage


def fetch_and_print_new_agent_response(
    thread_id: str,
    agents_client: AgentsClient,
    last_message_id: Optional[str] = None,
) -> Optional[str]:
    # エージェントからの最新の応答を取得
    response = agents_client.messages.get_last_message_by_role(
        thread_id=thread_id,
        role=MessageRole.AGENT,
    )
    if not response or response.id == last_message_id:
        return last_message_id  # 新しいコンテンツがない場合

    print("\nエージェントの応答:")
    print("\n".join(t.text.value for t in response.text_messages))

    for ann in response.url_citation_annotations:
        print(f"URL引用: [{ann.url_citation.title}]({ann.url_citation.url})")

    return response.id


def create_research_summary(
        message : ThreadMessage,
        filepath: str = "research_summary.md"
) -> None:
    if not message:
        print("メッセージコンテンツが提供されていないため、調査要約を作成できません。")
        return

    with open(filepath, "w", encoding="utf-8") as fp:
        # テキスト要約を書き込み
        text_summary = "\n\n".join([t.text.value.strip() for t in message.text_messages])
        fp.write(text_summary)

        # URL引用がある場合は追加
        if message.url_citation_annotations:
            fp.write("\n\n## 参考文献\n")
            seen_urls = set()
            for ann in message.url_citation_annotations:
                url = ann.url_citation.url
                title = ann.url_citation.title or url
                if url not in seen_urls:
                    fp.write(f"- [{title}]({url})\n")
                    seen_urls.add(url)

    print(f"調査要約を '{filepath}' に書き込みました。")



project_client = AIProjectClient(
    endpoint=os.environ["PROJECT_ENDPOINT"],
    credential=DefaultAzureCredential(),
)

conn_id = project_client.connections.get(name=os.environ["BING_RESOURCE_NAME"]).id


# Bing接続IDとDeep Researchモデルデプロイメント名でDeep Researchツールを初期化
deep_research_tool = DeepResearchTool(
    bing_grounding_connection_id=conn_id,
    deep_research_model=os.environ["DEEP_RESEARCH_MODEL_DEPLOYMENT_NAME"],
)

# Deep Researchツールを使ってエージェントを作成し、エージェント実行を処理
with project_client:

    with project_client.agents as agents_client:

        # Deep Researchツールが添付された新しいエージェントを作成
        # 注意: 既存のエージェントにDeep Researchを追加するには、`get_agent(agent_id)`で取得し、
        # Deep Researchツールでエージェントをアップデートしてください
        agent = agents_client.create_agent(
            model=os.environ["MODEL_DEPLOYMENT_NAME"],
            name="my-agent",
            instructions="あなたは科学的トピックの研究を支援する有用なエージェントです。",
            tools=deep_research_tool.definitions,
        )

        # [END create_agent_with_deep_research_tool]
        print(f"エージェントを作成しました、ID: {agent.id}")

        # 通信用のスレッドを作成
        thread = agents_client.threads.create()
        print(f"スレッドを作成しました、ID: {thread.id}")

        # スレッドにメッセージを作成
        message = agents_client.messages.create(
            thread_id=thread.id,
            role="user",
            content=query,
        )
        print(f"メッセージを作成しました、ID: {message.id}")

        print(f"メッセージの処理を開始しています... 完了まで数分かかる場合があります。しばらくお待ちください！")
        # 実行ステータスがキューまたは進行中の間、実行をポーリング
        run = agents_client.runs.create(thread_id=thread.id, agent_id=agent.id)
        last_message_id = None
        while run.status in ("queued", "in_progress"):
            time.sleep(1)
            run = agents_client.runs.get(thread_id=thread.id, run_id=run.id)

            last_message_id = fetch_and_print_new_agent_response(
                thread_id=thread.id,
                agents_client=agents_client,
                last_message_id=last_message_id,
            )
            print(f"実行ステータス: {run.status}")

        print(f"実行が完了しました。ステータス: {run.status}, ID: {run.id}")

        if run.status == "failed":
            print(f"実行に失敗しました: {run.last_error}")

        # スレッドからエージェントの最終メッセージを取得し、調査要約を作成
        final_message = agents_client.messages.get_last_message_by_role(
            thread_id=thread.id, role=MessageRole.AGENT
        )
        if final_message:
            create_research_summary(final_message)

        # 実行が完了したらエージェントをクリーンアップして削除
        # 注意: 後でエージェントを再利用する予定がある場合は、この行をコメントアウトしてください
        agents_client.delete_agent(agent.id)
        print("エージェントを削除しました")