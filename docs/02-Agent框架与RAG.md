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

## 第2周：Agent 框架与 RAG 实战

### Day 8-9：LangChain 核心（保留，略）

### Day 10-11：RAG 深入 + 上下文工程 ⭐

#### RAG 核心流程（保留 v1.0）

#### 上下文工程（Context Engineering）⭐ 新增

> **面试关键概念**：RAG 不只是"检索+生成"，上下文工程的优劣直接决定 Agent 质量。

```
上下文工程的四个层次：

┌─────────────────────────────────────────────────┐
│  Level 1: 原始上下文（Naive）                     │
│  Prompt = 用户问题 + 检索到的全部文档              │
│  问题：噪音多、Token 浪费                          │
├─────────────────────────────────────────────────┤
│  Level 2: 结构化上下文                            │
│  Prompt = 用户问题 + 去重排序后的文档              │
│  技巧：Reranker 重排序、去重、截断                  │
├─────────────────────────────────────────────────┤
│  Level 3: 动态上下文窗口                          │
│  根据任务复杂度动态调整 Top-K                      │
│  问题简单 → K=2，问题复杂 → K=10                   │
│  技巧：Self-RAG（先判断需不需要检索）              │
├─────────────────────────────────────────────────┤
│  Level 4: 多源上下文融合                          │
│  结构化数据(SQL) + 非结构化文档(RAG) + 实时API    │
│  Agent 自动选择最优信息源                          │
└─────────────────────────────────────────────────┘
```

**上下文工程核心技巧**：

```python
"""
上下文工程工具箱
"""

class ContextEngineer:
    """上下文工程核心 — 决定了 RAG 质量的上限"""
    
    def __init__(self):
        self.max_context_tokens = 3000  # 留给上下文的预算
    
    def build_context(
        self,
        query: str,
        retrieved_docs: list,
        history: list = None,
        data_sources: list = None,
    ) -> str:
        """
        构建最优上下文
        
        核心原则:
        1. 相关性 > 数量
        2. 结构化 > 堆砌
        3. 去噪 > 贪多
        """
        # Step 1: Rerank（重排序）
        docs = self._rerank(query, retrieved_docs)
        
        # Step 2: Dedup（去重）
        docs = self._deduplicate(docs)
        
        # Step 3: Truncate（截断，控制总 Token）
        docs = self._truncate_to_budget(docs, self.max_context_tokens)
        
        # Step 4: Structure（结构化组装）
        context_parts = []
        
        # 4a. 检索文档
        if docs:
            context_parts.append("## 📚 参考资料\n")
            for i, doc in enumerate(docs, 1):
                context_parts.append(
                    f"**文档{i}** [来源: {doc['source']}, "
                    f"相关性: {doc['score']:.2f}]\n{doc['content']}\n"
                )
        
        # 4b. SQL 查询结果
        if data_sources:
            context_parts.append("## 📊 数据查询结果\n")
            for ds in data_sources:
                context_parts.append(f"```json\n{json.dumps(ds, ensure_ascii=False, indent=2)}\n```\n")
        
        # 4c. 对话历史摘要
        if history:
            context_parts.append("## 💬 历史对话摘要\n")
            context_parts.append(self._summarize_history(history))
        
        return "\n---\n".join(context_parts)
    
    def _rerank(self, query: str, docs: list) -> list:
        """
        重排序策略:
        - 简单版: 基于相似度分数排序
        - 进阶版: 使用 Cross-Encoder Reranker (如 BGE-Reranker)
        - 高级版: LLM-as-Reranker（让 LLM 打分排序）
        """
        # 去重标题相似的内容
        seen_titles = set()
        reranked = []
        for doc in sorted(docs, key=lambda d: d['score'], reverse=True):
            title = doc.get('source', '')
            if title not in seen_titles:
                seen_titles.add(title)
                reranked.append(doc)
        return reranked
    
    def _deduplicate(self, docs: list) -> list:
        """基于内容相似度去重"""
        result = []
        for doc in docs:
            is_dup = False
            for existing in result:
                # 简单版：Jaccard 相似度
                if self._jaccard(doc['content'], existing['content']) > 0.7:
                    is_dup = True
                    break
            if not is_dup:
                result.append(doc)
        return result
    
    def _truncate_to_budget(self, docs: list, max_tokens: int) -> list:
        """按 Token 预算截断 — 确保不超出 Context Window"""
        current = 0
        result = []
        for doc in docs:
            estimated_tokens = len(doc['content']) // 2  # 中文约 2chars/token
            if current + estimated_tokens > max_tokens:
                # 截断最后一个文档
                available = max_tokens - current
                doc['content'] = doc['content'][:available * 2] + "..."
                result.append(doc)
                break
            result.append(doc)
            current += estimated_tokens
        return result
    
    def _jaccard(self, a: str, b: str) -> float:
        set_a = set(a)
        set_b = set(b)
        return len(set_a & set_b) / len(set_a | set_b) if set_a | set_b else 0
    
    def _summarize_history(self, history: list) -> str:
        """压缩历史对话"""
        # 实际使用 LLM 做摘要压缩
        return "\n".join([
            f"- {msg['role']}: {msg['content'][:100]}"
            for msg in history[-5:]  # 只保留最近5条
        ])
```

