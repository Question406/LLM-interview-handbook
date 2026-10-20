---
id: kuaishou-tool-chain-latency
section: systems
order: 142
level: A
title: 快手：三工具高 QPS 链路延迟高，从哪些维度优化？
quick: "先通过 trace 分清模型计算、工具请求、串行等待和排队各花多久。无依赖的工具并行调用，缓存幂等读，精简 schema 和上下文，简单任务路由小模型。为工具设置超时与熔断，再用压测检查收益。"
tags:
  - Kuaishou
  - Latency
  - Tool Calling
realInterview: true
status: published
format: markdown
updatedAt: 2026-08-21
sources:
  - title: 快手大模型LLM二面分享-日常实习
    url: https://www.nowcoder.com/feed/main/detail/058475a3d9204493bc145510c72e10f1
    type: candidate-first-hand
  - title: vLLM 文档：性能与调度
    url: https://docs.vllm.ai/en/latest/performance/
    type: primary
---

## 真题记录

- 公司：快手
- 团队 / 岗位：大模型 LLM 日常实习
- 届别 / 流程：日常实习；二面
- 面试时间：原帖未披露；帖子发布于 2026-03-31
- 来源类型与可信度：牛客候选人原帖，B
- 原始措辞：**“假如Agent推理链路包含3个工具且请求频率极高，导致系统整体延迟较高，你会从哪些维度进行优化？”**

常见误区是：先换更大模型，或把三个工具默认串成「思考→调1→调2→调3」。高 QPS 下延迟是 排队 + 串行气泡 + 工具 RTT + 模型 prefill/decode 的和。我先按 trace 拆 p50/p95：LLM、每个工具、是否串行、队列等待。没有数据依赖的工具应 fan-out；有依赖才串行，并缓存第一跳的热点读。本手册超时空返回卡负责「失败怎么对用户说」，本题负责「怎么别超时」。先画火焰图再改，不要先加卡。

## 拆时间线：串行还是排队

三工具若无数据依赖，一次 function call 并行打出，实际耗时近似 $\max(t_1,t_2,t_3)$ 而不是相加。有依赖（先搜商品再查库存再算券）只能串，但第一跳结果可缓存，后续请求少打。高 QPS 时真正打满的往往是 队列：vLLM/SGLang 的 waiting queue、工具线程池、下游限流。admission control 比盲目加 replica 更先：超容量直接 429 / 降级，避免重试风暴把 p99 推到超时。连接池、HTTP/2、批量读（能 merge 的库存查询 merge）是系统侧同一层。

产品侧：非关键工具改异步（返回后再补「券已算好」），预取下一轮可能用的工具。不要让「三个工具都必须成功」成为同步屏障。

## 模型侧：减少 token 和轮次，复用前缀

缩短工具 JSON schema，只暴露本轮候选工具，不要把 30 个函数描述塞进每次 输入预填充（prefill，即处理输入并建立缓存）。公共 system + schema 走 prefix cache，key 带 schema 版本。简单请求路由小模型或纯检索，复杂再上大模型。投机解码对短工具参数有时有效，对长 思维链（CoT，即分步推理过程） 不一定。KV 占用随并发和上下文涨：限制 max 输入、会话只留近轮。structured decoding 保证参数可解析，减少「调错再重试」的第二轮 LLM。Serving 用 continuous batching 吃高 QPS；静态 batch 会被最长工具参数生成拖死。

## 超时、熔断与验收

每个工具独立 timeout + 熔断：慢依赖不能占满线程池。超时后降级（缓存、默认、跳过非关键），而不是无限重试。重试必须 jitter，否则同步失败会放大 QPS。验收：p95/p99、错误率、限流比、单工具 RTT、成本。按目标 QPS 压测，切片「只 LLM / 只工具 / 整链」。优化顺序：并行与缓存 → 减 schema/上下文 → 超时熔断 → 最后才加模型规格。换更大模型通常让排队更长。

## 追问

- **三个工具一定要串行吗？** 无数据依赖应并行，实际耗时近似取最大而不是相加。有依赖才串，并缓存第一跳热点读。默认串成「思考→调1→调2→调3」是这题最常见的坑，高 QPS 下气泡会被放大。
- **为什么先不换大模型？** 大模型加长 prefill/decode 和 KV，高 QPS 下 waiting queue 更长。先减等待、并行、缓存、超时熔断，最后才加规格。换大模型常常让 p99 更差。
- **prefix cache 能省什么？** 公共系统提示和工具 JSON schema 的 prefill。schema 或候选工具集一变必须换 key，否则会复用错误前缀。只暴露本轮候选工具，不要每次塞 30 个函数描述。
- **重试为什么危险？** 超时瞬间同步重试会把下游 QPS 翻倍，熔断形同虚设。预算按用户请求计并加 jitter。慢依赖要独立 timeout，不能让一个工具占满线程池。
- **怎么证明优化有效？** 同脚本、同数据压测，分别报 LLM、每个工具、排队三段的 p95/p99、错误率和限流比。不要一个平均 RT。切片「只 LLM / 只工具 / 整链」才能指对组件。
