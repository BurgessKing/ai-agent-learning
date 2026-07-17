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

## 第1周：AI Agent 基础理论与 Python 速成

### Day 1-2：LLM 核心概念 + 关键名词扫盲

#### 1.1 必须掌握的名词表

面试中你需要**自信地聊这些概念**，不能只是"听说过"：

| 名词 | 一句话解释 | 面试场景 |
|------|-----------|----------|
| **LLM** | 大语言模型，基于 Transformer 的生成式模型 | 基础题，必须流畅 |
| **Token** | 模型处理的最小文本单元，不等于"字"或"词" | 必问题 |
| **Embedding** | 文本→高维向量，语义相近的向量距离近 | RAG 核心 |
| **Context Window** | 模型一次能处理的最大 Token 数（如 GPT-4 128K） | 上下文工程核心 |
| **Temperature** | 控制输出随机性，0=确定，1=随机 | 调参经验 |
| **Top-P / Top-K** | 采样策略，控制输出多样性 | 调参经验 |
| **Hallucination（幻觉）** | 模型编造不存在的信息 | 必问题，怎么缓解 |
| **Prompt Engineering** | 通过设计输入文本引导模型行为 | 基础技能 |
| **Few-shot / Zero-shot** | 给/不给示例的提示方式 | 基础题 |
| **Chain-of-Thought (CoT)** | 让模型"一步步思考"，显著提升推理能力 | 核心技术 |
| **RAG** | 检索增强生成 — 先查资料再回答，解决幻觉 | 核心技术 |
| **Fine-tuning** | 在特定数据上继续训练模型 | 与 RAG 的区别是高频题 |
| **LoRA / QLoRA** | 低秩适配，高效的微调方法 | 模型调优必问 |
| **Quantization** | 模型量化（INT8/INT4），降低显存占用 | 部署相关 |
| **RLHF** | 基于人类反馈的强化学习，对齐人类偏好 | 概念了解 |
| **Vector Database** | 存储和检索向量的数据库 | RAG 基础设施 |
| **MCP (Model Context Protocol)** | Anthropic 提出的 Agent-工具标准协议 | 2024-2025 热点 |

#### 1.2 Transformer 精要（与 v1.0 相同，略）

核心公式和 Q/K/V 理解保留，此处不再重复。参见初版文档 Day 1-2。

---

### Day 3-4：AI Agent 架构 + ReAct + Plan-and-Execute

#### 2.1 Agent 定义（保留 v1.0 内容）

> **AI Agent = LLM + Planning + Memory + Tool Use**

#### 2.2 ReAct 模式（保留，略）

#### 2.3 Plan-and-Execute 模式 ⭐ 新增

这是面试中区分"用过 Agent"和"深入理解 Agent"的分水岭。

**ReAct 的问题**：每一步思考只往前看一步，容易在复杂任务中"迷路"。

**Plan-and-Execute 的解法**：先规划全局再分步执行。

```
┌──────────────────────────────────────────────────────┐
│           Plan-and-Execute 模式                       │
│                                                       │
│  用户: "帮我分析100路客流，优化排班，发邮件给张经理"   │
│                                                       │
│  Step 1: Plan (规划)                                  │
│  ┌──────────────────────────────────────────────┐    │
│  │ Planner Agent (LLM)                           │    │
│  │                                               │    │
│  │ 任务分解:                                     │    │
│  │ 1. 查询100路最近30天客流数据                  │    │
│  │ 2. 分析高峰/平峰时段                          │    │
│  │ 3. 对比现有排班表                              │    │
│  │ 4. 生成优化方案                                │    │
│  │ 5. 发送邮件给张经理                            │    │
│  └──────────────────────────────────────────────┘    │
│                          ↓                            │
│  Step 2: Execute (逐步执行)                           │
│  ┌──────────────────────────────────────────────┐    │
│  │ Executor Agent (ReAct循环)                    │    │
│  │                                               │    │
│  │ Task 1 → [search_db] → ✅                     │    │
│  │ Task 2 → [analyze_data] → ✅                  │    │
│  │ Task 3 → [compare_schedule] → ✅              │    │
│  │ Task 4 → [generate_plan] → ✅                 │    │
│  │ Task 5 → [send_email] → ✅                    │    │
│  └──────────────────────────────────────────────┘    │
│                          ↓                            │
│  Step 3: Replan (按需重规划)                          │
│  如果某步失败 → 调整计划 → 继续                        │
└──────────────────────────────────────────────────────┘
```

