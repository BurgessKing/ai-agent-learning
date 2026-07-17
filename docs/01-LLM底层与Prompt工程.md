# 01 — LLM 底层与 Prompt 工程

> **核心原则**：框架两三年换一代，底层接口十年不变。先搞懂大模型那个接口到底在干嘛，框架后面就是一层皮。
>
> **学习周期**：Day 1-7 | **目标**：能用原生 API 写出一个带工具的 Agent，彻底理解消息格式

---

## 第一阶段：LLM 原生 API（Day 1-3）

### 1.1 别上框架，直接调 API

```python
"""
用 httpx 直接调 DeepSeek API（兼容 OpenAI 格式）
搞懂：System Prompt / User Message / Assistant Message / Tool Call 到底是什么
"""
import httpx, json

API_KEY = "sk-xxx"
BASE_URL = "https://api.deepseek.com/v1"

def call_llm(messages: list[dict], temperature: float = 0.7, max_tokens: int = 1024) -> dict:
    """原生 LLM 调用 — 不依赖任何框架"""
    resp = httpx.post(
        f"{BASE_URL}/chat/completions",
        headers={"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"},
        json={
            "model": "deepseek-chat",
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        },
        timeout=60
    )
    return resp.json()


# ===== 实验1: System Prompt 到底怎么影响输出 =====

# 不加 System Prompt
r1 = call_llm([{"role": "user", "content": "杭州有哪些公交线路？"}])
print("无 System:", r1["choices"][0]["message"]["content"][:100])

# 加 System Prompt
r2 = call_llm([
    {"role": "system", "content": "你是杭州公交专家，只回答公交相关问题。回答简洁，不超过3句。"},
    {"role": "user", "content": "杭州有哪些公交线路？"}
])
print("有 System:", r2["choices"][0]["message"]["content"][:100])


# ===== 实验2: Temperature 拉高拉低有什么区别 =====

for temp in [0, 0.5, 1.0]:
    r = call_llm([
        {"role": "user", "content": "用一个词形容杭州的公交系统"}
    ], temperature=temp)
    print(f"Temperature={temp}: {r['choices'][0]['message']['content']}")


# ===== 实验3: Token 到底怎么算钱 =====

usage = r1.get("usage", {})
prompt_tokens = usage.get("prompt_tokens", 0)
completion_tokens = usage.get("completion_tokens", 0)
total_tokens = usage.get("total_tokens", 0)

# DeepSeek 定价: 输入 ¥1/百万token, 输出 ¥2/百万token
cost = (prompt_tokens / 1_000_000) * 1 + (completion_tokens / 1_000_000) * 2
print(f"本次调用: prompt={prompt_tokens} tokens, completion={completion_tokens} tokens")
print(f"花费: ¥{cost:.6f}")
```

#### 📝 必须搞懂的事

| 概念 | 一句话 | 你实验的时候做什么 |
|------|--------|--------------------|
| **Token** | 模型处理的最小单元，不是"字" | 看 `usage.prompt_tokens`，和你的输入字数对比 |
| **System Prompt** | 设定 AI 角色和规则，最高优先级 | 对比有无 System Prompt 的输出差异 |
| **Temperature** | 0=死板确定，1=天马行空 | 同一个问题用 0 / 0.7 / 1.0 各跑一遍 |
| **max_tokens** | 限制输出长度，不是输入长度 | 设成 50 看看输出被截断 |
| **消息格式** | `{"role":"system/user/assistant/tool","content":"..."}` | 这是 Agent 的"通信协议"，后面全基于它 |

### 1.2 关键名词扫盲

面试中你必须自信聊这些：

| 名词 | 一句话 | 面试关联 |
|------|--------|----------|
| LLM | 大语言模型 | 基础题 |
| Token | 文本最小单元，≠字 | 成本计算必问 |
| Embedding | 文本→向量 | RAG 核心 |
| Context Window | 一次最大 Token（GPT-4 128K） | 上下文管理核心 |
| Hallucination | 模型编造信息 | 缓解方案必问 |
| RAG | 先检索再生成 | 核心架构 |
| Fine-tuning | 继续训练模型 | vs RAG 高频题 |
| LoRA/QLoRA | 高效微调方法 | 模型调优必问 |

