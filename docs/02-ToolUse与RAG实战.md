# 02 — Tool Use 与 RAG 实战

> **核心原则**：Tool Use 是 Agent 的分水岭——过了这步才算真正入门。RAG 不是"装个向量库就行"，参数全是针对业务一点一点试出来的。
>
> **学习周期**：Day 8-14 | **目标**：能手写完整的 Function Calling 流程 + 能搭一个真能用的 RAG 系统

---

## 第一阶段：Tool Use / Function Calling（Day 8-10）

> 文章说："这一步是分水岭。Agent = 大模型 + 工具 + 循环。"

### 1.1 Schema 设计 — 工具描述怎么写

这是 Function Calling 最核心也最被忽视的部分。Schema 写得好不好，直接决定 Agent 能不能正确选工具。

```python
"""
工具 Schema 设计原则

差的 Schema:
  {"name": "f1", "description": "do something", "parameters": {"x": "string"}}
  → LLM 不知道什么时候该调、参数该填什么

好的 Schema:
  {"name": "search_bus_route",
   "description": "查询两个具体地名之间的公交路线，返回线路号、耗时、票价。当用户询问'怎么走''坐什么车'时使用。",
   "parameters": {
     "origin": "string, 出发地的具体名称，如'西湖'、'杭州东站'。不要用模糊描述如'市中心'。",
     "destination": "string, 目的地的具体名称"
   }}
  → LLM 明确知道使用场景和参数要求
"""

# ===== Schema 设计检查清单 =====
# 1. description 里说清楚"什么时候用这个工具"（触发场景）
# 2. 每个参数的 description 包含示例值（不要只写"string"）
# 3. 如果是枚举值，用 enum 列出所有选项
# 4. required 字段准确标注——可选参数不要标 required
# 5. 工具名称用动词开头：search_xxx, get_xxx, create_xxx
```

### 1.2 消息格式 — Agent 的通信协议

```python
"""
Function Calling 的完整消息流转

这是 Agent 开发最重要的"通信协议"，搞懂了就明白 LangChain 在包什么。
"""

# ===== 第1轮: 用户请求 → LLM 返回 tool_calls =====

request_messages = [
    {"role": "system", "content": "你是公交助手。有工具可用时使用工具。"},
    {"role": "user",   "content": "查西湖到火车东站公交"}
]

# LLM 返回（不是文本，是 tool_calls 数组）:
response = {
    "choices": [{
        "message": {
            "role": "assistant",
            "content": None,  # 注意: content 为 null
            "tool_calls": [{
                "id": "call_abc123",
                "type": "function",
                "function": {
                    "name": "search_route",
                    "arguments": '{"origin":"西湖","destination":"火车东站"}'
                }
            }]
        }
    }]
}

# ===== 第2轮: 你的代码执行工具 → 结果返回 LLM =====

# 你必须在 messages 中添加两条记录：
messages = [
    # ... 前面的消息 ...
    
    # 2a. 先添加 assistant 的 tool_calls 消息（原样回传）
    {"role": "assistant", "content": None, "tool_calls": [tool_call]},

    # 2b. 再添加 tool 角色的返回结果
    {"role": "tool", "tool_call_id": "call_abc123", "content": '{"routes":[{"no":"100路","duration":35}]}'},
]

# 然后再次 call_llm(messages) → LLM 基于工具结果生成最终回答
```

### 1.3 工具执行失败的兜底

```python
"""
工具挂了怎么兜底 — 这是 Demo 和生产的分界线
"""

def execute_tool_with_fallback(tool_name: str, args: dict, max_retries: int = 2) -> str:
    """带重试和兜底的工具执行"""
    import time

    for attempt in range(max_retries + 1):
        try:
            result = TOOLS[tool_name](**args)
            
            # 空结果兜底
            if not result or result == "[]":
                return f"工具 {tool_name} 未查到结果，建议换个关键词或检查参数"
            
            # 结果太大截断
            if len(str(result)) > 4000:
                result = str(result)[:4000] + "...(已截断)"
            
            return str(result)

        except Exception as e:
            if attempt < max_retries:
                time.sleep(1 * (attempt + 1))  # 递增延迟
            else:
                return f"工具 {tool_name} 执行失败({max_retries+1}次): {e}。请告知用户稍后重试。"
```

---

## 第二阶段：RAG 检索增强生成（Day 11-14）

> 文章的核心观点：RAG 应该在 Tool Use 之后学——因为你已经知道大模型哪里不行，才会自然需要 RAG。
>
> 另一关键：**参数没有标准答案，全是针对业务试出来的。**

### 2.1 文本切分 — Chunk Size 不是玄学

```python
"""
Chunk Size 选择 — 对着业务试，不是抄教程

实验记录（公交运营手册，50页PDF）:

| Chunk Size | Overlap | Top-3召回率 | Top-5召回率 | 备注 |
|-----------|---------|------------|------------|------|
| 256       | 50      | 71%        | 79%        | 太碎，上下文丢失 |
| 512       | 128     | 87%        | 93%        | ✅ 最佳 |
| 1024      | 200     | 73%        | 82%        | 噪音多 |
| 2000      | 300     | 58%        | 68%        | 粒度太粗 |

结论: 中文公交文档，512 chunk + 128 overlap 效果最好
"""

def find_best_chunk_params(documents: list, test_queries: list, sizes=[256, 512, 1024]):
    """
    找到最佳分块参数 — 这是 RAG 项目必做的实验
    别抄网上的数字，拿你自己的文档跑一遍
    """
    results = {}
    for size in sizes:
        overlap = size // 4  # overlap = 25%
        chunks = chunk_documents(documents, chunk_size=size, overlap=overlap)
        vector_store = build_index(chunks)
        
        recall = evaluate_recall(vector_store, test_queries)
        results[size] = recall
        print(f"Chunk={size}, Overlap={overlap} → Recall@5={recall:.1%}")
    
    best = max(results, key=results.get)
    print(f"\n✅ 最佳 Chunk Size: {best} (Recall@5={results[best]:.1%})")
    return best
```