---

### Day 12-13：LangChain 框架深度实战 + Dify 全维度对比 ⭐

> 📄 **配套实战文档**：`LangChain从零到调通后端接口-实战手册.md` — Windows 本机 Hermes 部署全流程，从 `pip install` 到 Agent 调通 Spring Boot 后端接口。

#### 12.1 LangChain 核心概念体系

LangChain 是目前生态最完善的 Agent 开发框架。你的 Java 架构背景可以帮助快速理解其设计。

```
LangChain 六大核心模块（类比 Spring 生态）:

┌──────────────────────────────────────────────────────────┐
│                   LangChain 架构                          │
│                                                          │
│  ┌─────────────┐  ┌─────────────┐  ┌───────────────┐   │
│  │   Models    │  │   Prompts   │  │    Chains     │   │
│  │  LLM/Chat   │  │  Templates  │  │   链式组合     │   │
│  │ (类比JDBC)  │  │ (类比JSP)   │  │ (类比Filter)  │   │
│  └─────────────┘  └─────────────┘  └───────────────┘   │
│                                                          │
│  ┌─────────────┐  ┌─────────────┐  ┌───────────────┐   │
│  │   Agents    │  │   Memory    │  │  Retrieval    │   │
│  │  智能体     │  │  对话记忆   │  │  RAG 检索     │   │
│  │ (类比策略)  │  │ (类比Session)│  │ (类比ES搜索)  │   │
│  └─────────────┘  └─────────────┘  └───────────────┘   │
└──────────────────────────────────────────────────────────┘

Java 架构师理解法：
  Model   = 数据源抽象 (类似 DataSource)
  Chain   = 责任链模式 (类似 Filter Chain)
  Agent   = 策略模式 + 状态机 (类似 Spring State Machine)
  Memory  = 会话管理 (类似 HTTP Session + Redis)
  Tool    = SPI 插件机制 (类似 ServiceLoader)
```

#### 12.2 LCEL — LangChain Expression Language（现代写法）

> LCEL 是 LangChain 的"流式 API"，用 `|` 管道符串联组件，类比 Java 8 的 Stream API 或 Reactor 的链式调用。

