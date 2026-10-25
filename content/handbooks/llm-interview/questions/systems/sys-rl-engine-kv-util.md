---
id: sys-rl-engine-kv-util
section: systems
order: 278
level: A
title: vLLM / SGLang 怎么看利用率？RL 训练里 KV cache 利用率看什么？
quick: "利用率要拆开看：算力忙不忙、KV 满不满、请求在跑还是在等。RL 里还要看同题 $G$ 条有没有命中共享前缀、长 CoT 是否占满页、abort 后页有没有释放。"
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

我会分别看算力、KV 容量和请求队列，再把它们对起来判断瓶颈。比如 GPU 很忙但 waiting 一直增长，可能是长 CoT 占满 KV 页，新请求进不来；这时继续提高计算利用率也解决不了问题。接到 GRPO 后，还要检查同题 $G$ 条的前缀共享、是否等组齐，以及 abort 后有没有释放页。产品侧的 TTFT、TPOT 和 goodput 见 `sys-serving-metrics`。

## Serving 默认看这几条

vLLM 常见：`gpu_cache_usage_perc`（KV 页占用）、running / waiting 请求数、prefix cache hit、输入预填充（prefill，即处理输入并建立缓存） / 逐 token 生成（decode） throughput。SGLang 同类：token 使用量、cache hit、radix 命中。GPU SM 利用率高但 waiting 很长，往往是 KV 满了插不进新请求，不是算子没写好。KV 占用很低、tokens/s 也低，才去查 batch 太小、PD 不均、或在等 CPU tokenizer / 工具。

Prefix cache 命中会让 TTFT 双峰：命中用户很快，冷启动仍慢。报数要分冷热，见 `sys-prefix-cache-isolation`。

## 强化学习（RL） 训练多出来的读法

Rollout 不是聊天流量。同一输入提示 采 $G$ 条，前缀理应命中；组不齐、continuous batching 把短回复先抽走，见 `sys-rl-cont-batch-onpolicy`。读利用率时对上这几件事：

- **KV 占用冲到接近 1，waiting 涨：** 长尾 思维链（CoT，即分步推理过程） 占着页，短题进不来，整体利用率受最长样本制约，见 `byte-grpo-rollout-tail-gpu`。处理方法是长度分组、partial abort 或增加 decode 卡，不是把 `gpu_util` 再刷高一点。
- **KV 占用低，但实际耗时仍慢：** 可能在等组齐、等 验证器（verifier）、等 `update_weights`。引擎空，瓶颈在数据面。
- **prefix hit 低：** 同题 $G$ 条没共享到块，或每次权重更新把 cache flush 掉。flush 在换 $\theta$ 时是对的，见 `sys-partial-kv-policy`；同版本下命中低才是调度 / 哈希问题。
- **abort / partial 之后占用不降：** 页没释放，碎片化。看起来 cache 很满，实际可分配连续块不够。

训练侧 MFU 是 GEMM 有效算力，分母是峰值 FLOP。和引擎 KV 占用没有换算公式。Actor 更新时 SM 打满、采样轨迹（rollout） 卡在等，两池的利用率必须分开报。

所以排查时先对照 KV 水位和 waiting，再看 tokens/s。RL 里同版本、同一输入提示（prompt）的 $G$ 条回答应该共享前缀，若各占一份完整 prompt KV，要检查调度和缓存键。

## 追问

**`gpu_cache_usage_perc` 到 90% 是好是坏？**
要看 waiting。没有排队说明池子用满了还吃得下；waiting 飙升就是容量不够或长尾占页。
**和 PD 分离怎么一起看？**
Prefill 池看计算利用率，decode 池看 KV 占用。两个池都报同一个 tokens/s 没有意义，见 `sys-kv-cache-transfer`。
**量化 KV 之后占用降了、正确率掉了？**
省的是页，采样分布变了。训练图仍要重算 logp，见 `meituan-verl-recompute-logprob`。