### 2.2 向量化模型选型

```python
"""
Embedding 模型对比（公交领域实测参考）

| 模型 | 维度 | Top-5召回率 | 速度 | 费用 |
|------|------|-----------|------|------|
| text-embedding-3-small (OpenAI) | 1536 | 89% | 快 | $0.02/1M tokens |
| BGE-M3 (BAAI) | 1024 | 91% | 中 | 免费(本地) |
| BGE-Large-zh (BAAI) | 1024 | 88% | 中 | 免费(本地) |
| m3e-base (Moka) | 768 | 82% | 快 | 免费(本地) |

推荐: 本地部署 BGE-M3，效果最好且免费
"""

from sentence_transformers import SentenceTransformer

# 本地 Embedding — 不需要 API Key
model = SentenceTransformer("BAAI/bge-m3")

def embed_texts(texts: list[str]) -> list:
    """批量向量化 — BGE 模型输入前加 instruction 效果更好"""
    # BGE 模型需要用 '为这个句子生成表示以用于检索相关文章：' 前缀
    return model.encode(texts, normalize_embeddings=True).tolist()

def embed_query(query: str):
    """查询向量化 — 查询不加前缀"""
    return model.encode([query], normalize_embeddings=True)[0].tolist()
```

### 2.3 召回后处理 — 这才是 RAG 翻车的根子

> 文章中说："不是召不准，是召回来的东西乱七八糟塞进去，大模型根本抓不住重点。"

```python
"""
召回后处理 Pipeline — RAG 质量的最后一道关

原文问题: "把检索结果按段落重新排了序再喂，回答准确率从71%提到91%"
"""

def post_process_docs(docs: list, query: str) -> str:
    """
    三步处理:
    1. 去重 — 几乎一样的内容只留一条
    2. 重排序 — 按相关性重新排序（不是按向量距离排序）
    3. 结构化组装 — 每条标注来源，按优先级排列
    """
    # Step 1: 去重
    seen = set()
    unique = []
    for doc in docs:
        key = doc.page_content[:50]  # 用前50字做去重key
        if key not in seen:
            seen.add(key)
            unique.append(doc)
    
    # Step 2: 按来源分组 + 优先级排序
    # 运营手册 > 历史报告 > 其他文档
    priority = {"运营手册": 1, "调度规范": 1, "历史报告": 2}
    
    def sort_key(doc):
        source = doc.metadata.get("source", "")
        p = 3
        for k, v in priority.items():
            if k in source:
                p = v
                break
        return (p, -doc.metadata.get("score", 0))
    
    unique.sort(key=sort_key)
    
    # Step 3: 结构化组装
    parts = []
    for i, doc in enumerate(unique[:5], 1):
        source = doc.metadata.get("source", "未知")
        parts.append(f"【资料{i}】来源: {source}\n{doc.page_content}")
    
    return "\n\n---\n\n".join(parts)
```

### 2.4 非结构化+结构化混合检索

你的公交业务天生就有很多**结构化数据**（MySQL 里的客流表、排班表），不能只靠向量检索。

```python
"""
混合检索: 向量检索(语义) + SQL查询(精确) + 关键词(BM25)

场景: "100路上周五客流量多少？"
  → SQL: SELECT total FROM passenger_flow WHERE route='100' AND date='2024-01-12'
  → RAG: 检索"客流分析报告"中关于100路的分析结论
  → 合并: 精确数字 + 分析结论 → LLM 综合回答
"""

def hybrid_search(query: str):
    """混合检索 — 三路召回合并"""
    # 路1: SQL 查询（精确数据）
    sql_result = None
    if any(kw in query for kw in ["多少","几个","数量","百","千","万"]):
        sql_result = execute_sql_query(query)  # Text-to-SQL
    
    # 路2: 向量检索（语义相似）
    vector_docs = vector_store.similarity_search(query, k=3)
    
    # 路3: BM25 关键词（精确匹配）
    bm25_docs = bm25_index.search(query, k=3)
    
    # 合并去重
    all_context = []
    if sql_result:
        all_context.append(f"【数据库查询结果】\n{sql_result}")
    all_context.append(post_process_docs(vector_docs + bm25_docs, query))
    
    return "\n\n=====\n\n".join(all_context)
```

---

## 🎯 第二阶段检查点

- [ ] 能写出完整的 Function Calling 消息格式（assistant tool_calls + tool result）
- [ ] 工具 Schema 的 5 条设计原则都理解了吗？
- [ ] 工具执行失败有重试和兜底吗？
- [ ] Chunk Size 在你的文档上跑过实验吗？（别抄网上的512）
- [ ] Embedding 模型选型是你测过的还是随大流？
- [ ] 召回结果做后处理了吗（去重+重排序+结构化）？
- [ ] 结构化数据（SQL）和向量检索能混合召回吗？