```python
"""
LCEL 核心语法: component1 | component2 | component3

这个管道符号 `|` 背后是 Runnable 接口 — 类似 Java 的 Function<T,R>
LangChain 中几乎所有组件都实现了 Runnable 接口
"""

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough, RunnableLambda

# ===== 最简 LCEL Chain =====
# 对比传统写法：prompt → llm → output_parser

prompt = ChatPromptTemplate.from_template("用{language}解释：{concept}")
llm = ChatOpenAI(model="gpt-4", temperature=0)

# LCEL 管道串联
chain = prompt | llm | StrOutputParser()

# 调用
result = chain.invoke({"language": "Java", "concept": "RAG"})
print(result)

# ===== 复杂 Chain: RAG 问答（LCEL 版本）=====

# 1. 定义各个组件
retriever = vector_store.as_retriever(search_kwargs={"k": 3})

rag_prompt = ChatPromptTemplate.from_messages([
    ("system", """基于以下参考资料回答问题。如果不确定，请说不知道。

参考资料：
{context}"""),
    ("human", "{question}")
])

# 2. LCEL 串联整个 RAG Pipeline
def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)

rag_chain = (
    {
        "context": retriever | format_docs,          # 检索 + 格式化
        "question": RunnablePassthrough()            # 原样传递用户问题
    }
    | rag_prompt                                      # 构建 Prompt
    | llm                                             # LLM 生成
    | StrOutputParser()                               # 解析输出
)

# 3. 一行调用
answer = rag_chain.invoke("100路末班车几点？")

# ===== 流式输出（LCEL 原生支持）=====
async for chunk in rag_chain.astream("杭州公交票价多少？"):
    print(chunk, end="", flush=True)

# ===== 带 Function Calling 的 Agent Chain =====
from langchain.tools import tool

@tool
def search_bus_route(origin: str, destination: str) -> str:
    """查询公交路线"""
    return f"{origin}到{destination}: 100路直达, 约35分钟"

@tool
def query_realtime(route_no: str, stop_name: str) -> str:
    """查询实时到站"""
    return f"{route_no}在{stop_name}站还有5分钟到站"

tools = [search_bus_route, query_realtime]

# 绑定工具到 LLM
llm_with_tools = llm.bind_tools(tools)

# Agent 提示词
agent_prompt = ChatPromptTemplate.from_messages([
    ("system", "你是公交出行助手。使用工具帮助用户。"),
    ("human", "{input}"),
    ("placeholder", "{agent_scratchpad}")  # 工具调用历史占位
])

agent_chain = agent_prompt | llm_with_tools
```

#### 12.3 LangChain 核心接口深度 — Runnable 体系

```
Runnable 接口体系（面试能画这张图很加分）:

                    ┌──────────────┐
                    │   Runnable   │  ← 基础接口
                    │──────────────│
                    │ invoke()     │  同步调用
                    │ ainvoke()    │  异步调用
                    │ stream()     │  同步流式
                    │ astream()    │  异步流式
                    │ batch()      │  批量
                    │ abatch()     │  异步批量
                    └──────┬───────┘
                           │
          ┌────────────────┼────────────────┐
          ↓                ↓                ↓
   ┌──────────────┐ ┌──────────────┐ ┌──────────────┐
   │RunnableLambda│ │RunnableBranch│ │RunnablePassthrough│
   │ 自定义函数    │ │ 条件分支      │ │ 透传          │
   └──────────────┘ └──────────────┘ └──────────────┘

链式组合:
  chain = a | b | c  # a的输出 → b的输入 → c的输入
  
并行组合:
  chain = {
      "summary": a,
      "details": b,
  } | c  # a和b并行执行，结果合并后给c
```

**面试话术**：
> "LCEL 的 `|` 管道背后是 Runnable 接口，类似 Java 的 `Function<T,R>`.andThen()。这种统一接口设计让组件可以任意组合——你可以把 PromptTemplate、LLM、Retriever、自定义函数任意串联，而不用关心它们的内部实现。这本质上是一种函数式编程的 Monad 模式。"

#### 12.4 LangGraph — 有状态的 Agent 编排

LangGraph 是 LangChain 生态的"状态机引擎"，用于构建复杂的多步骤 Agent。

```
LangGraph 三要素:

1. State（状态）— 类似 Redux Store
   class AgentState(TypedDict):
       messages: Annotated[list, operator.add]  # 消息追加
       next_step: str                           # 下一步路由

2. Node（节点）— 每个节点是 Runnable
   def agent_node(state): ...       # LLM 决策节点
   def tool_node(state): ...        # 工具执行节点
   def response_node(state): ...    # 最终回复节点

3. Edge（边）— 控制流
   - 普通边: START → agent → tools → agent → ... → END
   - 条件边: agent → {tools / response} (按 next_step 路由)
```

**LangGraph vs 传统 Chain**：

