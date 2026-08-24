# 09 — 多模态与 MCP 协议

> **覆盖**：多模态 Agent（图片/语音/OCR）、MCP 协议规范与实现、Agent 前沿方向

---

## 一、多模态 Agent

### 1.1 什么是多模态

```
单模态（当前）:  用户输入文本 → LLM → 输出文本
多模态:          用户输入 图片/语音/视频/文件 → LLM → 输出 文本/图片/结构化数据
```

**公交业务场景**：

| 场景 | 输入 | 期望输出 |
|------|------|----------|
| 司机上传事故照片 | 图片（碰撞现场） | 事故描述 + 严重程度评估 |
| 证件识别 | 图片（驾驶证/行驶证） | 结构化信息（姓名/证号/有效期） |
| 语音投诉 | 音频（乘客录音） | 文本转录 + 投诉分类 |
| 合同/协议识别 | PDF/图片（包车合同） | 提取关键条款 |

### 1.2 图片理解（Vision）

```python
"""多模态 LLM — DeepSeek 支持 Vision，需使用 deepseek-chat 模型"""

# DeepSeek 多模态调用（兼容 OpenAI 格式）
from openai import OpenAI
client = OpenAI(
    api_key="sk-xxx",
    base_url="https://api.deepseek.com/v1"
)

response = client.chat.completions.create(
    model="deepseek-chat",  # DeepSeek 已支持图片输入
    messages=[{
        "role": "user",
        "content": [
            {"type": "text", "text": "这张图片里的公交车车牌号是什么？损伤程度如何？"},
            {"type": "image_url", "image_url": {"url": "https://example.com/bus_damage.jpg"}}
        ]
    }]
)
print(response.choices[0].message.content)

# 本地 base64 图片
import base64
with open("accident.jpg", "rb") as f:
    image_b64 = base64.b64encode(f.read()).decode()

response = client.chat.completions.create(
    model="deepseek-chat",
    messages=[{
        "role": "user",
        "content": [
            {"type": "text", "text": "描述这张事故照片"},
            {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{image_b64}"}}
        ]
    }]
)
```

### 1.3 OCR + LLM 组合

```python
"""
纯多模态 LLM 识别精度不如专业 OCR
推荐: 专业 OCR 提取文字 → LLM 理解语义

架构:
  图片 → PaddleOCR/Tesseract → 结构化文本 → LLM → JSON
"""

# 方案 1: PaddleOCR（中文最强）
# pip install paddleocr
from paddleocr import PaddleOCR
ocr = PaddleOCR(lang='ch')
result = ocr.ocr("driver_license.jpg")
# 返回: [[坐标, (文字, 置信度)], ...]

# 方案 2: 用多模态 LLM 直接提取
def extract_driver_license(image_path: str) -> dict:
    """从驾驶证图片提取结构化信息"""
    with open(image_path, "rb") as f:
        image_b64 = base64.b64encode(f.read()).decode()

    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=[{
            "role": "user",
            "content": [
                {"type": "text", "text": """
提取驾驶证上的信息，输出 JSON:
{"name": "", "license_no": "", "vehicle_type": "", "valid_from": "", "valid_to": ""}
如果看不清，对应的值填 null
"""},
                {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{image_b64}"}}
            ]
        }],
        response_format={"type": "json_object"}
    )
    return json.loads(response.choices[0].message.content)
```

### 1.4 语音处理

```python
"""
语音 → 语音识别 → LLM（理解+处理）

DeepSeek 当前不提供原生语音 API。方案：
  - 选项 A: 本地 Whisper（免费，推荐）
  - 选项 B: 通义听悟 API（阿里云，¥2.8/小时）
"""

# 本地 Whisper（推荐，需 GPU 加速）
# pip install openai-whisper
import whisper
model = whisper.load_model("medium")  # tiny/base/small/medium/large
result = model.transcribe("complaint.mp3", language="zh")
print(result["text"])  # "喂，我要投诉100路司机，到站不停..."


---

## 二、MCP 协议

### 2.1 为什么需要 MCP

```
没有 MCP 时:
  LangChain Agent  → @tool 装饰器 → 调 API
  CrewAI Agent     → BaseTool 子类 → 重新实现
  AutoGen Agent    → Function 注册  → 再重新实现

  结果: 换框架 = 重写所有工具

有了 MCP:
  所有工具写成 MCP Server
  所有 Agent 框架用 MCP Client 调用
  结果: 一次编写，到处使用
```

### 2.2 MCP 协议规范

```
MCP 架构:

┌──────────────┐     JSON-RPC      ┌──────────────┐
│  MCP Client  │ ←──────────────→  │  MCP Server  │
│  (Agent)     │   (stdio/HTTP)    │  (Tool提供方) │
└──────────────┘                   └──────────────┘

通信方式:
  - stdio: 本地进程通信（推荐，零网络开销）
  - HTTP + SSE: 远程服务通信

