---
id: drustz-ddddac8b5a4097aed1
section: mlsd
order: 152
level: A
title: 18 · Case：设计大规模分布式推理系统 · 6. 可靠性：抢占、恢复、幂等 ⭐⭐⭐
quick: 作者文档章节 · 18 · Case：设计大规模分布式推理系统 · 6. 可靠性：抢占、恢复、幂等 ⭐⭐⭐
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
## 6. 可靠性：抢占、恢复、幂等 ⭐⭐⭐

### 6.1 失败分类学（先分类，再谈处理）

| 失败类型 | 频率 | 是容量信号吗 | 处理 |
|---|---|---|---|
| **被抢占**（更高优先级 job 来了） | 共享池里常态 | 是 | 优雅退出 + 检查点 + 重新排队 |
| **OOM** | 自己作的 | 是 | 降并发（AIMD 乘性减）+ 查是不是有超长样本 |
| **引擎崩溃 / CUDA error** | 偶发 | 否 | 重启 worker，在途工作重新入队 |
| **Poison pill**（单条样本必崩） | 稀有但致命 | **否** | 计数，2 次后隔离到 dead-letter |
| **瞬时网络 / 对象存储 5xx** | 常见 | 否 | 指数退避 + jitter 重试 |
| **输出解析失败**（JSON 不合法等） | 常见 | 否 | 有限次重试，仍失败进 dead-letter |
| **静默截断**（撞 max_tokens） | **常见且最危险** | 否 | 见 §9 |

**核心原则**：**容量类失败才触发退避；样本类失败只能隔离，不能退避。** 混淆这两类是自适应并发框架最常见的实现 bug（§4.3 已说）。

### 6.2 检查点粒度：一个可以算的取舍

太细 → 写放大（几百万个小文件，对象存储 LIST 慢到无法续跑）。太粗 → 抢占时丢大量工作。

```text
浪费比例 ≈ (检查点窗口 W / 2) / 抢占平均间隔 MTBP
```



要把浪费控制在 5% 以内 → **W ≈ 0.1 × MTBP**。MTBP 40 分钟 → 每 4 分钟落一次盘。

实操上：**按分片写**，一个分片约 5k–10k 个样本或 1–5 分钟的工作量，append-only 写入，写完落一个 manifest 记录该分片包含的 id 范围。续跑时只读 manifest（几千个），不 LIST 几百万个文件。

### 6.3 idempotency与"resume 不可能逐位复现"

- **至少一次投递**：一条样本可能被执行两次（lease 到期、worker 假死后又活了）。写入时按 `sample_id` 去重，后写覆盖先写。
- **诚实的一条**：即使 `temperature=0` + 固定 seed，**continuous batching 下的输出也不是逐位可复现的**——batch 组成变化会改变 kernel 选择和归约顺序，浮点结果在最低位不同，偶尔就翻转一个 token。（社区已有专门讨论批不变性 kernel 的工作。）

  **推论很重要**：resume 的正确性**不能靠"重跑一遍结果一样"来验证**，只能靠 **id 覆盖率**验证——work list 里的每个 id 恰好有一条结果，就算完成。如果你的验收逻辑写成了输出比对，它会一直报假警。

- **优雅退出**：SIGTERM → 停止接新工作 → 让在途请求跑完（或到 grace period 上限就放弃）→ 落盘 → 退出。抢占系统给的 grace period 通常 30–120 秒，**在途请求的最长耗时必须小于它**，否则每次抢占都要丢一批——这反过来约束了 `max_tokens` 的设定。

---

---

来源：[DrustZ / Mingrui Zhang · ml_sys_prep/18_case_distributed_inference.md](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/ml_sys_prep/18_case_distributed_inference.md)。作者整理资料；许可和第三方来源范围见阅读指南。
