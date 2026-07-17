"""
LLM API 参数全量实验 — DeepSeek
每个参数单独实验，观察真实输出差异
"""
import httpx, json, os, sys
from dotenv import load_dotenv
load_dotenv()

API_KEY = os.getenv("DEEPSEEK_API_KEY")
BASE_URL = os.getenv("OPENAI_BASE_URL", "https://api.deepseek.com/v1")

if not API_KEY:
    print("❌ 请在 .env 中设置 DEEPSEEK_API_KEY")
    sys.exit(1)

def call(prompt: str, system: str = "", **kwargs) -> dict:
    """统一调用函数"""
    messages = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": prompt})

    defaults = {"model": "deepseek-chat", "temperature": 0.7, "max_tokens": 200}
    defaults.update(kwargs)

    r = httpx.post(
        f"{BASE_URL}/chat/completions",
        headers={"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"},
        json={"messages": messages, **defaults},
        timeout=30
    )
    data = r.json()
    usage = data.get("usage", {})
    return {
        "content": data["choices"][0]["message"]["content"],
        "prompt_tokens": usage.get("prompt_tokens", 0),
        "completion_tokens": usage.get("completion_tokens", 0),
    }

def header(title):
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}")

# ============================================================
# 实验1: Temperature — 控制"创造性"
# 0=死板确定, 0.5=平衡, 1.0=天马行空
# ============================================================
header("实验1: Temperature 对比 (0 / 0.5 / 1.0)")

prompt = "用一句话形容杭州的公交系统"
for temp in [0, 0.5, 1.0]:
    r = call(prompt, temperature=temp, max_tokens=50)
    print(f"\nTemperature={temp}: {r['content']}")
    print(f"  Tokens: prompt={r['prompt_tokens']}, completion={r['completion_tokens']}")

# ============================================================
# 实验2: max_tokens — 输出长度硬截断
# 设得太小会截断答案，太大浪费钱
# ============================================================
header("实验2: max_tokens 对比 (30 / 100 / 300)")

prompt = "详细介绍一下杭州西湖的历史文化和主要景点"
for mt in [30, 100, 300]:
    r = call(prompt, temperature=0.3, max_tokens=mt)
    finish = "..." if r['completion_tokens'] >= mt else " [完整]"
    print(f"\nmax_tokens={mt}: {r['content'][:150]}{finish}")
    print(f"  实际消耗 completion_tokens={r['completion_tokens']}")

# ============================================================
# 实验3: System Prompt — 角色设定到底多管用
# 对比无/有/强约束三种
# ============================================================
header("实验3: System Prompt 约束力对比")

prompt = "杭州有什么好吃的？"

# 无 System
r = call(prompt, temperature=0.5, max_tokens=100)
print(f"\n【无 System Prompt】\n{r['content'][:200]}")

# 有 System
r = call(prompt, system="你只回答3句话以内，语气简洁冷淡。", temperature=0.5, max_tokens=100)
print(f"\n【System: 简洁冷淡】\n{r['content'][:200]}")

# 强 System
r = call(prompt, system="""你是杭州公交智能客服，只回答公交相关问题。
如果用户问吃的，就说"我是公交助手，不清楚美食信息。需要查询公交路线吗？"
绝对不要回答非公交问题。""", temperature=0.5, max_tokens=100)
print(f"\n【System: 角色强约束】\n{r['content'][:200]}")

# ============================================================
# 实验4: Few-shot — 示例数量对格式对齐的影响
# ============================================================
header("实验4: Few-shot 示例数量 (0 / 1 / 3)")

# 0-shot
r = call("将'100路早高峰7:00-9:00间隔5分钟'转为JSON", temperature=0.1, max_tokens=100)
print(f"\n【0-shot】\n{r['content'][:200]}")

# 1-shot
r = call("""将公交信息转为JSON。示例：
输入: 55路首班6:00末班22:00
输出: {"route":"55","first":"06:00","last":"22:00"}

现在转换: 100路早高峰7:00-9:00间隔5分钟""", temperature=0.1, max_tokens=100)
print(f"\n【1-shot】\n{r['content'][:200]}")

# 3-shot
r = call("""将公交信息转为JSON。
示例1: 1路 → {"route":"1"}
示例2: 55路首班6:00末班22:00 → {"route":"55","first":"06:00","last":"22:00"}
示例3: 28路早高峰7:30-9:30间隔6分钟 → {"route":"28","peak":{"start":"07:30","end":"09:30","interval":6}}
现在转换: 100路早高峰7:00-9:00间隔5分钟""", temperature=0.1, max_tokens=150)
print(f"\n【3-shot】\n{r['content'][:200]}")

# ============================================================
# 实验5: stop 参数 — 让输出停在指定位置
# ============================================================
header("实验5: stop 停止词")

prompt = "列出杭州最热门的5个景点：1."
r = call(prompt, temperature=0.3, max_tokens=100, stop=["3."])
print(f"\n【stop=['3.']】\n{r['content'][:200]}")
print(f"  (在遇到'3.'时停止，即使还有 max_tokens)")

# ============================================================
# 实验6: 成本计算 — 每次调用到底花多少钱
# ============================================================
header("实验6: Token 成本计算")

# 长输入 + 长输出场景
long_prompt = "请详细介绍杭州公交的发展历史、主要线路、票价政策、未来规划。" + "请尽量详细。" * 10
r = call(long_prompt, temperature=0.5, max_tokens=500)

pt = r['prompt_tokens']
ct = r['completion_tokens']
# DeepSeek 定价: 输入 ¥1/百万token, 输出 ¥2/百万token
cost = (pt / 1_000_000) * 1 + (ct / 1_000_000) * 2

print(f"""
长文本调用成本:
  prompt_tokens:     {pt:,}
  completion_tokens: {ct:,}
  total_tokens:      {pt+ct:,}
  本次花费:          ¥{cost:.6f}

  如果日活 1000 次类似调用:
  日成本:            ¥{cost * 1000:.2f}
  月成本:            ¥{cost * 1000 * 30:.2f}
""")

# ============================================================
# 实验7: CoT — 要求"逐步思考"对推理的影响
# ============================================================
header("实验7: CoT (Chain-of-Thought) 效果")

math_q = "100路公交车早高峰每5分钟发一班，从7:00到9:00共发多少班？"

# 直接问
r = call(math_q, temperature=0.1, max_tokens=50)
print(f"\n【直接问】\n{r['content'][:200]}")

# CoT
r = call(f"{math_q}\n\n请一步步推理，先写出计算过程，再给出答案。", temperature=0.1, max_tokens=200)
print(f"\n【CoT 逐步推理】\n{r['content'][:300]}")

print(f"\n{'='*60}")
print("  全部实验完成")
print(f"{'='*60}")
