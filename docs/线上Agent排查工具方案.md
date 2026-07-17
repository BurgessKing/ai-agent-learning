# 线上Java问题排查：Hermes+Arthas智能体方案汇总

## 一、核心前置结论

- 

  线上环境严禁Agent完全自治，必须采用「Copilot+人工Approve」模式：Agent输出排查命令+意图说明，人工确认后执行，避免Arthas的redefine/tt -p等破坏性操作误触发。

- 

  Hermes在Linux/Docker环境下调用Arthas理论可行，但需要额外配置权限围栏（Guardrail）才能用于生产。

## 二、现有智能体方案分类

### 2.1 通用壳派（通用Agent将Arthas作为工具调用）

#### 2.1.1 Hermes + arthas-diag Skill（当前已有方案）

- 

  部署形态：Linux服务器部署Hermes Headless版（`hermes serve`+systemd保活），禁用GUI桌面版；Docker环境可通过宿主机`docker exec`桥接或Sidecar模式部署。

- 

  核心配置：

  - 

    关闭Hermes自进化能力（`auto_improve: false`），避免生产环境Skill被随意修改。

  - 

    terminal工具配置白名单，仅允许`java`/`jstack`/`jmap`/`top`/`ps`/`grep`/`curl`/`tail`等安全命令，禁止`rm`/`kill -9`等高危操作。

  - 

    编写`arthas-diag`Skill固化排查流程，强制所有Arthas操作前输出意图说明、等待人工确认。

- 

  优点：已有Hermes+DeepSeek技术栈，零迁移成本；支持长期记忆，可沉淀项目专属排查经验（如已知热点接口、典型慢SQL模式）。

- 

  缺点：Arthas命令为字符串拼接，非结构化工具调用；`trace`/`watch`输出易爆炸，需手动截断避免Token浪费。

- 

  适用场景：裸机/Docker单实例Java服务，单人运维，已有Hermes技术栈。

#### 2.1.2 Claude Code + Arthas MCP Gateway

- 

  核心能力：Arthas MCP Gateway暴露38个结构化工具（26个即时诊断、5个异步长任务、3个K8s编排、4个网关自有），Claude Code通过MCP协议调用，无需手动拼接命令。

  - 

    异步长任务支持：`watch`/`trace`/`stack`/`tt`/`monitor`等耗时操作返回`taskId`，后台运行不阻塞Agent，适合生产不停机场景。

  - 

    K8s原生编排：内置`k8s.ensure-arthas-mcp`工具，可自动定位Pod、注入Arthas MCP服务，无需人工执行`kubectl exec`。

- 

  配置示例：

```json
{
  "mcpServers": {
    "arthas-gw": {
      "type": "http",
      "url": "http://localhost:8761/mcp"
    }
  }
}
```

- 

  优点：结构化工具调用，风险可控；K8s场景适配极佳；异步任务避免生产卡死。

- 

  缺点：Claude Code框架本身需境外网络+虚拟卡（仅框架免费，模型可替换为DeepSeek降低成本）；国内社区案例较少。

- 

  适用场景：K8s多Pod集群，需要自动化Pod注入、异步任务支持的生产环境。

#### 2.1.3 Cursor/Trae + Arthas MCP

- 

  核心能力：IDE侧配置Arthas MCP Server（`arthas.properties`开启`arthas.mcpEndpoint=/mcp`），可直接在IDE内自然语言触发Arthas排查，结果直接在IDE面板展示。

- 

  优点：开发/预发环境调试体验极佳，无需切换终端。

- 

  缺点：仅适合开发/预发环境，生产服务器不会部署IDE。

- 

  适用场景：开发期问题复现、预发环境验证。

### 2.2 垂直Arthas Agent派（专为Arthas排查设计的专用Agent）

#### 2.2.1 Arthas Agent（阿里云，2026.3发布）

- 

  核心设计：Skill-first（内置`arthas-cpu-high`/`arthas-springcontext-issues-resolve`等排障剧本）+ Safety-first（默认每轮仅执行1-2个低风险步骤，避免生产抖动）。

- 

  输出规范：结构化四段式诊断报告（结论/证据/原因/建议），30秒可输出Spring版本冲突、CPU飙高、Bean加载失败等典型问题结论。

- 

  优点：国产直连，Spring/阿里系项目适配极佳；排障逻辑经过阿里生产环境验证，风险极低。

- 

  缺点：灵活性低于通用Agent，无法沉淀项目专属记忆。