---

## 第二阶段：Prompt Engineering（Day 4-5）

### 2.1 这不是"写提示词"——这是 Context Engineering

> 文章中说的"正经工程上叫 Context Engineering，Agent 开发里数一数二的手艺活"，指的就是这个。

```python
# ===== 技术1: Few-shot — 给示例让模型对齐格式 =====

few_shot_prompt = """
将公交信息转为JSON。示例：

输入: 线路100路，早高峰7:00-9:00发车间隔5分钟，平峰发车间隔10分钟
输出: {"route":"100","peak":{"start":"07:00","end":"09:00","interval":5},"offpeak":{"interval":10}}

输入: 线路55路，首班6:00，末班22:00
输出: {"route":"55","first":"06:00","last":"22:00"}

现在请转换: 线路28路，早高峰7:30-9:30间隔6分钟，平峰12分钟
"""


# ===== 技术2: Chain-of-Thought — 让模型一步步思考 =====

cot_prompt = """
请分析以下客流数据，先给出计算步骤，再给出结论。

100路周一至周五客流: 850, 920, 880, 780, 950
请计算: 日均客流是多少？高峰日出在哪天？波动幅度多大？

请逐步分析。
"""


# ===== 技术3: 结构化输出控制 =====

structured_prompt = """
分析100路运营状况，严格按以下JSON格式输出（不要输出其他内容）:
{
  "daily_avg": 数字,
  "peak_day": "周几",
  "recommendation": "建议",
  "confidence": "高/中/低"
}

数据: 本周客流 850,920,880,780,950
"""
```

#### 📝 10 个 Prompt 改到对为止

> 文章说"自己动手改十个 Prompt，一条一条对效果。够了。"

| # | 改什么 | 观察什么 |
|---|--------|----------|
| 1 | 不加 vs 加 System Prompt | 输出风格变化 |
| 2 | Temperature 0 vs 0.7 vs 1.0 | 创造性和确定性取舍 |
| 3 | Few-shot 0个 vs 1个 vs 3个示例 | 格式对齐度 |
| 4 | 直接问 vs CoT（要求逐步思考） | 推理准确率 |
| 5 | max_tokens 50 vs 200 vs 无限制 | 截断影响 |
| 6 | Prompt 中英文混杂 vs 纯中文 | 理解准确度 |
| 7 | 角色设定："你是专家" vs 无角色 | 答案深度 |
| 8 | 输出格式：自然语言 vs JSON 约束 | 结构化成功率 |
| 9 | 给背景知识 vs 不给 | 幻觉程度 |
| 10 | 长 Prompt vs 精简短 Prompt | Token 性价比 |

---

## 第三阶段：Python 速成（Day 5-6）

> Java 对比视角。你不需要学 Python 语法大全——只学 Agent 开发必须的三样：**async/await（并发调 LLM）、Pydantic（数据建模）、FastAPI（暴露接口）**。

### 3.1 语法速查 — Java vs Python

```python
# ===== 变量（无类型声明，运行时确定） =====
name: str = "Alice"         # Java: String name = "Alice";
age = 30                    # Java: int age = 30;

# ===== 列表推导（替代 Stream map/filter） =====
nums = [1, 2, 3, 4, 5]
evens = [x for x in nums if x % 2 == 0]  # [2, 4]
doubled = [x * 2 for x in nums]          # [2, 4, 6, 8, 10]
# Java: nums.stream().filter(x -> x%2==0).collect(...)

# ===== 字典（替代 Map） =====
d = {"route": "100路", "stops": 8}
d["price"] = 2.0           # 直接赋值，不需要 map.put()
val = d.get("driver", "未分配")  # 带默认值的 get

# ===== 函数（def 定义，无返回类型） =====
def search_route(origin: str, dest: str) -> dict:
    """查询路线 — 类型提示是可选的，但建议写"""
    return {"route": "100路", "duration": 35}

# ===== 解包（unpacking） =====
a, b = [1, 2]              # a=1, b=2
merged = {**d, "new": 3}  # 合并字典
```

### 3.2 async/await — Agent 开发最核心的 Python 技能

Agent 必须并发：同时调 LLM + 查数据库 + 调 API，不能串行等。