核心概念:
  - Resources: 暴露数据（类似 REST GET）
  - Tools: 暴露可执行函数（类似 REST POST）
  - Prompts: 预定义的 Prompt 模板
  - Sampling: Server 请求 Client 的 LLM 能力
```

### 2.3 MCP Server 实现

```python
"""
MCP Server — 公交业务工具标准化

pip install mcp
"""

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent
import json

server = Server("bus-tools")

@server.list_tools()
async def list_tools() -> list[Tool]:
    """注册可用工具"""
    return [
        Tool(
            name="search_route",
            description="查询公交路线。当用户询问'怎么走''坐什么车'时使用。",
            inputSchema={
                "type": "object",
                "properties": {
                    "origin": {"type": "string", "description": "出发地，如'西湖'"},
                    "destination": {"type": "string", "description": "目的地，如'火车东站'"}
                },
                "required": ["origin", "destination"]
            }
        ),
        Tool(
            name="calculate_price",
            description="计算包车报价",
            inputSchema={
                "type": "object",
                "properties": {
                    "distance_km": {"type": "number", "description": "往返总里程"},
                    "passenger_count": {"type": "integer"},
                    "vehicle_type": {"type": "string", "enum": ["大巴", "中巴", "商务车"]},
                },
                "required": ["distance_km", "passenger_count", "vehicle_type"]
            }
        ),
    ]

@server.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    """执行工具"""
    if name == "search_route":
        origin = arguments["origin"]
        dest = arguments["destination"]
        # 实际调用你的 Java 后端 API
        result = {"routes": [{"no": "100路", "duration": 35}]}
        return [TextContent(type="text", text=json.dumps(result, ensure_ascii=False))]

    if name == "calculate_price":
        base = arguments["distance_km"] * 8
        surcharge = {"大巴": 500, "中巴": 300, "商务车": 200}.get(arguments["vehicle_type"], 0)
        total = base + surcharge
        return [TextContent(type="text", text=f"报价: ¥{total}")]

    raise ValueError(f"Unknown tool: {name}")

# 启动 Server（stdio 模式）
# 运行: python mcp_server.py
async def main():
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream)
```

### 2.4 MCP Client（Agent 侧）

```python
"""
Agent 通过 MCP Client 调用工具
LangChain / CrewAI 都可以用同一个 MCP Server
"""

from mcp.client import Client
from mcp.client.stdio import stdio_client

async def get_tools_from_mcp():
    """从 MCP Server 获取工具列表 → 转为 LangChain Tool"""
    async with stdio_client("python mcp_server.py") as (read, write):
        async with Client(read, write) as client:
            tools = await client.list_tools()

            langchain_tools = []
            for tool in tools:
                langchain_tools.append(StructuredTool(
                    name=tool.name,
                    description=tool.description,
                    args_schema=_build_pydantic_schema(tool.inputSchema),
                    func=lambda **kwargs: client.call_tool(tool.name, kwargs)
                ))
            return langchain_tools
```

### 2.5 MCP vs Function Calling

| 维度 | Function Calling | MCP |
|------|-----------------|-----|
| **标准化** | 每个 LLM 有自己的格式 | 统一协议，跨 LLM 通用 |
| **工具复用** | 绑定到特定 Agent | 一次编写，多 Agent 共享 |
| **动态发现** | 工具在代码里写死 | Agent 运行时发现可用工具 |
| **成熟度** | 非常成熟 | 2024年底发布，生态快速增长 |
| **适用** | 单 Agent 固定工具 | 多 Agent、工具市场、外部集成 |

**面试话术**：
> "MCP 正在成为 Agent 生态的标准协议。我们的架构已经开始预留 MCP 接口——公交业务系统通过 MCP Server 暴露能力，未来无论用 LangChain 还是其他框架，工具层不用重写。"

---

## 三、Agent 前沿方向

### 3.1 当前值得关注的趋势

| 方向 | 说明 | 与你的关联 |
|------|------|-----------|
| **Computer Use** | Agent 操作桌面/GUI | 调度员工作台自动化 |
| **Code Agent** | Agent 写代码并执行 | 报表自动生成 |
| **Long-term Memory** | 跨会话持久记忆 | 乘客偏好记忆 |
| **Agent Swarm** | 大规模 Agent 协作 | 大规模调度优化 |
| **Agent-as-Judge** | Agent 评估 Agent | 服务质量自动化监控 |

### 3.2 保持敏感度的方式

```
1. GitHub Trending: 关注 langchain/crewAI/autogen 等仓库
2. X(Twitter): @LangChainAI, @AnthropicAI, @OpenAI
3. 论文: arXiv cs.CL / cs.AI 每日更新
4. 实战: HuggingFace Spaces 上的 Demo
```

---

> **面试应对**: "MCP 是 Agent 工具标准化的关键。我们公交平台的车辆查询、调度、报价能力未来都会通过 MCP Server 暴露，这样无论前端 Agent 框架怎么变，工具层稳如泰山。"
