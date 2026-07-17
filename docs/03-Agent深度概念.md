# 从Java架构师到AI Agent开发工程师 — 1个月高强度学习计划 v2.0

> **目标画像**：35岁Java架构师，公共交通领域背景（长保班车+散包旅游），擅长数据分析
> **目标**：杭州 30-40K AI Agent 岗位
> **学习周期**：4周，每天6-8小时
>
> **v2.0 更新**：
> - 新增 Java 多线程/高并发/事务 经典题目章节
> - 新增 Plan-and-Execute、上下文工程、模型调优 深度内容
> - LangChain 框架深度实战（LCEL/LangGraph）+ Dify 全维度对比
> - 终极项目改为公交出行平台 AI 融合架构（车辆调度 + 报价规则）
> - 📄 附独立文档：`LangChain从零到调通后端接口-实战手册.md`（Windows本机部署全流程）

---

## 📋 目录

- [第1周：AI Agent 基础理论与 Python 速成](#第1周ai-agent-基础理论与-python-速成)
- [第2周：Agent 框架与 RAG 实战](#第2周agent-框架与-rag-实战)
- [第3周：Java 核心深化 + Agent 深度概念](#第3周java-核心深化--agent-深度概念)
- [第4周：面试冲刺 + 终极融合项目](#第4周面试冲刺--终极融合项目)
- [附录A：Java 多线程/高并发/事务 经典题目与答案](#附录ajava-多线程高并发事务-经典题目与答案)
- [附录B：Agent 深度概念（Plan-and-Execute/上下文工程/模型调优）](#附录bagent-深度概念plan-and-execute上下文工程模型调优)
- [附录C：高频面试题与答案](#附录c高频面试题与答案)
- [附录D：公交出行平台 AI 融合架构设计](#附录d公交出行平台-ai-融合架构设计)
- [附录E：学习资源汇总](#附录e学习资源汇总)

---


---

## 附录B：Agent 深度概念（Plan-and-Execute/上下文工程/模型调优）

### B1：Plan-and-Execute vs ReAct — 何时用哪个？

```
决策树：

你的任务是否有明确的步骤结构？
    ├── 是 → 任务步骤是否固定？
    │       ├── 是 → 传统 Chain/Pipeline 即可（不需要 Agent）
    │       └── 否 → Plan-and-Execute（先规划再执行）
    │               例子：数据分析报表、多步骤调研、代码生成
    │
    └── 否 → 是否需要根据中间结果动态决策？
            ├── 是 → ReAct（每步根据观察调整）
            │       例子：智能客服、故障排查
            └── 否 → 单次 LLM 调用即可

混合模式（生产中最常见）:
┌──────────────────────────────────┐
│  Planner: Plan-and-Execute       │
│  ┌────────────────────────────┐  │
│  │ Step 1 → Step 2 → Step 3  │  │
│  └────────────────────────────┘  │
│           ↓         ↓            │
│  ┌──────────┐  ┌──────────┐     │
│  │ Executor │  │ Executor │     │
│  │ (ReAct)  │  │ (ReAct)  │     │
│  └──────────┘  └──────────┘     │
│  开放式子任务    开放式子任务      │
└──────────────────────────────────┘
```

**面试话术**：
> "我们用分层策略：顶层用 Plan-and-Execute 做任务分解（Planner Agent），每个子任务内部用 ReAct 做工具调用（Executor Agent）。这样既保证了全局目标的可见性，又保留了应对不确定性的灵活性。"

### B2：上下文工程四个层次（详解）

```
Level 1: 朴素上下文
  Prompt = "参考以下资料回答：{全文粘贴}"
  问题：Token 浪费、噪音干扰

Level 2: 结构化上下文  
  Prompt = """
  ## 参考资料（共3篇，按相关性排序）
  
  ### 文档1 [相关性:0.95]
  {内容}
  
  ### 文档2 [相关性:0.82]
  {内容}
  """
  优势：LLM 更容易理解信息的层次

Level 3: 自适应上下文
  - 动态调整 Top-K（简单问题K=2，复杂问题K=10）
  - 根据内容类型选择不同截断策略
  - Self-RAG: 先让 LLM 判断"我需要检索吗？"
  
Level 4: 多源融合上下文
  - SQL 查询结果 + 向量检索结果 + 实时 API 结果
  - Agent 自动选择最优信息源
  - 信息源优先级: 实时API > 数据库 > 文档库
```

### B3：模型调优决策全景

```
                    ┌──────────────────┐
                    │  需要改进模型表现  │
                    └────────┬─────────┘
                             ↓
                    ┌──────────────────┐
                    │  能改 Prompt 吗？  │
                    └────┬─────────┬───┘
                     能  │         │ 不能
                         ↓         ↓
                  ┌──────────┐  ┌──────────────────┐
                  │ Prompt   │  │ 数据频繁变化？     │
                  │Engineering│  └────┬─────────┬───┘
                  │ (首选)    │    是 │         │ 否
                  └──────────┘       ↓         ↓
                              ┌──────────┐  ┌──────────┐
                              │   RAG    │  │ Fine-tuning│
                              │ (检索增强)│  │  (微调)    │
                              └──────────┘  └──────────┘
                                                    ↓
                                            ┌──────────────┐
                                            │ GPU 够吗？    │
                                            └──┬───────┬───┘
                                            够 │       │ 不够
                                               ↓       ↓
                                        ┌──────────┐ ┌──────────┐
                                        │ Full FT  │ │LoRA/QLoRA│
                                        │ 全量微调  │ │ 高效微调  │
                                        └──────────┘ └──────────┘
```

**Fine-tuning vs RAG 对比**：

| 维度 | Fine-tuning | RAG |
|------|------------|-----|
| **知识更新** | 需要重新训练 | 更新文档即可 |
| **幻觉控制** | 可能学会"编造" | 有据可查 |
| **成本** | GPU 训练成本高 | 推理时检索成本 |
| **推理速度** | 快（无额外检索） | 慢（需检索+重排） |
| **适用场景** | 风格/格式学习、领域术语 | 知识密集型、频繁更新 |
| **数据需求** | 需要标注数据 | 需要文档 |

**常用微调方法**：

```
1. Full Fine-tuning — 更新全部参数
   - 需要: 大量 GPU 显存（7B模型约56GB）
   - 效果: 最好，但也最容易过拟合

2. LoRA (Low-Rank Adaptation) 
   - 原理: 冻结原模型参数，只训练低秩矩阵（旁路）
   - 优势: 显存需求降低90%，训练速度提升
   - 参数量: 7B模型只需训练约33M参数

3. QLoRA 
   - = 4-bit 量化 + LoRA
   - 7B模型只需约10GB显存（单块RTX 3080即可）
   - 效果接近 Full Fine-tuning

4. RLHF (Reinforcement Learning from Human Feedback)
   - 过程: SFT → 奖励模型 → PPO强化学习
   - 目的: 对齐人类偏好（不要有毒输出、遵循指令）
   - 代表: ChatGPT 的核心训练方法
```

### B4：Multi-Agent 协作协议深入

**消息格式标准化**：

```json
{
  "message_id": "msg-001",
  "from_agent": "DispatchPlanner",
  "to_agent": "DriverMatcher",
  "type": "task_delegation",
  "payload": {
    "task": "allocate_drivers",
    "params": {
      "route_id": "R001",
      "date": "2024-01-15",
      "vehicle_count": 3
    },
    "deadline": "2024-01-15T08:00:00Z",
    "priority": "high"
  },
  "context": {
    "parent_task": "emergency_dispatch",
    "dependencies": ["VehicleAllocator.completed"]
  }
}
```

**Agent 间通信模式对比**：

| 模式 | 机制 | 优点 | 缺点 | 适用 |
|------|------|------|------|------|
| **直接调用** | Agent A 调 Agent B 的函数 | 简单直接 | 紧耦合 | 固定流程 |
| **消息队列** | 发布/订阅 | 解耦、可扩展 | 增加延迟 | 异步协作 |
| **共享状态** | 读写同一 State 对象 | 数据一致 | 竞争条件 | LangGraph |
| **中央调度** | Orchestrator 统一分发 | 可控 | 单点瓶颈 | 层级结构 |

### B5：LLM 应用经验 — 面试要能聊的"实战感悟"

**1. Token 成本控制实战**：

```
策略                      节省比例    实现方式
─────────────────────────────────────────────
缓存相同问题              30-50%     Redis + 语义相似度匹配
小模型预筛选              20-30%     小模型判断意图，大模型执行
提示压缩                  15-25%     去除冗余信息
模型降级                  40-60%     简单任务用 gpt-3.5，复杂用 gpt-4
输出长度限制              10-20%     max_tokens 限制
```

**2. Agent 循环检测**：

```python
# 实际遇到的 Loop 陷阱及解决方案

# 陷阱1: 工具调用死循环
# 表现: Agent 反复调用同一工具，参数不变
# 解决:
class LoopDetector:
    def __init__(self, max_same_calls=3):
        self.call_history = []
        self.max_same_calls = max_same_calls
    
    def check(self, tool_name: str, args: dict) -> bool:
        key = f"{tool_name}:{json.dumps(args, sort_keys=True)}"
        self.call_history.append(key)
        # 检查最近 max_same_calls 次是否都是同一个调用
        recent = self.call_history[-self.max_same_calls:]
        if len(recent) == self.max_same_calls and len(set(recent)) == 1:
            return False  # 循环检测
        return True

# 陷阱2: 工具返回为空时 Agent 反复重试
# 解决: 工具返回空时直接返回"未找到相关信息"，不让 Agent 猜测

# 陷阱3: 上下文无限增长
# 解决: 滑动窗口 + 定期摘要压缩
```

**3. 流式输出的工程处理**：

```python
# SSE (Server-Sent Events) 流式输出 — 类比 WebSocket 但单向

async def stream_agent_response(agent, user_input: str):
    """流式 Agent 响应"""
    async for event in agent.astream_events(
        {"input": user_input},
        version="v1",
    ):
        kind = event["event"]
        
        if kind == "on_chat_model_stream":
            # LLM 输出的 token
            content = event["data"]["chunk"].content
            if content:
                yield f"data: {json.dumps({'type': 'token', 'content': content})}\n\n"
        
        elif kind == "on_tool_start":
            # 工具调用开始
            yield f"data: {json.dumps({'type': 'tool_start', 'tool': event['name']})}\n\n"
        
        elif kind == "on_tool_end":
            # 工具调用结束
            yield f"data: {json.dumps({'type': 'tool_end', 'output': str(event['data']['output'])[:200]})}\n\n"
    
    yield "data: [DONE]\n\n"
```

---