- 

  适用场景：阿里/Spring系Java服务，团队无Agent运维经验，追求开箱即用。

#### 2.2.2 Spectre

- 

  核心能力：零侵入（目标JVM无需预装Arthas、无需修改依赖，Spectre按需上传工具链+`jattach`挂载）；ABAC权限引擎（命令级访问控制+审计日志）；跨形态网关（统一支持SSH服务器/Docker/K8s集群）。

- 

  优点：生产级权限审计能力，多JVM实例统一管理，适合合规要求高的场景。

- 

  缺点：国内社区较小，生态成熟度待验证。

- 

  适用场景：金融/支付等对操作审计有强要求的场景，多JVM实例统一管控。

#### 2.2.3 ARMS Arthas诊断（阿里云）

- 

  核心能力：ARMS完全集成Arthas，白屏化操作`thread`/`trace`/`watch`/堆快照等功能，与ARMS TraceID打通，无需记忆Arthas命令。

- 

  优点：阿里云用户开箱即用，无需维护Agent；操作可追溯，符合合规要求。

- 

  缺点：灵活性低，不支持自然语言交互，无法自定义排查逻辑。

- 

  适用场景：阿里云环境，仅需基础Arthas排查能力，无定制化需求。

### 2.3 框架自建派（基于Agent框架自定义排查流程）

#### 2.3.1 LangGraph + Arthas工具节点 + DeepSeek

- 

  核心能力：将Arthas作为LangGraph的工具节点嵌入排查流程图，支持`interrupt()`人工审批、Checkpoint断点恢复、时间旅行回溯，完全贴合生产合规要求。

- 

  典型流程：告警触发→Prometheus/Loki采集上下文→Arthas工具节点执行诊断→`interrupt()`等待人工审批→飞书/企微推送结果→恢复验证→报告沉淀。

- 

  优点：框架级Guardrail，每一步操作都可审计、可回滚；国产DeepSeek模型直连，成本低。

- 

  缺点：需要额外部署Python服务，开发成本高。

- 

  适用场景：金融/支付/订单等对合规性、可追溯性有强要求的生产环境。

#### 2.3.2 Strands（AWS）+ Arthas MCP

- 

  核心能力：AWS推出的模型驱动Agent框架，LLM自主决定Arthas工具调用顺序，无需手动编排流程图；支持对接Arthas MCP Server。

- 

  优点：AWS生态适配极佳，模型驱动降低编排成本。

- 

  缺点：国内案例较少，非AWS生态适配一般。

- 

  适用场景：AWS环境，已有Strands技术栈。

### 2.4 K8s部署形态（与Agent方案正交，决定Arthas可达性）

#### 2.4.1 宿主机+kubectl/docker exec桥接

- 

  部署方式：宿主机部署Agent，通过`kubectl exec pod -c java-container`或`docker exec container`进入容器执行Arthas。

- 

  坑点：容器内PID可能为1（`ENTRYPOINT ["java","-jar"]`），需手动指定`--pid 1`；JDK版本需≥8u292/11.0.12，否则会报`UnsupportedClassVersionError`。

- 

  适用场景：小规模K8s集群，临时排查。

#### 2.4.2 Sidecar容器（生产级推荐）

- 

  部署方式：Pod开启`shareProcessNamespace: true`，新增arthas-sidecar容器（sleep infinity），通过emptyDir共享`/tmp`目录（Arthas socket通信目录）。

  - 

    子方案A：sidecar内部署Agent（Hermes/Claude Code），同PID命名空间下可直接`jps`看到业务进程。

  - 

    子方案B：sidecar仅运行Arthas MCP Server，外部Agent通过MCP协议调用。

- 

  优点：业务容器无侵入，权限隔离清晰，支持MutatingWebhook自动注入。

- 

  适用场景：中大型K8s集群，生产环境常态化排查。

#### 2.4.3 Arthas Tunnel Server集中管理

- 

  部署方式：Helm部署`arthas-tunnel-server`，所有Pod内的Arthas连接至Tunnel Server，通过Web控制台或API统一调用。

- 

  优点：多Pod集群统一管理，无需逐个登录Pod。

- 

  缺点：架构复杂度高，需额外维护Tunnel Server。

- 

  适用场景：大规模K8s集群，多团队共享排查入口。

## 三、选型矩阵