```python
import asyncio

# ===== 基础: async def + await =====
async def call_llm(prompt: str) -> str:
    """异步调 LLM（不阻塞其他任务）"""
    await asyncio.sleep(0.5)  # 模拟网络IO，实际用 httpx.AsyncClient
    return f"Response: {prompt}"

async def query_db(sql: str) -> list:
    """异步查数据库"""
    await asyncio.sleep(0.2)
    return [{"route": "100路", "passengers": 850}]

# ===== 并发执行 — Java 的 CompletableFuture.allOf =====
async def agent_plan(user_input: str):
    """三件事并发做，不等串行"""
    results = await asyncio.gather(
        call_llm(f"分析意图: {user_input}"),
        query_db(f"SELECT * FROM routes WHERE name LIKE '%{user_input}%'"),
        call_llm(f"提取关键信息: {user_input}"),
    )
    return results  # 三个结果同时返回

# 运行: asyncio.run(agent_plan("查100路"))


# ===== 流式输出 — Agent 的常见需求 =====
async def stream_tokens(prompt: str):
    """模拟 LLM 逐个 token 返回"""
    for word in ["杭州", "公交", "100路", "到站", "5分钟"]:
        yield word
        await asyncio.sleep(0.1)

async def main():
    async for token in stream_tokens("查100路"):
        print(token, end="", flush=True)  # 逐词输出，不换行

# asyncio.run(main())


# ===== 超时控制 =====
async def call_with_timeout():
    try:
        result = await asyncio.wait_for(
            call_llm("复杂问题"),
            timeout=5.0  # 5秒超时
        )
        return result
    except asyncio.TimeoutError:
        return "请求超时，请重试"
```

### 3.3 Pydantic — 数据建模（替代 Lombok @Data + @Validated）

```python
from pydantic import BaseModel, Field, validator
from typing import Optional, List, Literal
from datetime import datetime

class CharterTask(BaseModel):
    """包车任务 — 对应你的 CharterTaskVO"""
    task_no: str = Field(..., description="任务编号")
    customer_name: str = Field(..., min_length=1, max_length=50)
    passenger_num: int = Field(ge=1, le=100)
    travel_type: Literal["单程", "往返", "包天"]

    # 起终点
    start_point: str
    end_point: str
    stopover_points: List[str] = Field(default_factory=list, max_length=5)

    # 费用
    estimated_amount: Optional[float] = None

    @validator("start_point", "end_point")
    def not_empty(cls, v):
        if not v or not v.strip():
            raise ValueError("起终点不能为空")
        return v.strip()

# 使用 — 自动校验 + 序列化
task = CharterTask(
    task_no="CT20240115001",
    customer_name="阿里巴巴",
    passenger_num=30,
    travel_type="往返",
    start_point="西溪园区",
    end_point="千岛湖",
)
print(task.model_dump_json(indent=2))  # 序列化
```

### 3.4 FastAPI — 暴露 HTTP 接口（替代 @RestController）

```python
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(title="Agent API")

class QueryRequest(BaseModel):
    origin: str
    destination: str

@app.post("/api/route/search")     # ← 替代 @PostMapping
async def search(request: QueryRequest):
    """路线查询 — async def 才能用 await"""
    # 这里调你的 Agent
    return {"routes": [{"no": "100路", "duration": 35}]}

@app.get("/api/health")
async def health():
    return {"status": "ok"}

# 启动: uvicorn main:app --port 8000
```

**启动命令**（每次别忘了激活虚拟环境）：
```bash
source venv/Scripts/activate   # Windows git-bash
uvicorn main:app --reload --port 8000
```

### 3.5 够用标准

完成 Day 5-6 后，检查自己：
- [ ] 能用 `async def` + `await` + `asyncio.gather` 写并发调用吗？
- [ ] 能用 Pydantic 定义一个 CharterTask 模型并校验吗？
- [ ] 能用 FastAPI 写一个带 POST 和 GET 的接口吗？
- [ ] 不用查文档，能写出 `[x for x in list if cond]` 吗？

> **够了。** 你不会用 Python 写复杂的业务逻辑（那是 Java 的活）。Python 在这里只做三件事：**调 LLM、定义数据结构、暴露 HTTP 接口**。