```
传统 Chain (LCEL):
  A → B → C → D  (固定流程，一次性跑完)

LangGraph:
       ┌─────┐
       │START│
       └──┬──┘
          ↓
       ┌─────┐
    ┌─→│Agent│←─┐      ← 循环！每次经过 Agent 都可能
    │  └──┬──┘  │        选择不同的下一步
    │     ↓     │
    │  ┌────┐ ┌─┴──┐
    │  │Tool│ │Resp│   ← 条件路由
    │  │ A  │ │ond │
    │  └──┬─┘ └──┬─┘
    │     │      ↓
    └─────┘    ┌───┐
              │END│
              └───┘
```

**完整 LangGraph Agent 代码**（对比 Day 3-4 手写 ReAct，看框架的简洁）：

```python
"""
LangGraph ReAct Agent — 不到30行代码替代手写的200行
"""
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode
from typing import TypedDict, Annotated
import operator

# 1. 定义 State
class AgentState(TypedDict):
    messages: Annotated[list, operator.add]

# 2. 创建 Graph
graph = StateGraph(AgentState)

# 3. 添加节点
graph.add_node("agent", lambda state: {
    "messages": [llm_with_tools.invoke(state["messages"])]
})
graph.add_node("tools", ToolNode(tools))  # 内置工具执行节点

# 4. 添加边
graph.set_entry_point("agent")
graph.add_conditional_edges(
    "agent",
    lambda state: "tools" if state["messages"][-1].tool_calls else END
)
graph.add_edge("tools", "agent")  # 工具结果返回给 Agent

# 5. 编译运行
app = graph.compile()
result = app.invoke({"messages": [("user", "查西湖到火车东站公交")]})
```

#### 12.5 LangChain vs Dify — 全维度对比

| 维度 | LangChain (含 LangGraph) | Dify |
|------|--------------------------|------|
| **定位** | 开发框架，代码即配置 | 低代码平台，可视化编排 |
| **上手门槛** | 中高（需 Python + 框架概念） | 低（拖拽+配置，非开发人员可用） |
| **灵活性** | ⭐⭐⭐⭐⭐ 完全控制每个细节 | ⭐⭐⭐ 受平台能力边界限制 |
| **Agent 能力** | ReAct / Plan-Execute / Multi-Agent 均支持 | 支持 Agent + 工作流，但复杂编排受限 |
| **自定义工具** | 任意 Python 函数 + API | 支持 API 工具 + 代码节点 |
| **记忆管理** | 完全自定义（Redis/PGVector/自定义） | 内置会话变量（能力有限） |
| **RAG 能力** | 自由组合检索策略 + 重排序 | 内置 RAG Pipeline（够用但不灵活） |
| **模型支持** | 任何有 API 的模型 + 本地模型 | 有限供应商列表（OpenAI/Claude/通义等） |
| **Multi-Agent** | LangGraph/CrewAI 原生支持 | 不支持（需拆多个应用） |
| **调试追踪** | LangSmith / LangFuse | 内置调试面板 |
| **CI/CD 集成** | 标准 Git + CI/CD | Docker 部署 + API 导出 |
| **学习曲线** | 2-4周熟练 | 1-3天上手 |
| **团队协作** | Git 协作（工程师） | 平台内协作（产品+工程） |

**选型决策树**：

```
你的场景适合 Dify 还是 LangChain？

1. 只是做个知识库问答？ → Dify（半天上线）
2. 需要复杂的 Multi-Agent 编排？ → LangChain + LangGraph
3. 需要深度集成现有 Java 业务系统？ → LangChain（Python Agent + Java API）
4. 团队有非技术业务人员需要参与？ → Dify 辅助（给业务人员用）
5. 需要自定义记忆策略/检索策略？ → LangChain
6. 快速验证一个想法？ → Dify（PoC） → 验证通过 → LangChain（生产）
```

**面试话术**：
> "这两个不是二选一的关系。团队实践中，我们用 Dify 做快速原型验证和给业务人员搭建简单应用，用 LangChain/LangGraph 做生产级 Agent。比如公交投诉系统——先用 Dify 画出工作流验证逻辑通不通，确认后移植到 LangGraph 做代码级控制，包括自定义记忆策略、A/B 测试框架、全链路追踪。"

#### 12.6 深层理解：LangChain 的设计模式

