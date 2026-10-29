---
id: drustz-efd145c31ce97b9ccd
section: mlsd
order: 156
level: A
title: 18 · Case：设计大规模分布式推理系统 · 10. 10 分钟口述稿
quick: 作者文档章节 · 18 · Case：设计大规模分布式推理系统 · 10. 10 分钟口述稿
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
## 10. 10 分钟口述稿

> 我先确认一件事：这是**在线低延迟 serving** 还是**离线batch inference**？这两个的目标函数是相反的——在线优化 SLO 内的 goodput，离线优化每百万 token 的成本，架构选择基本没有重合。我先说这个分叉，再按你想听的那侧展开。
>
> **在线**这侧，一切从一个物理事实出发：prefill 是 compute-bound、decode 是 memory-bandwidth-bound。70B fp16 权重 140 GB，8 张 H100 聚合带宽 26.8 TB/s，所以 decode 一步的下限是 5.2 毫秒，和 batch 多大无关——这就是为什么 batching 几乎是免费的throughput。做法上：continuous batching 做迭代级调度、PagedAttention 把 KV 分块管理消除碎片、chunked prefill 防止长 prompt 卡住 decode。如果 TTFT 和 TPOT 的 SLO 冲突严重，再考虑 prefill/decode 分池，但要先算 KV 传输成本——2000 token 的 prompt 是 640 MB，400G 网络上 13 毫秒，TTFT 预算几百毫秒才划算。speculative decoding我会在小并发场景用，大 batch 下它抢算力反而降throughput。
>
> 指标上我坚持三件事：**报 p99 不报均值**、**排队时间单独度量**、**用 goodput 不用 raw throughput**。排队必须拆出来，因为它区分了"该加卡"和"该修调度器"。而且利用率 0.9 时排队等待就是服务时间的 9 倍，所以在线系统的稳态利用率只能做到 60–70%，那 30% 是买延迟的钱。
>
> **这里我要标一个边界：我没有在线 serving 的 oncall 经验**，机制和容量估算我能推，真实事故复盘我讲不了。我真正做过的是另一侧。
>
> **离线批量**是我在 Reflection 的主责。我们为 RL 合成 math/STEM 数据，跑在共享 GPU 池上，被其他团队抢占是常态。三个设计点：
>
> 第一，**推理预算的分配**。RL rollout 正式跑是每题 128 条，但全对全错的题在 GRPO 里 advantage 为零、没有梯度。所以我们先用 16 条探测可解率，全对全错的直接丢。盈亏平衡点可以算：16 除以 128 是 12.5%，只要丢弃率超过 12.5% 就净赚，我们实际在 40% 量级。这和 DAPO 的 dynamic sampling 是一个思想。要注意 16 条的统计精度有限——全对时可解率的 95% 下界只有 0.83，所以我们其实在丢一部分有信号的题，这是显式取舍不是免费的。
>
> 第二，**自适应并发**。共享池里可用容量是别人的函数，固定并发不是欠打就是持续 OOM。我们做了 TCP 式的 AIMD：成功就加一、失败就砍半，加 jitter 防羊群。最关键的实现细节是**必须区分容量类失败和样本类失败**——429 和抢占要退避，但单条样本 prompt 超长导致的失败不能退避，否则一个 poison pill 就能把并发压到 1、整个 job 卡死不报错。这是我们踩过的坑。
>
> 第三，**抢占恢复**。检查点粒度有公式：浪费比例约等于窗口的一半除以抢占平均间隔，要控制在 5% 就取 MTBP 的十分之一。样本 id 按内容加配置哈希，写入按 id 幂等，续跑靠 id 差集。有一点要诚实：continuous batching 下即使 temperature=0 输出也不是逐位可复现的，因为 batch 组成会改变归约顺序——所以 resume 的验收标准只能是 **id 覆盖率**，不能是输出比对。
>
> **成本**上我会算给面试官看：8 卡 H100 跑 70B，KV 预算 436 GB、每 token 320 KB，能装 133 万 token，4k 上下文下并发约 330，实际throughput 6–9k tok/s，二十美元一小时算下来大约 0.7 美元每百万输出 token。这个数和 API 报价同量级——**所以自建能不能赢是利用率问题不是单价问题**：利用率 20% 的话自建是 API 的五倍贵。
>
> 最后是**最容易坏的地方**：batch 调到 OOM 边缘会 thrashing 式非线性崩塌，不是线性变慢；离线最阴险的是撞 max_tokens 的静默截断，格式检查还能通过，一批垃圾就进训练集了——所以 finish_reason 的分布必须监控。还有一个反直觉的：nvidia-smi 的 GPU 利用率是骗人的，它只报有没有 kernel 在跑，要看 MFU 或者 tokens/s per GPU。

---

---

来源：[DrustZ / Mingrui Zhang · ml_sys_prep/18_case_distributed_inference.md](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/ml_sys_prep/18_case_distributed_inference.md)。作者整理资料；许可和第三方来源范围见阅读指南。