---

## 第四阶段：手写第一个 Agent（Day 7）

### ⚠️ 别上框架，用原生 API 写

> 文章："用原生 API 自己撸一个带工具的 Agent 出来。把那个 Loop 从头到尾亲自跑一遍，你才算真正懂了。"

```python
"""
手写 ReAct Agent — 零框架依赖

Agent = LLM + 工具 + 循环
工具描述(Schema) → LLM 决策 → 解析 JSON → 执行工具 → 结果反馈 → 循环
"""

import httpx, json, re

API_KEY = "sk-xxx"
BASE_URL = "https://api.deepseek.com/v1"

# ===== 1. 定义工具（注意 Schema 怎么写的，这是 Agent 的核心） =====

def search_route(origin: str, destination: str) -> str:
    """查询公交路线"""
    return f"{origin}→{destination}: 100路直达, 35分钟"

TOOLS = [
    {
        "name": "search_route",
        "description": "查询两个地点之间的公交路线",
        "parameters": {
            "origin": "string, 出发地",
            "destination": "string, 目的地"
        }
    }
]

TOOLS_DESC = "\n".join([
    f"- {t['name']}: {t['description']}。参数: {json.dumps(t['parameters'], ensure_ascii=False)}"
    for t in TOOLS
])

# ===== 2. System Prompt（包含了工具 Schema + 输出格式要求） =====

SYSTEM_PROMPT = f"""你是公交出行助手。

## 可用工具
{TOOLS_DESC}

## 回复格式
需要调用工具时:
Thought: [你的分析]
Action: [工具名]
Args: {{"参数": "值"}}

可以直接回答时:
Thought: [分析]
Answer: [回答]
"""

# ===== 3. 原生 LLM 调用 =====

def call_llm(messages: list[dict]) -> dict:
    resp = httpx.post(
        f"{BASE_URL}/chat/completions",
        headers={"Authorization": f"Bearer {API_KEY}"},
        json={"model": "deepseek-chat", "messages": messages, "temperature": 0.3},
        timeout=30
    )
    return resp.json()

# ===== 4. Agent 主循环 =====

def run_agent(user_input: str, max_turns: int = 5) -> str:
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_input}
    ]

    for turn in range(max_turns):
        print(f"\n=== Turn {turn+1} ===")
        
        # 1. LLM 决策
        resp = call_llm(messages)
        llm_text = resp["choices"][0]["message"]["content"]
        print(f"LLM: {llm_text[:200]}")
        
        # 2. 解析 Action
        action_match = re.search(r"Action:\s*(.+)", llm_text)
        args_match = re.search(r"Args:\s*(\{.+?\})", llm_text, re.DOTALL)
        
        if not action_match:
            # 没有 Action，返回 Answer
            answer = re.search(r"Answer:\s*(.+)", llm_text, re.DOTALL)
            return answer.group(1).strip() if answer else llm_text

        # 3. 执行工具
        tool_name = action_match.group(1).strip()
        tool_args = json.loads(args_match.group(1)) if args_match else {}
        
        print(f"执行: {tool_name}({tool_args})")
        result = TOOL_EXECUTORS[tool_name](**tool_args)
        print(f"结果: {result}")
        
        # 4. 反馈结果
        messages.append({"role": "assistant", "content": llm_text})
        messages.append({"role": "user", "content": f"工具返回: {result}"})

    return "达到最大轮次"

TOOL_EXECUTORS = {"search_route": search_route}

# 测试
if __name__ == "__main__":
    print(run_agent("从西湖到火车东站怎么走？"))
```

---

## 🎯 第一阶段检查点

完成 Day 1-7 后，你应该能回答：

- [ ] System Prompt 和 User Message 有什么区别？
- [ ] Temperature 0 vs 1.0 对输出有什么影响？
- [ ] 一次 API 调用，Token 怎么算、花多少钱？
- [ ] Few-shot 和 CoT 分别解决什么问题？
- [ ] 不用任何框架，能写出一个带工具调用的 Agent 循环吗？
- [ ] 工具的描述（Schema）如果写错了，Agent 会怎样？
- [ ] 消息格式里 role 有哪几种？tool call 的消息怎么传？