```
1. Chain of Responsibility（责任链）
   prompt | llm | parser | post_processor
   每个环节只做一件事，管道串联
   → 对应 Java: FilterChain / Interceptor

2. Strategy（策略模式）
   LLM 是可替换的：ChatOpenAI / ChatAnthropic / ChatOllama
   都实现 BaseChatModel，运行时切换
   → 对应 Java: @Autowired + @Qualifier

3. Template Method（模板方法）
   BaseTool._run() → 子类实现具体逻辑
   AgentExecutor 固定执行流程（think→act→observe循环）
   → 对应 Java: AbstractClass + 子类 override

4. Builder（建造者）
   ChatPromptTemplate.from_messages(...) 
   StateGraph.add_node().add_edge().compile()
   → 对应 Java: Lombok @Builder

5. Observer（观察者）
   callbacks 机制：on_llm_start / on_tool_end / on_chain_end
   → 对应 Java: EventListener / ApplicationEvent
```

#### 12.7 Day 12-13 练习题

**题目**：用 LCEL 实现一个带"兜底策略"的 RAG Chain

> 要求：先向量检索 → 如果检索结果为空 → 回退到 SQL 查询 → 如果 SQL 也为空 → 回答"未找到相关信息"

<details>
<summary><b>点击查看参考答案</b></summary>

```python
from langchain_core.runnables import RunnableBranch, RunnableLambda

# 定义两条分支
def docs_not_empty(state):
    """检索结果非空 → 用文档生成回答"""
    return len(state.get("docs", [])) > 0

# RAG 分支
rag_branch = (
    RunnableLambda(lambda s: {
        "context": "\n\n".join(d.content for d in s["docs"]),
        "question": s["question"]
    })
    | rag_prompt | llm | StrOutputParser()
)

# SQL fallback 分支
sql_branch = (
    RunnableLambda(lambda s: {
        "question": s["question"]
    })
    | sql_prompt | llm | StrOutputParser()
)

# 兜底分支
fallback_branch = RunnableLambda(lambda s: "抱歉，未找到相关信息，请尝试换个关键词。")

# 用 RunnableBranch 组合（类比 Java switch-case）
retrieval_chain = RunnableBranch(
    (docs_not_empty, rag_branch),     # if: 有文档 → RAG
    sql_branch,                        # elif: 调用 SQL
    # 默认走 fallback
)

# 整体流程
full_chain = {
    "docs": retriever,
    "question": RunnablePassthrough()
} | retrieval_chain
```
</details>

---

> 📄 **配套实战文档**：`LangChain从零到调通后端接口-实战手册.md` — 从安装 Python 虚拟环境、`pip install langchain`、配置 API Key、手写 Agent Demo、到最终调通一个 Spring Boot 后端接口的完整步骤。**用 Hermes 终端在 Windows 本机实操，每一步都有预期输出和验证方法。**

---

### Day 14：LangChain 实战项目 — 班车调度助手

这是直接对应你公交业务的实战项目。

**场景**：企业客户通过 Agent 查询班车线路、调整发车时间、申请临时加班车。