| 方案                             | 最贴场景                        | 国内可达性           | 生产Guardrail强度   | 备注                         |
| -------------------------------- | ------------------------------- | -------------------- | ------------------- | ---------------------------- |
| Hermes + arthas-diag Skill       | 裸机/Docker单实例，已有Hermes栈 | ✅ 直连               | 中（依赖Skill规则） | 零迁移成本，支持项目记忆     |
| Claude Code + Arthas MCP Gateway | K8s多Pod，需自动Pod注入         | ❌ 需代理（框架免费） | 高（工具级粒度）    | 异步任务+K8s编排能力极强     |
| Arthas Agent（阿里）             | 阿里/Spring系，追求开箱即用     | ✅ 直连               | 高（内置安全规则）  | 2026新出，排障逻辑经阿里验证 |
| Spectre                          | 多JVM实例，需ABAC审计           | ⚠️ 小众               | 极高（命令级审计）  | 架构工程化，合规首选         |
| LangGraph + Arthas节点           | 金融/支付，需合规追溯           | ✅ 直连               | 极高（框架级审批）  | 需额外Python服务，开发成本高 |
| ARMS Arthas诊断                  | 阿里云用户，无定制需求          | ✅ 直连               | 高（白屏操作审计）  | 灵活度低，无需维护Agent      |
| Cursor/Trae + Arthas MCP         | 开发/预发环境调试               | ✅ 直连               | 低（仅本地环境）    | 不适合生产                   |

## 四、落地建议

### 4.1 当前场景（已有Hermes+DeepSeek，裸机/Docker单实例）

1. 

   服务器部署Hermes Headless版，关闭`auto_improve`，配置terminal命令白名单。

2. 

   直接使用附录的`arthas-diag`Skill模板，先在预发环境验证2周，确认Skill行为稳定。

3. 

   生产环境首月所有Arthas操作强制人工确认，2周后可将`thread`/`dashboard`/`jstack`等只读命令的确认关闭，`trace`/`watch`/`redefine`保留人工确认。

4. 

   若使用Java21虚拟线程，需在Skill中增加虚拟线程识别规则：`thread -n 3`输出中出现`carrier`前缀时，需关联到上层虚拟线程业务逻辑。

### 4.2 扩容信号

- 

  信号1：order-service迁移至K8s多Pod集群 → 升级为「Claude Code + Arthas MCP Gateway」或「LangGraph + Arthas工具节点」。

- 

  信号2：团队多人参与排查，需要操作审计 → 升级为「Spectre」或「LangGraph + Arthas节点」。

### 4.3 Arthas使用注意事项

1. 

   `watch`/`trace`/`tt`基于字节码增强，高QPS接口勿长期开启，排查完成后务必执行`quit`退出Arthas。

2. 

   `trace`/`watch`输出极易超过Token限制，Skill中需强制截断（如`| nl | head -20`），避免Token浪费。

3. 

   生产环境禁止使用`redefine`/`tt -p`等热修复命令，除非人工明确确认。

## 附录：arthas-diag Skill模板

```markdown
## Skill: arthas-diag
触发条件: 用户提及"线上慢/CPU高/线程堵/OOM/接口超时"

执行流程:
1. 先执行`ps -ef | grep java`获取Java进程PID，输出PID列表并要求用户确认目标进程（防止attach错进程）。
2. 按症状选择Arthas命令，执行前必须输出「操作意图+预期收益」，等待用户yes/no确认：
   - CPU高 → `thread -n 3`（查看CPU占用最高的3个线程）+ `profiler start/stop`（生成火焰图）
   - 线程堵 → `thread -b`（查找阻塞线程）+ `lock-info`（查看锁持有情况）
   - 接口慢 → `trace 包.类 方法 -n 3`（追踪方法调用链）+ `watch 包.类 方法 '{params,returnObj,throwExp}' -x 2`（观测入参/返回值/异常）
   - OOM → `jmap -histo:live pid`（查看存活对象分布）+ `heapdump /tmp/heap.hprof`（生成堆快照）
3. 所有Arthas会话结束后必须执行`quit`退出，超时5分钟无操作自动kill arthas-boot进程。
4. 绝不直接执行`redefine`/`tt -p`等热修复命令，除非用户显式要求。
5. 若检测到Java21虚拟线程（`thread`输出含`carrier`前缀），需关联虚拟线程调度器，定位上层业务线程。

输出规范:
诊断结论需包含「现象描述→根因定位→修复建议」三部分，禁止仅输出原始Arthas日志。
```