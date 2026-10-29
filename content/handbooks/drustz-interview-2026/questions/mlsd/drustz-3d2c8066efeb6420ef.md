---
id: drustz-3d2c8066efeb6420ef
section: mlsd
order: 155
level: A
title: 18 · Case：设计大规模分布式推理系统 · 9. 常见失败模式：这个系统最容易在哪里坏 ⭐⭐⭐
quick: 作者文档章节 · 18 · Case：设计大规模分布式推理系统 · 9. 常见失败模式：这个系统最容易在哪里坏 ⭐⭐⭐
companies: []
tags:
  - DrustZ
  - 作者文档章节
  - ML System Design · 全流程
realInterview: false
status: published
format: markdown
updatedAt: '2026-10-28'
sources:
  - title: DrustZ / Mingrui Zhang · pinned source
    url: >-
      https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/ml_sys_prep/18_case_distributed_inference.md
    type: primary
---
## 9. 常见失败模式：这个系统最容易在哪里坏 ⭐⭐⭐

| # | 失败模式 | 机制 | 防御 |
|---|---|---|---|
| 1 | **batch 调到 OOM 边缘** | 平时正常，来一个长 prompt → KV 耗尽 → 引擎抢占 + 重算 → throughput**非线性崩塌**（thrashing），不是线性下降 | 留 10–20% 余量（`gpu_memory_utilization` 0.85–0.9 而不是 0.98）；监控抢占率而不是等 p99 报警 |
| 2 | **只看均值延迟** | 掩盖排队。ρ=0.9 时排队 = 9× 服务时间 | 报 p99 + **单独报排队时间** |
| 3 | **长 prompt 造成队头阻塞** | 一个 30k token 的 prefill 占住一整个 step，所有 decode 中的序列 TPOT 尖刺 | chunked prefill；或长请求单独分池 |
| 4 | **重试风暴** | 部分故障 → 客户端重试 → 负载在容量下降时反而翻倍 → 全面雪崩 | 重试预算（重试量 ≤ 总流量 10%）、断路器、指数退避 + **jitter**（没有 jitter 会同步成脉冲） |
| 5 | **扩缩容震荡** | 冷启动 3 分钟 > 扩容决策周期 → 扩了没起来又缩 | 按队列深度 + 滞回 + 预热池；短期尖峰用准入控制而不是扩容 |
| 6 | **静默截断（离线，最阴险）** | 撞 `max_tokens` → 输出被切断 → 格式检查可能仍通过（比如 JSON 恰好闭合）→ **一批垃圾数据静默进入训练集** | **必须监控 `finish_reason` 分布**；`length` 的比例突然上升就报警；对截断样本单独标记而不是丢进正常池 |
| 7 | **Poison pill 活锁** | 一条 200k token 的文档 → OOM → 整个 in-flight batch 的工作丢失 → 重试 → 再 OOM，无限循环 | 入队前按 token 数预过滤；硬 `max_model_len`；**每样本失败计数，2 次后隔离到 dead-letter** |
| 8 | **checkpoint 粒度太粗** | 跑到 95% 被抢占，全部重来 | §6.2 的公式：W ≈ 0.1 × MTBP |
| 9 | **prefix cache 被一个动态 token 打死** | system prompt 里的时间戳 / UUID / 未排序 JSON | 监控 cache hit rate；把动态内容全部移到前缀之后 |
| 10 | **AIMD 把样本错误当容量错误** | 一个 poison pill 让并发一路降到 1，job 卡死但不报错 | 严格区分两类错误（§4.3） |
| 11 | **探测与正式跑的sampling参数不一致** | 16 条探测用了不同 temperature → 可解率估计有偏 → 筛选逻辑失效，丢错样本 | 探测与正式跑共用同一份 config 对象，禁止分别配置 |
| 12 | **judge/verifier 阶段自身不一致** | LRM-as-judge 在不同题目上对同一标准判得不一致 → 下游筛选噪声大 | 固定 rubric + 抽样人工calibration；对同一样本多判几次看方差；judge 的一致性本身要当作监控指标 |

---

---

来源：[DrustZ / Mingrui Zhang · ml_sys_prep/18_case_distributed_inference.md](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/ml_sys_prep/18_case_distributed_inference.md)。作者整理资料；许可和第三方来源范围见阅读指南。
