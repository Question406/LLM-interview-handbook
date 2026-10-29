---
id: drustz-12be2ef142c7cf5aad
section: mlsd
order: 151
level: A
title: 18 · Case：设计大规模分布式推理系统 · 5. 成本模型：要能在白板上算出数字 ⭐⭐
quick: 作者文档章节 · 18 · Case：设计大规模分布式推理系统 · 5. 成本模型：要能在白板上算出数字 ⭐⭐
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
## 5. 成本模型：要能在白板上算出数字 ⭐⭐

### 5.1 基本公式

```text
$/M output token = (GPU 单价 $/hr × GPU 数) ÷ (输出吞吐 tok/s × 3600) × 1e6
```



**worked example（70B，8×H100，离线批量）**：

| 项 | 值 | 来源 |
|---|---|---|
| 权重 fp16 | 140 GB | 70B × 2 bytes |
| 可用显存（`gpu_memory_utilization=0.9`） | 640 × 0.9 = 576 GB | |
| **KV 预算** | 576 − 140 = **436 GB** | |
| KV/token | 320 KiB | §3.2 表 |
| **可容纳的 KV token 总数** | 436e9 / 327680 ≈ **1.33 M** | |
| 平均序列 4k → **最大并发序列数** | ≈ **330** | |
| decode step：权重读 | 140 GB / 26.8 TB/s = 5.2 ms | |
| decode step：KV 读（KV 池装满即 436 GB） | 436 / 26.8 TB/s = **16.3 ms** | **注意：长上下文下 KV 读超过权重读** |
| step 合计（含 overhead） | ≈ 22 ms | |
| **理论聚合throughput** | 330 / 0.022 ≈ **15 k tok/s** | |
| 实际达成（40–60%） | **6–9 k tok/s** | |
| 成本（8 × $2.5/GPU-hr = $20/hr，按 8k tok/s） | **&#36;0.69 / M output token** | |

**这个例子的三个可讲点**：
1. **KV 读在长上下文下超过权重读**，成为 decode 的主瓶颈。这意味着"batching 是免费throughput"这句话有上限：当 `并发 × 平均长度 × KV/token > 权重字节数` 时（本例约在并发 53 @ 8k 上下文），继续加 batch 的边际throughput就开始递减。**能说出这个交叉点，比背 continuous batching 强得多。**
2. **input token 比 output token 便宜得多**（prefill 是并行的，decode 是串行的）。用本篇自己的数字算：prefill 2000 token 要 88 ms → **≈ 23 k tok/s**，decode 实际 **6–9 k tok/s**，同一套卡上大约 **3 倍**；并发越低差距越大（batch=1 时 decode 只有 190 tok/s，差两个数量级）。主流 API 的输入/输出定价差也在 **3–5 倍**量级（Claude、GPT 系列当前都是 5 倍）。结论：**设计 pipeline 时"多读文档"比"多生成文本"便宜得多**。
3. **自建 vs 调 API 是一个利用率问题，不是单价问题。** 上面算出的 &#36;0.69/M 已经和同规模模型的 API 报价同量级。所以：**如果你的 GPU 只有 20% 时间在跑，自建成本是 API 的 5 倍。** 自建能赢的三个条件：(a) 长期高利用率，(b) 能吃 spot/碎片算力，(c) 有 API 不给的东西（自定义模型、数据不出域、logprobs）。

### 5.2 量化的收益与代价

| 方案 | 省什么 | 什么时候有效 | 质量代价 |
|---|---|---|---|
| **权重-only INT8/INT4**（GPTQ/AWQ） | 权重显存和读带宽 | **小 batch（memory-bound）收益最大**；大 batch 时收益小，反量化开销甚至可能反噬 | 通常小，但长链推理/数学退化更明显 |
| **W8A8 FP8**（H100 原生） | 显存 + **算力翻倍** | 两头都有收益，H100/H200 上的默认选择 | 一般很小 |
| **KV cache 量化到 FP8/INT8** | KV 显存减半 → **并发翻倍** | 长上下文、高并发场景收益巨大 | 需要在**长上下文**上专门测，短上下文测不出问题 |

**必须说的一句**：量化的质量评估**不能只看 MMLU**。要在**你自己的任务、自己的长度分布**上测。经验上退化最明显的是需要精确多步推理的任务（数学、代码），因为误差会沿推理链累积——而这恰好是我做的数据的类型。所以我的做法是：量化前后跑同一批题的可解率对比，差异超过阈值就不上。

### 5.3 Prefix caching：多阶段 pipeline 的最大杠杆

多阶段 LLM 流水线里，每次调用的前缀几乎完全相同：system prompt + rubric + few-shot 示例（常常 2000+ token），只有末尾的样本内容不同。开 prefix cache（vLLM 的 automatic prefix caching / SGLang 的 RadixAttention）后：

- 命中率 90% 时，prefill 的绝大部分消失。
- **配合按前缀排序调度**（把共享前缀的样本排在一起），命中率能从"随机命中"提到接近上限。

**经典事故（必讲）**：系统prompt里放了一个 `当前时间: 2026-07-29 14:32:11`，或者一个 request UUID，或者一个未排序的 `json.dumps()`——**前缀每次都不同，缓存命中率恒为 0**，而且没有任何报错。排查方法：直接看引擎报的 cache hit rate 指标，如果是 0，去前缀里找变量。

---

---

来源：[DrustZ / Mingrui Zhang · ml_sys_prep/18_case_distributed_inference.md](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/ml_sys_prep/18_case_distributed_inference.md)。作者整理资料；许可和第三方来源范围见阅读指南。
