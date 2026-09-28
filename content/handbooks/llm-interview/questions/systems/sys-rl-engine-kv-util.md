---
id: sys-rl-engine-kv-util
section: systems
order: 278
level: A
title: vLLM / SGLang 怎么看利用率？RL 训练里 KV cache 利用率看什么？
quick: >-
  Serving 看 GPU 忙闲、running / waiting、prefix hit、KV 占用百分比。RL 还要看：组内共享前缀有没有打到
  cache、长 CoT 有没有把页占满导致排队、abort / partial 有没有把 KV 碎片化。不要用训练 MFU 代替引擎
  cache 占用，也不要用 tokens/s 代替 goodput。
tags:
  - vLLM
  - SGLang
  - KV Cache
  - Metrics
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-23
sources:
  - title: vLLM production metrics
    url: https://docs.vllm.ai/en/stable/usage/metrics/
    type: primary
  - title: SGLang documentation
    url: https://docs.sglang.ai/
    type: primary
  - title: DistServe
    url: https://arxiv.org/abs/2401.09670
    type: primary
---

产品口径的 TTFT / TPOT / goodput 见 `sys-serving-metrics`。本题是 **引擎内部**，以及接到 GRPO 之后多看的几条。利用率三个字在面试里常被说成一个数，至少要拆成：算力忙不忙、KV 满不满、请求在跑还是在等。

## Serving 默认看这几条

vLLM 常见：`gpu_cache_usage_perc`（KV 页占用）、running / waiting 请求数、prefix cache hit、prefill / decode throughput。SGLang 同类：token usage、cache hit、radix 命中。GPU SM 利用率高但 waiting 很长，往往是 KV 满了插不进新请求，不是算子没写好。KV 占用很低、tokens/s 也低，才去查 batch 太小、PD 不均、或在等 CPU tokenizer / 工具。

Prefix cache 命中会让 TTFT 双峰：命中用户很快，冷启动仍慢。报数要分冷热，见 `sys-prefix-cache-isolation`。

## RL 训练多出来的读法

Rollout 不是聊天流量。同一 prompt 采 $G$ 条，前缀理应命中；组不齐、continuous batching 把短回复先抽走，见 `sys-rl-cont-batch-onpolicy`。读利用率时对上这几件事：

- **KV 占用冲到接近 1，waiting 涨：** 长尾 CoT 占着页，短题进不来，GPU 利用率被最长样本钉死，见 `byte-grpo-rollout-tail-gpu`。药是分桶、partial abort、加 decode 卡，不是把 `gpu_util` 再刷高一点。
- **KV 占用低，但墙钟仍慢：** 可能在等组齐、等 verifier、等 `update_weights`。引擎空，瓶颈在数据面。
- **prefix hit 低：** 同题 $G$ 条没共享到块，或每次权重更新把 cache flush 掉。flush 在换 $\theta$ 时是对的，见 `sys-partial-kv-policy`；同版本下命中低才是调度 / 哈希问题。
- **abort / partial 之后占用不降：** 页没释放，碎片化。看起来 cache 很满，实际可分配连续块不够。

训练侧 MFU 是 GEMM 有效算力，分母是峰值 FLOP。和引擎 KV 占用没有换算公式。Actor 更新时 SM 打满、rollout 卡在等，两池的利用率必须分开报。

先问 KV 满不满，再问请求在跑还是在等，最后才问 tokens/s。RL 还要确认：同版本前缀该命中，$G$ 条不该各占一份完整 prompt KV。

## 追问

- **`gpu_cache_usage_perc` 到 90% 是好是坏？** 要看 waiting。没有排队说明池子用满了还吃得下；waiting 飙升就是容量不够或长尾占页。
- **和 PD 分离怎么一起看？** Prefill 池看计算利用率，decode 池看 KV 占用。两个池都报同一个 tokens/s 没有意义，见 `sys-kv-cache-transfer`。
- **量化 KV 之后占用降了、正确率掉了？** 省的是页，采样分布变了。训练图仍要重算 logp，见 `meituan-verl-recompute-logprob`。
