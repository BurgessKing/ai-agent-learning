# AI Agent 强化学习计划

> Java 架构师 → AI Agent 开发工程师，1-2 个月系统学习与实践
>
> **v3.0 核心理念**：底层 > 框架。框架是确认层，不是入门砖。

[![Status](https://img.shields.io/badge/status-Phase1-orange)](https://github.com/BurgessKing/ai-agent-learning)
[![LangChain](https://img.shields.io/badge/LangChain-1.3.13-blue)](https://python.langchain.com)

> 📍 **[项目目标与路线图 →](./ROADMAP.md)**

---

## 📂 文档导航

| # | 模块 | 核心内容 | 周期 |
|---|------|----------|------|
| 01 | [LLM底层与Prompt工程](./docs/01-LLM底层与Prompt工程.md) | 原生API调用、Token计算、SystemPrompt、Few-shot/CoT、手写Agent、Transformer深入、Tokenization | Day 1-7 |
| 02 | [ToolUse与RAG实战](./docs/02-ToolUse与RAG实战.md) | Function Calling、Schema设计、RAG分块实验、Embedding选型、混合检索、RAG评估体系 | Day 8-14 |
| 03 | [Agent深度概念](./docs/03-Agent深度概念.md) | Plan-and-Execute、Multi-Agent协作、上下文工程四层、模型调优、通信协议、冲突解决 | Day 15-18 |
| 04 | [框架与工程化](./docs/04-框架与工程化.md) | LangChain、上下文管理、Token成本、可观测性、降级容错、流式输出全链路 | Day 19-21 |
| 05 | [公交平台AI融合架构](./docs/05-公交平台AI融合架构.md) | ⭐ 终极项目：公交出行平台 + AI Agent 全栈融合（调度 + 报价） | Day 22-28 |
| 06 | [面试题与学习资源](./docs/06-面试题与学习资源.md) | 13道高频面试题、学习资源、4周作息表 | — |
| 07 | [AI基础设施与部署](./docs/07-AI基础设施与部署.md) | 🆕 GPU选型、模型部署(vLLM/Ollama)、微调全链路、LoRA/QLoRA、模型量化 | — |
| 08 | [Agent评估与安全](./docs/08-Agent评估与安全.md) | 🆕 评估体系(任务完成率/LLM-as-Judge)、RAG评估(Recall/MRR)、安全(Prompt注入/权限/脱敏) | — |
| 09 | [多模态与MCP协议](./docs/09-多模态与MCP协议.md) | 🆕 多模态Agent(Vision/OCR/语音)、MCP协议规范与实践、Agent前沿方向 | — |

## 🛠 配套实战

| 项目 | 路径 | 说明 |
|------|------|------|
| LangChain Agent Demo | [langchain-demo/](./langchain-demo/) | DeepSeek + LangChain 1.3，已验证三场景 |
| 操作手册 | [LangChain操作手册.md](./LangChain操作手册.md) | 环境 + 命令 + 问题速查 |

## 📊 学习路线

```
Week 1  底层 ████████  LLM原生API → Prompt → 手写Agent（零框架）
Week 2  实战 ████████  Tool Use → RAG调优（参数自己跑实验）
Week 3  深度 ████████  Agent概念 → 框架（确认层，一看就懂）
Week 4  落地 ████████  工程化上线 → 终极项目（公交平台AI融合）
```

## 🎯 目标

- **岗位**: 杭州 AI Agent 开发/架构 | **薪资**: 30-40K
- **策略**: 公交行业壁垒 + Agent 工程能力 + LLM 深度理解
- **差异化**: 不是"用过 LangChain"，而是"从底层原理到工程上线全栈掌握"
