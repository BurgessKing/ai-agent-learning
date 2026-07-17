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

## 第3周：Java 核心深化 + Agent 深度概念

> ⭐ **本周重点**：面试中 Java 多线程/并发/事务是基础分，Agent 深度概念是加分项。

### Day 15-16：Java 多线程与高并发

（详细题目与答案见 [附录A](#附录ajava-多线程高并发事务-经典题目与答案)）

**学习路线**：

```
Java 并发知识地图:

基础                         进阶                          实战
Thread/Runnable    →    synchronized/volatile   →   线程池 ThreadPoolExecutor
wait/notify        →    Lock/AQS/CAS            →    CompletableFuture
                          ConcurrentHashMap     →    生产者-消费者
                          CountDownLatch        →    限流器实现
                          CyclicBarrier         →    并发缓存
                          Semaphore             →    异步任务编排
```

**Day 15-16 学习清单**：
1. 手写线程池参数含义（corePoolSize, maxPoolSize, keepAliveTime, workQueue, RejectedExecutionHandler）
2. synchronized 底层原理（对象头、Monitor、锁升级：偏向锁→轻量锁→重量锁）
3. volatile 的可见性和禁止指令重排
4. CAS 原理 + ABA 问题
5. AQS (AbstractQueuedSynchronizer) 框架理解
6. ConcurrentHashMap JDK7 vs JDK8 实现差异
7. CompletableFuture 异步编排

**练习题**（至少手写 5 道，答案见附录A）：
- 手写 DCL（双重检查锁定）单例
- 手写生产者-消费者（wait/notify + BlockingQueue 两版）
- 手写一个简单线程池
- 三个线程交替打印 ABC
- CompletableFuture 实现并行查询 + 聚合

---

### Day 17-18：Java 事务 + Spring 并发

**核心必会**：

```java
// 1. 事务传播行为 — 面试必问
@Transactional(propagation = Propagation.REQUIRED)      // 默认：有则加入，无则新建
@Transactional(propagation = Propagation.REQUIRES_NEW)  // 总是新建事务，挂起当前
@Transactional(propagation = Propagation.NESTED)         // 嵌套事务（需要 Savepoint）
@Transactional(propagation = Propagation.MANDATORY)      // 必须在已有事务中
@Transactional(propagation = Propagation.NEVER)          // 必须在非事务中

// 2. 隔离级别 — 解决脏读/不可重复读/幻读
@Transactional(isolation = Isolation.READ_COMMITTED)      // 默认
@Transactional(isolation = Isolation.REPEATABLE_READ)     // MySQL 默认
@Transactional(isolation = Isolation.SERIALIZABLE)        // 串行化

// 3. 事务失效的8种场景（面试高频！）
// ① 非 public 方法
// ② 同类方法调用（this.method() 不走代理）
// ③ 异常被 catch 未抛出
// ④ 非 RuntimeException（默认不回滚 checked exception）
// ⑤ 数据库引擎不支持（MyISAM）
// ⑥ 多线程中调用
// ⑦ final/static 方法
// ⑧ @Transactional 注解的类未被 Spring 管理
```

**并发场景下的事务问题**：

```java
/**
 * 场景：班车调度中的并发问题
 * 
 * 问题：多个调度员同时分配同一辆车给不同线路
 * 解决：乐观锁 + 分布式锁
 */

// 方案1: 乐观锁（小并发场景）
@Transactional
public boolean assignVehicle(String vehicleId, String routeId) {
    // UPDATE vehicle SET route_id = ?, version = version + 1
    // WHERE id = ? AND version = ? AND status = 'IDLE'
    int rows = vehicleMapper.assignWithOptimisticLock(vehicleId, routeId, currentVersion);
    if (rows == 0) {
        throw new ConcurrentModificationException("车辆已被分配");
    }
    return true;
}

// 方案2: 分布式锁（高并发场景）
@Transactional
public boolean assignVehicleDistributed(String vehicleId, String routeId) {
    String lockKey = "vehicle:lock:" + vehicleId;
    boolean locked = redisTemplate.opsForValue()
        .setIfAbsent(lockKey, "1", Duration.ofSeconds(30));
    if (!locked) {
        throw new ConcurrentModificationException("车辆正在被调度");
    }
    try {
        // 分配逻辑
        vehicleMapper.assign(vehicleId, routeId);
    } finally {
        redisTemplate.delete(lockKey);  // 注意：生产用 Redisson 避免误删
    }
    return true;
}
```

**完整题目与答案见 [附录A](#附录ajava-多线程高并发事务-经典题目与答案)**

---

### Day 19-20：Agent 深度概念

详细内容见 [附录B](#附录bagent-深度概念plan-and-execute上下文工程模型调优)

**学习清单**：
1. **Plan-and-Execute 深入** — 与 ReAct 的混合使用策略
2. **上下文工程四个层次** — 从朴素 RAG 到多源融合
3. **模型调优全景** — Fine-tuning vs RAG vs Prompt Engineering 的选择决策树
4. **Multi-Agent 协作协议** — 消息传递、冲突解决、层级调度

**面试加分句**：
> "模型调优不是非此即彼。我们通常先 Prompt Engineering，不够加 RAG，还不够做 Fine-tuning。判断标准是——数据是否频繁变化（是→RAG），任务是否通用（是→Fine-tuning），成本预算多少。"

### Day 21：综合项目（保留 v1.0 内容，略）

---

## 附录A：Java 多线程/高并发/事务 经典题目与答案

### A1：Java 多线程基础

#### 题目1：手写 DCL 单例 + 解释为什么用 volatile

```java
/**
 * DCL (Double-Checked Locking) 单例
 * 
 * 关键点：
 * 1. volatile 防止指令重排
 * 2. 两次 null 检查的原因
 * 3. synchronized 加在类对象上
 */
public class DCLSingleton {
    
    // volatile 关键作用：
    // 1. 保证可见性 — 一个线程修改，其他线程立即可见
    // 2. 禁止指令重排 — 防止返回未初始化完成的对象
    // 
    // 不加 volatile 的问题：
    // instance = new DCLSingleton() 分三步：
    //   ① 分配内存空间
    //   ② 初始化对象
    //   ③ instance 指向内存地址
    // JVM 可能重排序为 ①→③→②
    // 此时另一个线程在第一次 null 检查时发现 instance != null
    // 但对象还没初始化完成，返回了半成品对象！
    private static volatile DCLSingleton instance;
    
    private DCLSingleton() {
        // 防止反射破坏
        if (instance != null) {
            throw new RuntimeException("单例已被创建");
        }
    }
    
    public static DCLSingleton getInstance() {
        // 第一次检查：避免不必要的同步（性能优化）
        if (instance == null) {
            // 类对象锁
            synchronized (DCLSingleton.class) {
                // 第二次检查：防止多线程同时通过第一次检查
                if (instance == null) {
                    instance = new DCLSingleton();
                }
            }
        }
        return instance;
    }
    
    // 防止反序列化破坏单例
    private Object readResolve() {
        return getInstance();
    }
}
```

#### 题目2：手写生产者-消费者（两种实现）

```java
/**
 * 版本1: wait/notify 实现
 * 
 * 面试要点：
 * 1. while 而不是 if 判断条件（防止虚假唤醒）
 * 2. notifyAll 而不是 notify（防止信号丢失）
 */
class ProducerConsumer1 {
    private final LinkedList<Integer> buffer = new LinkedList<>();
    private final int capacity = 10;
    
    public void produce() throws InterruptedException {
        int value = 0;
        while (true) {
            synchronized (this) {
                // while 判断：被唤醒后重新检查条件
                while (buffer.size() == capacity) {
                    wait();  // 释放锁，等待消费
                }
                System.out.println("生产: " + value);
                buffer.add(value++);
                notifyAll();  // 唤醒所有等待线程
                Thread.sleep(500);
            }
        }
    }
    
    public void consume() throws InterruptedException {
        while (true) {
            synchronized (this) {
                while (buffer.isEmpty()) {
                    wait();
                }
                int value = buffer.removeFirst();
                System.out.println("消费: " + value);
                notifyAll();
                Thread.sleep(1000);
            }
        }
    }
}

/**
 * 版本2: BlockingQueue 实现（推荐）
 * 
 * BlockingQueue 内部已经实现了线程安全的 put/take
 * put: 队列满时阻塞
 * take: 队列空时阻塞
 */
class ProducerConsumer2 {
    private final BlockingQueue<Integer> queue = new LinkedBlockingQueue<>(10);
    
    public void produce() throws InterruptedException {
        int value = 0;
        while (true) {
            queue.put(value);  // 阻塞直到有空位
            System.out.println("生产: " + value++);
            Thread.sleep(500);
        }
    }
    
    public void consume() throws InterruptedException {
        while (true) {
            int value = queue.take();  // 阻塞直到有数据
            System.out.println("消费: " + value);
            Thread.sleep(1000);
        }
    }
}
```

#### 题目3：三个线程交替打印 ABC（N 轮）

```java
/**
 * 要求：线程1打印A，线程2打印B，线程3打印C，交替打印N轮
 * 输出: ABCABCABC...
 * 
 * 考察：线程通信、状态控制
 */

// 方案1: synchronized + wait/notify + 状态变量
class PrintABC1 {
    private int state = 0;  // 0=A, 1=B, 2=C
    private final int rounds;
    
    public PrintABC1(int rounds) { this.rounds = rounds; }
    
    public void printA() {
        synchronized (this) {
            for (int i = 0; i < rounds; i++) {
                while (state != 0) {
                    try { wait(); } catch (InterruptedException e) {}
                }
                System.out.print("A");
                state = 1;
                notifyAll();
            }
        }
    }
    
    public void printB() {
        synchronized (this) {
            for (int i = 0; i < rounds; i++) {
                while (state != 1) {
                    try { wait(); } catch (InterruptedException e) {}
                }
                System.out.print("B");
                state = 2;
                notifyAll();
            }
        }
    }
    
    public void printC() {
        synchronized (this) {
            for (int i = 0; i < rounds; i++) {
                while (state != 2) {
                    try { wait(); } catch (InterruptedException e) {}
                }
                System.out.print("C");
                state = 0;
                notifyAll();
            }
        }
    }
}

// 方案2: Lock + Condition（更精细控制）
class PrintABC2 {
    private final Lock lock = new ReentrantLock();
    private final Condition conditionA = lock.newCondition();
    private final Condition conditionB = lock.newCondition();
    private final Condition conditionC = lock.newCondition();
    private int state = 0;
    private final int rounds;
    
    public PrintABC2(int rounds) { this.rounds = rounds; }
    
    public void printA() throws InterruptedException {
        lock.lock();
        try {
            for (int i = 0; i < rounds; i++) {
                while (state != 0) conditionA.await();
                System.out.print("A");
                state = 1;
                conditionB.signal();
            }
        } finally { lock.unlock(); }
    }
    
    // printB/printC 类似...

// 方案3: Semaphore（最简洁）
class PrintABC3 {
    private final Semaphore semA = new Semaphore(1);
    private final Semaphore semB = new Semaphore(0);
    private final Semaphore semC = new Semaphore(0);
    private final int rounds;
    
    public PrintABC3(int rounds) { this.rounds = rounds; }
    
    public void printA() throws InterruptedException {
        for (int i = 0; i < rounds; i++) {
            semA.acquire();  // 等待A的许可
            System.out.print("A");
            semB.release();  // 释放B的许可
        }
    }
    
    public void printB() throws InterruptedException {
        for (int i = 0; i < rounds; i++) {
            semB.acquire();
            System.out.print("B");
            semC.release();
        }
    }
    
    public void printC() throws InterruptedException {
        for (int i = 0; i < rounds; i++) {
            semC.acquire();
            System.out.print("C");
            semA.release();
        }
    }
}
```

### A2：Java 并发容器与工具

#### 题目4：ConcurrentHashMap 原理 + 为什么线程安全

```
JDK7 ConcurrentHashMap: Segment 分段锁
┌─────────────────────────────────┐
│ ConcurrentHashMap                │
│  ┌──────────┐ ┌──────────┐     │
│  │Segment 0 │ │Segment 1 │ ... │  ← 默认16个Segment
│  │ ┌──────┐ │ │ ┌──────┐ │     │    每个Segment独立加锁
│  │ │Hash  │ │ │ │Hash  │ │     │    并发度=Segment数量
│  │ │Entry │ │ │ │Entry │ │     │
│  │ └──────┘ │ │ └──────┘ │     │
│  └──────────┘ └──────────┘     │
└─────────────────────────────────┘

JDK8 ConcurrentHashMap: CAS + synchronized（细粒度）
- 抛弃了 Segment，改用 Node 数组 + CAS + synchronized
- 锁粒度从 Segment 降到单个桶（bin）的 head 节点
- put 时：
  1. 数组为空 → CAS 初始化
  2. 桶为空 → CAS 插入（无锁）
  3. 桶不为空 → synchronized(head)（只锁一个桶）
  4. 链表长度≥8 → 转为红黑树（加速查询）
```

#### 题目5：线程池核心参数 + 拒绝策略

```java
/**
 * 线程池参数理解 — 面试必问
 * 
 * 核心参数:
 * corePoolSize:    核心线程数（常驻线程）
 * maxPoolSize:     最大线程数
 * keepAliveTime:   非核心线程空闲存活时间
 * workQueue:       任务队列
 * RejectedExecutionHandler: 拒绝策略
 * 
 * 执行流程:
 * 1. 当前线程 < corePoolSize → 新建线程
 * 2. 当前线程 >= corePoolSize → 放入 workQueue
 * 3. workQueue 满了 → 新建线程（不超过 maxPoolSize）
 * 4. 达到 maxPoolSize → 执行拒绝策略
 */

// 实际业务中的线程池配置
ThreadPoolExecutor executor = new ThreadPoolExecutor(
    10,                        // 核心线程: 假设日常并发10个任务
    20,                        // 最大线程: 峰值扩容到20
    60L, TimeUnit.SECONDS,     // 空闲60秒回收非核心线程
    new LinkedBlockingQueue<>(100),  // 队列100个任务缓冲
    new ThreadPoolExecutor.CallerRunsPolicy()  // 拒绝策略: 调用者线程执行
    // 其他策略:
    // AbortPolicy:     抛异常（默认）
    // DiscardPolicy:   直接丢弃
    // DiscardOldestPolicy: 丢弃最老的
    // CallerRunsPolicy: 调用者线程执行（推荐，提供背压）
);

// 面试加分：你知道怎么算线程数
// CPU密集型: N+1 (N=CPU核数)
// IO密集型:  2N (因为有大量等待时间)
int cpuCores = Runtime.getRuntime().availableProcessors();
ThreadPoolExecutor cpuPool = new ThreadPoolExecutor(
    cpuCores + 1, cpuCores + 1, 0L, TimeUnit.SECONDS,
    new LinkedBlockingQueue<>()
);
```

#### 题目6：CompletableFuture 实战 — 并发查询多个数据源

```java
/**
 * 场景：散包下单时，需要同时查询：
 * 1. 可用车辆列表
 * 2. 可用司机列表  
 * 3. 历史报价参考
 * 4. 天气信息（影响报价）
 * 
 * 其中天气和历史报价非必须，超时可降级
 */
public class OrderAggregationService {
    
    public OrderContext aggregate(String customerId, OrderRequest request) {
        
        // 并行查询（必须成功的）
        CompletableFuture<List<Vehicle>> vehiclesFuture = 
            CompletableFuture.supplyAsync(() -> 
                vehicleService.getAvailableVehicles(request.getDate(), request.getType()));
        
        CompletableFuture<List<Driver>> driversFuture = 
            CompletableFuture.supplyAsync(() -> 
                driverService.getAvailableDrivers(request.getDate()));
        
        // 可选查询（带超时降级）
        CompletableFuture<List<PriceHistory>> historyFuture = 
            CompletableFuture.supplyAsync(() -> 
                priceService.getHistory(customerId))
                .orTimeout(2, TimeUnit.SECONDS)  // 2秒超时
                .exceptionally(ex -> {
                    log.warn("历史报价查询失败，使用默认值", ex);
                    return Collections.emptyList();
                });
        
        CompletableFuture<WeatherInfo> weatherFuture = 
            CompletableFuture.supplyAsync(() -> 
                weatherService.getForecast(request.getDate()))
                .orTimeout(3, TimeUnit.SECONDS)
                .exceptionally(ex -> null);
        
        // 组合所有结果
        CompletableFuture<OrderContext> resultFuture = CompletableFuture
            .allOf(vehiclesFuture, driversFuture, historyFuture, weatherFuture)
            .thenApply(v -> {
                try {
                    return OrderContext.builder()
                        .vehicles(vehiclesFuture.get())
                        .drivers(driversFuture.get())
                        .priceHistory(historyFuture.get())
                        .weather(weatherFuture.get())
                        .build();
                } catch (Exception e) {
                    throw new RuntimeException("聚合失败", e);
                }
            });
        
        return resultFuture.join();  // 阻塞等待全部完成
    }
}
```

### A3：事务

#### 题目7：事务传播行为 — 经典场景分析

```java
/**
 * 场景：散包下单（order）+ 费用预估（quote） 
 * 
 * 问题：
 * - 订单创建失败时，报价记录也要回滚吗？
 * - 报价生成失败时，订单要回滚吗？
 */

@Service
public class OrderService {
    
    @Autowired
    private QuoteService quoteService;
    
    /**
     * REQUIRED: 如果报价失败，订单也会回滚
     * 适用于：订单和报价强一致（如自动报价）
     */
    @Transactional(propagation = Propagation.REQUIRED)
    public Order createOrderWithQuote(OrderRequest request) {
        Order order = orderMapper.insert(toEntity(request));
        Quote quote = quoteService.generateQuote(order.getId());  // 失败则回滚订单
        order.setQuoteId(quote.getId());
        return order;
    }
}

@Service
public class QuoteService {
    
    /**
     * REQUIRES_NEW: 报价记录独立提交
     * 适用于：报价失败不能影响订单创建（如人工报价场景）
     */
    @Transactional(propagation = Propagation.REQUIRES_NEW)
    public Quote generateQuote(Long orderId) {
        Quote quote = calculateQuote(orderId);
        quoteMapper.insert(quote);  // 独立提交，不影响外部事务
        return quote;
    }
    
    /**
     * NESTED: 嵌套事务，可以利用 Savepoint 回滚到嵌套点
     * 适用于：报价失败时回滚报价但不回滚订单
     * 
     * 注意：NESTED 需要 JDBC Savepoint 支持（MySQL 支持）
     */
    @Transactional(propagation = Propagation.NESTED)
    public Quote generateQuoteNested(Long orderId) {
        Quote quote = calculateQuote(orderId);
        quoteMapper.insert(quote);
        // 如果这里抛异常，只回滚嵌套事务，外层订单事务继续
        return quote;
    }
}

/**
 * 事务失效场景排查清单：
 * 
 * 1. 数据库引擎: MyISAM 不支持事务 → 检查: SHOW TABLE STATUS LIKE 'orders';
 * 2. 同类方法调用: this.xxx() 不走代理 → 解决: 注入自己或提取到另一个 Service
 * 3. 异常类型: checked Exception 默认不回滚 → 解决: @Transactional(rollbackFor = Exception.class)
 * 4. catch 后未抛出: try { dao.insert() } catch { log.error() } → 解决: catch 后 throw
 * 5. 非 public: protected/private 方法上 @Transactional 无效
 * 6. 多线程: 新线程不在原事务上下文中
 */
```

#### 题目8：分布式事务方案对比

```java
/**
 * 场景：散包下单涉及多个服务
 * - 订单服务: 创建订单
 * - 调度服务: 锁定车辆
 * - 支付服务: 预扣款
 * 
 * 分布式事务方案选型:
 */

// 方案1: 最终一致性 — 本地消息表 + 定时任务（推荐）
// 适用于：对实时性要求不高的场景
@Service
public class OrderServiceWithLocalMsg {
    
    @Transactional
    public void createOrder(OrderRequest request) {
        // 1. 创建订单 + 消息记录（同一个本地事务）
        Order order = orderMapper.insert(toEntity(request));
        OutboxMessage msg = OutboxMessage.builder()
            .topic("order.created")
            .payload(JsonUtil.toJson(order))
            .status("PENDING")
            .build();
        outboxMapper.insert(msg);  // 与订单在同一事务中
    }
    
    // 2. 定时任务轮询发送
    @Scheduled(fixedDelay = 5000)
    public void sendPendingMessages() {
        List<OutboxMessage> pending = outboxMapper.findPending();
        for (OutboxMessage msg : pending) {
            try {
                rocketMQ.send(msg.getTopic(), msg.getPayload());
                outboxMapper.updateStatus(msg.getId(), "SENT");
            } catch (Exception e) {
                // 重试，超过最大次数标记为 FAILED 人工处理
            }
        }
    }
}

// 方案2: Seata AT 模式（强一致性）
// 适用于：需要强一致性的核心交易
@GlobalTransactional  // Seata 全局事务注解
public void createOrderWithSeata(OrderRequest request) {
    orderService.createOrder(request);      // 本地事务1 → 注册到 Seata
    dispatchService.lockVehicle(request);    // 本地事务2 → 注册到 Seata
    paymentService.preDeduct(request);       // 本地事务3 → 注册到 Seata
    // 全部成功 → 全局提交
    // 任一失败 → 全局回滚（Seata 自动 undo）
}

/**
 * 选型建议:
 * - 内部系统、并发不高 → Seata AT（开发简单）
 * - 高并发、跨组织 → 本地消息表 + MQ（最终一致性）
 * - 复杂长流程 → Saga 模式（正向操作 + 补偿操作）
 */
```

---