```python
"""
LangChain Agent: 企业班车调度助手
技术栈: LangChain + OpenAI + FastAPI
对标模块: 长保业务 — 企业班车
"""

from langchain.agents import AgentExecutor, create_openai_tools_agent
from langchain_openai import ChatOpenAI
from langchain.tools import tool
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.memory import ConversationBufferWindowMemory
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
import json

# ==================== 1. 领域模型（对应你的数据库表） ====================

class BusRoute(BaseModel):
    """班车线路 — 对应 line_route 表"""
    route_id: str = Field(description="线路ID")
    name: str = Field(description="线路名称，如'阿里西溪-EFC班车'")
    origin: str
    destination: str
    stops: List[str] = Field(description="途经站点")
    schedule: List[dict] = Field(description="发车时刻表")
    driver_id: Optional[str] = None
    vehicle_id: Optional[str] = None

class TempBusRequest(BaseModel):
    """临时加班车申请 — 对应 temp_bus_order 表"""
    request_id: str
    company: str
    route: str
    date: str
    passenger_count: int
    reason: str
    status: str = "pending"  # pending/approved/rejected

# ==================== 2. 模拟数据库（实际对接 MySQL） ====================

ROUTES_DB = {
    "R001": BusRoute(
        route_id="R001",
        name="阿里西溪—EFC班车",
        origin="阿里巴巴西溪园区",
        destination="欧美金融城(EFC)",
        stops=["阿里西溪南门", "海创园", "EFC南门"],
        schedule=[
            {"time": "08:00", "type": "上班"},
            {"time": "08:20", "type": "上班"},
            {"time": "18:00", "type": "下班"},
            {"time": "18:30", "type": "下班"},
        ],
        driver_id="D001",
        vehicle_id="V001"
    ),
    "R002": BusRoute(
        route_id="R002",
        name="网易—云栖小镇班车",
        origin="网易大厦",
        destination="云栖小镇",
        stops=["网易大厦", "转塘", "云栖小镇"],
        schedule=[
            {"time": "08:30", "type": "上班"},
            {"time": "17:30", "type": "下班"},
        ],
        driver_id="D002",
        vehicle_id="V002"
    ),
}

TEMP_REQUESTS = []

# ==================== 3. 工具定义（LangChain @tool 装饰器） ====================

@tool
def search_route(company_name: str) -> str:
    """
    根据企业名称查询班车线路信息。
    参数: company_name - 企业名称（如'阿里'、'网易'）
    """
    results = []
    for rid, route in ROUTES_DB.items():
        if company_name in route.name or company_name in route.origin or company_name in route.destination:
            results.append({
                "route_id": route.route_id,
                "name": route.name,
                "origin": route.origin,
                "destination": route.destination,
                "stops": route.stops,
                "schedule": route.schedule,
                "driver_id": route.driver_id,
                "vehicle_id": route.vehicle_id,
            })
    if not results:
        return f"未找到'{company_name}'相关的班车线路"
    return json.dumps(results, ensure_ascii=False, indent=2)

@tool
def query_schedule(route_id: str, date: str = None) -> str:
    """
    查询指定线路的发车时刻表。
    参数: route_id - 线路ID；date - 查询日期(YYYY-MM-DD)，默认今天
    """
    if route_id not in ROUTES_DB:
        return f"线路{route_id}不存在"
    route = ROUTES_DB[route_id]
    return json.dumps({
        "route_name": route.name,
        "schedule": route.schedule,
        "date": date or datetime.now().strftime("%Y-%m-%d"),
    }, ensure_ascii=False, indent=2)

@tool
def request_temp_bus(company: str, route_id: str, date: str, passenger_count: int, reason: str) -> str:
    """
    申请临时加班车。
    参数:
        company - 企业名称
        route_id - 线路ID
        date - 发车日期(YYYY-MM-DD)
        passenger_count - 预计乘车人数
        reason - 申请原因
    """
    request_id = f"TMP-{len(TEMP_REQUESTS)+1:04d}"
    req = TempBusRequest(
        request_id=request_id,
        company=company,
        route=route_id,
        date=date,
        passenger_count=passenger_count,
        reason=reason,
        status="pending"
    )
    TEMP_REQUESTS.append(req)
    
    # 这里对接你的调度逻辑：检查车辆/司机可用性、判断是否需要额外审批
    return json.dumps({
        "request_id": request_id,
        "status": "pending",
        "message": f"加班车申请已提交（{date}，{passenger_count}人），等待调度确认",
        "estimated_response": "1小时内",
    }, ensure_ascii=False, indent=2)

@tool
def check_driver_availability(date: str, time_slot: str) -> str:
    """
    检查指定日期时段的司机可用性。
    参数:
        date - 日期(YYYY-MM-DD)
        time_slot - 时段，如'早高峰'、'晚高峰'、'平峰'
    """
    # 实际对接 driver_schedule 表，这里模拟
    available_drivers = [
        {"id": "D003", "name": "王师傅", "vehicle_type": "大巴(50座)"},
        {"id": "D005", "name": "李师傅", "vehicle_type": "中巴(30座)"},
    ]
    return json.dumps({
        "date": date,
        "time_slot": time_slot,
        "available_drivers": available_drivers,
        "total_available": len(available_drivers),
    }, ensure_ascii=False, indent=2)

# ==================== 4. Agent 构建 ====================

SYSTEM_PROMPT = """你是企业班车调度助手，服务于「公共出行平台」的长保业务线。

## 职责
1. 帮助企业客户查询班车线路、发车时刻表
2. 受理临时加班车申请
3. 检查司机/车辆可用性
4. 回答班车运营相关问题

## 规则
- 加班车申请超过50人的，需提醒"可能需要大型车辆，调度时间可能延长"
- 申请时需确认日期、人数、原因三个要素缺一不可
- 所有信息基于工具查询结果，不编造

## 工作流程
1. 分析用户意图（查询/申请/咨询）
2. 如果信息不全，追问补充
3. 调用工具获取结果
4. 友好呈现结果
"""

def create_bus_agent():
    """创建班车调度 Agent"""
    
    llm = ChatOpenAI(
        model="gpt-4",
        temperature=0.3,
        # 实际部署配置 api_key
    )
    
    tools = [search_route, query_schedule, request_temp_bus, check_driver_availability]
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", SYSTEM_PROMPT),
        MessagesPlaceholder(variable_name="chat_history"),
        ("human", "{input}"),
        MessagesPlaceholder(variable_name="agent_scratchpad"),
    ])
    
    # 使用 ConversationBufferWindowMemory 保留最近5轮对话
    memory = ConversationBufferWindowMemory(
        memory_key="chat_history",
        return_messages=True,
        k=5,
    )
    
    agent = create_openai_tools_agent(llm, tools, prompt)
    
    return AgentExecutor(
        agent=agent,
        tools=tools,
        memory=memory,
        verbose=True,
        max_iterations=10,
        handle_parsing_errors=True,
        return_intermediate_steps=True,  # 返回中间步骤，用于追踪
    )

# ==================== 5. FastAPI 接口 ====================

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI(title="班车调度 Agent API")
agent_executor = create_bus_agent()

class ChatRequest(BaseModel):
    message: str
    session_id: str = "default"

class ChatResponse(BaseModel):
    answer: str
    intermediate_steps: Optional[List] = None
    session_id: str

@app.post("/api/bus-agent/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """班车调度 Agent 对话接口"""
    try:
        result = await agent_executor.ainvoke({
            "input": request.message,
        })
        return ChatResponse(
            answer=result["output"],
            intermediate_steps=result.get("intermediate_steps", []),
            session_id=request.session_id,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

class TempBusAPI:
    """
    临时加班车申请 API — 对接你的 Spring Boot 后端
    
    调用链:
    小程序 → Spring Boot Controller → Feign/HTTP → 此 Agent API
    """
    
    @staticmethod
    async def handle_temp_bus_request(request_data: dict) -> dict:
        """处理临时班车申请（被 Spring Boot 调用）"""
        company = request_data.get("company", "")
        route_id = request_data.get("route_id", "")
        date = request_data.get("date", "")
        count = request_data.get("passenger_count", 0)
        reason = request_data.get("reason", "")
        
        # Agent 自动处理
        query = f"企业{company}申请临时加班车: 线路{route_id}, 日期{date}, {count}人, 原因:{reason}"
        result = await agent_executor.ainvoke({"input": query})
        return {"agent_response": result["output"]}

# ==================== 6. 测试用例 ====================

async def test_cases():
    agent = create_bus_agent()
    
    # 测试1: 查询班车
    test1 = "帮我查一下阿里的班车线路"
    result = await agent.ainvoke({"input": test1})
    print(f"✅ 测试1: {result['output'][:200]}")
    
    # 测试2: 申请加班车
    test2 = "阿里需要申请明天早上8点的加班车，预计60人，因为季度总结大会"
    result = await agent.ainvoke({"input": test2})
    print(f"✅ 测试2: {result['output'][:200]}")
    
    # 测试3: 多轮对话
    test3 = "刚才申请的加班车，司机确定了吗？"
    result = await agent.ainvoke({"input": test3})
    print(f"✅ 测试3: {result['output'][:200]}")

# asyncio.run(test_cases())
```

---

