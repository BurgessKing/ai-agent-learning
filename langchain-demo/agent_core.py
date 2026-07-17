"""LangChain Agent — 公交出行助手 (DeepSeek + LangChain 1.3)"""
import os, asyncio
from dotenv import load_dotenv
load_dotenv()

from langchain_openai import ChatOpenAI
from langchain.agents import create_agent
from tools import ALL_TOOLS

SYSTEM_PROMPT = """你是公交出行助手。用工具帮用户查线路、调车辆、算报价。信息不全就追问用户。回答简洁清晰。"""

def create_bus_agent():
    api_key = os.getenv("DEEPSEEK_API_KEY") or os.getenv("OPENAI_API_KEY")
    base_url = os.getenv("OPENAI_BASE_URL")
    if not api_key:
        raise RuntimeError("请设置 DEEPSEEK_API_KEY")

    llm = ChatOpenAI(
        model="deepseek-chat",
        temperature=0.3,
        api_key=api_key,
        base_url=base_url,
    )

    agent = create_agent(
        model=llm,
        tools=ALL_TOOLS,
        system_prompt=SYSTEM_PROMPT,
    )
    return agent

async def main():
    print("=" * 50)
    print("🚌 公交出行助手 (DeepSeek + LangChain 1.3)")
    print("=" * 50)

    agent = create_bus_agent()

    tests = [
        ("路线查询", "查一下从西湖到火车东站的公交路线"),
        ("车辆调度", "帮R001线路调度一辆大巴，2024年1月15号，35个人"),
        ("报价计算", "千岛湖包车，往返300公里，35人，大巴，2024年1月15号"),
    ]

    for name, query in tests:
        print(f"\n{'─'*40}")
        print(f"📋 {name}")
        print(f"👤 {query}")
        try:
            result = agent.invoke({"messages": [{"role": "user", "content": query}]})
            # 取最后一条消息作为回复
            msgs = result.get("messages", [])
            if msgs:
                last = msgs[-1]
                content = getattr(last, "content", str(last))
                print(f"🤖 {content}")
            else:
                print("🤖 (无响应)")
        except Exception as e:
            print(f"❌ 错误: {e}")

    print("\n" + "=" * 50)
    print("✅ 三场景测试完成")

if __name__ == "__main__":
    asyncio.run(main())
