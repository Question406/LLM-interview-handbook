---
id: drustz-20afe9b3f3985ea555
section: mlsd
order: 157
level: A
title: 18 · Case：设计大规模分布式推理系统 · 11. 面试前一页速记
quick: 作者文档章节 · 18 · Case：设计大规模分布式推理系统 · 11. 面试前一页速记
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
## 11. 面试前一页速记

**第一句**：先分叉——在线（p99 / goodput）vs 离线（&#36;/M token）。目标函数相反，架构不同。

**物理地基**：prefill = compute-bound；decode = memory-bound。70B/8×H100 decode step 下限 = 140 GB ÷ 26.8 TB/s = **5.2 ms**，与 batch 无关 → batching 近乎免费的throughput。

**KV 公式**：`2 × layers × kv_heads × head_dim × dtype_bytes` per token。**70B GQA = 320 KiB/token；8B = 128 KiB；同规模 MHA = 2.5 MiB（8 倍）。**

**交叉点**：当 `并发 × 长度 × KV/token > 权重字节` 时，KV 读超过权重读，batching 的边际收益开始递减（70B @ 8k 约在并发 53）。

**在线四件套**：continuous batching（收益来自长度方差）／PagedAttention（碎片 60–80% → <4%）／chunked prefill（防 TPOT 尖刺）／PD 分离（先算 KV 传输：640 MB / 13 ms）。

**speculative decoding**：用算力换带宽。**小 batch 赚、大 batch 亏**。分布等价（rejection sampling）。

**并行顺序**：能单卡就 DP 多副本 → 节点内 TP（取放得下的最小度）→ 跨节点 PP（throughput）。PP 在 decode 有气泡。

**冷启动 2–5 分钟** → 不能靠扩容应对分钟级尖峰 → 预热池 + 按队列深度 + 滞回 + 准入控制降级。

**离线三件套**：① 16 条探测筛选，盈亏平衡 = 16/128 = **12.5% 丢弃率**；② **AIMD**（+1 / ×0.5，加 jitter），**必须区分容量类失败与样本类失败**；③ 检查点窗口 **W ≈ 0.1 × MTBP**。

**流水线**：每阶段独立 job + 数据集做边界（理由 = 重跑成本，不是优雅）。必须流式则用有界队列，**绝不用无界队列**。

**成本**：`$/M = (GPU$/hr × N) / (tok/s × 3600) × 1e6`。70B/8×H100 ≈ **&#36;0.7/M output**。input 比 output 便宜约 3×（低并发时更多），API 定价差 3–5×。**自建 vs API 是利用率问题。** 批量 API 打 5 折（1h 典型 / 24h 上限）就是延迟的市场定价。

**监控红线**：p99 + **排队时间单独拆**；抢占/重算率；KV 利用率；**finish_reason 分布**；goodput。

**两个骗人的指标**：nvidia-smi 利用率（只报有没有 kernel）、平均延迟（ρ=0.9 → 排队 9×）。

**必背句**：在线系统里，你为峰值买单却按均值收益；离线系统没有峰值，所以它的正解恰是在线的禁忌。

**诚实边界**：没有在线 serving 的 oncall 经验，能推演不能复盘；离线批量是我的主场。

---

---

来源：[DrustZ / Mingrui Zhang · ml_sys_prep/18_case_distributed_inference.md](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/ml_sys_prep/18_case_distributed_inference.md)。作者整理资料；许可和第三方来源范围见阅读指南。