**对比表格（面试必须能讲清楚）**：

| 维度 | ReAct | Plan-and-Execute |
|------|-------|-------------------|
| **决策粒度** | 每步决策 | 全局规划 + 分步执行 |
| **长任务表现** | 容易丢失目标 | 始终保持全局视角 |
| **Token 消耗** | 较高（每步都思考） | 规划阶段消耗大，执行阶段节约 |
| **灵活性** | 高（动态调整） | 中等（按计划执行） |
| **适用场景** | 开放式探索任务 | 结构化多步骤任务 |
| **失败恢复** | 自然回溯 | 需要显式 Replan |

**面试话术**：
> "在实际项目中，我通常采用 Plan-and-Execute 处理结构化任务（如数据分析报表），用 ReAct 处理开放式问答。两者可以组合——用 Planner 生成计划，每个子任务内部用 ReAct 执行。"

```python
"""
Plan-and-Execute Agent 核心实现
"""

import json
from typing import List

class PlanStep:
    def __init__(self, step_id: int, description: str, tool: str, args: dict):
        self.step_id = step_id
        self.description = description
        self.tool = tool
        self.args = args
        self.status = "pending"  # pending / running / completed / failed
        self.result = None

class PlanAndExecuteAgent:
    """Plan-and-Execute Agent"""
    
    def __init__(self, llm_call, tools: dict):
        self.llm_call = llm_call
        self.tools = tools
    
    async def run(self, user_input: str) -> str:
        # 1. 规划阶段
        plan = await self._plan(user_input)
        print(f"📋 计划: {[s.description for s in plan]}")
        
        # 2. 执行阶段
        for step in plan:
            print(f"▶️ 执行 Step {step.step_id}: {step.description}")
            step.status = "running"
            
            try:
                step.result = await self._execute_step(step)
                step.status = "completed"
                print(f"   ✅ 完成: {str(step.result)[:100]}")
            except Exception as e:
                step.status = "failed"
                print(f"   ❌ 失败: {e}")
                
                # 3. 重规划（Replan）
                plan = await self._replan(plan, step, str(e))
        
        # 4. 汇总
        return await self._summarize(user_input, plan)
    
    async def _plan(self, user_input: str) -> List[PlanStep]:
        """调用 LLM 生成执行计划"""
        prompt = f"""将以下任务分解为可执行的步骤（每步调用一个工具）。
可用工具: {json.dumps(list(self.tools.keys()))}

任务: {user_input}

返回 JSON 数组:
[{{"step_id": 1, "description": "...", "tool": "工具名", "args": {{...}}}}]"""
        
        response = await self.llm_call([{"role": "user", "content": prompt}])
        steps_data = json.loads(response)
        return [PlanStep(**s) for s in steps_data]
    
    async def _execute_step(self, step: PlanStep) -> dict:
        """执行单个步骤（内部可用 ReAct 循环）"""
        tool_func = self.tools[step.tool]
        return await tool_func(**step.args)
    
    async def _replan(self, plan: List[PlanStep], failed_step: PlanStep, error: str) -> List[PlanStep]:
        """某步失败后重新规划剩余步骤"""
        remaining = [s for s in plan if s.status == "pending"]
        prompt = f"""步骤 {failed_step.step_id} "{failed_step.description}" 失败，原因: {error}
剩余任务: {[s.description for s in remaining]}
请调整计划:"""
        # ... 类似 _plan 的逻辑
        return remaining
    
    async def _summarize(self, goal: str, plan: List[PlanStep]) -> str:
        """汇总所有步骤结果"""
        results = "\n".join([
            f"Step {s.step_id} ({s.status}): {s.result}"
            for s in plan
        ])
        response = await self.llm_call([{
            "role": "user",
            "content": f"目标: {goal}\n\n执行结果:\n{results}\n\n请汇总回答。"
        }])
        return response
```

---

### Day 5-6：Python 速成（保留 v1.0 内容，略）

### Day 7：综合项目 — 首个 Agent（保留，略）

---

