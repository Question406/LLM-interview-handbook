---
id: sys-batch-invariance
section: systems
order: 274
level: S
title: 什么是 batch invariance？atomicAdd 能让推理确定性吗？
quick: >-
  Batch invariance 是同一条请求的输出不随同批其它请求、batch size、调度顺序改变。浮点加法没有结合律，动态
  batching 会换 kernel shape 和 reduction 顺序，温度 0 也可能漂。`atomicAdd`
  通常是非确定性来源，因为多线程写入顺序不固定。要确定性靠固定顺序归约或 batch-invariant kernel，不是再加一层
  atomic。
tags:
  - Reproducibility
  - vLLM
  - Serving
  - Numerics
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-23
sources:
  - title: PyTorch Reproducibility
    url: https://docs.pytorch.org/docs/stable/notes/randomness.html
    type: primary
  - title: torch.use_deterministic_algorithms
    url: https://docs.pytorch.org/docs/2.9/generated/torch.use_deterministic_algorithms.html
    type: primary
  - title: vLLM Reproducibility
    url: https://docs.vllm.ai/en/latest/usage/reproducibility/
    type: primary
---

这块容易把「设了 seed」说成可复现。Seed 管的是 RNG。Batch invariance 管的是 **同一输入在不同邻居下数学是否同一条执行路径**。RL 评测、温度 0 回归、以及「为什么这道题今天和昨天 token 不同」都会问到这里。

## 训练侧怎么开确定性

PyTorch 常用：

```python
torch.use_deterministic_algorithms(True)
torch.backends.cudnn.benchmark = False
torch.backends.cudnn.deterministic = True
```

并设置 `CUBLAS_WORKSPACE_CONFIG=:4096:8`，再固定 Python / NumPy / CUDA seed。这仍不能保证每个算子都有确定实现：没有确定 kernel 的 op 会直接报错或走慢路径。分布式还要固定 NCCL、集合通信顺序。RL 里 rollout 引擎默认 **不** 保证可复现。

## Batch invariance 是什么

同一 prompt、同一权重、同一采样参数，输出不应取决于：

- 同一步 decode 里还有谁；
- `max_num_seqs` / 实际 batch；
- prefill 切块边界、等待队列顺序。

破坏它的是浮点非结合、reduction 树形状随 $B$ 变、softmax / RMSNorm 的 block 划分、以及原子操作的竞争。Continuous batching 几乎必然改变这些形状，见 `sys-cont-batch`。所以「离线 bs=1 过了、在线一上 serving 就漂」常常不是权重错，是执行路径变了。

vLLM 文档写得很直：默认不保证可复现。离线可关 V1 multiprocessing；在线最多启用 batch-invariant 路径，且只在相同硬件、相同版本下有意义。不要承诺跨机、跨版本 bit 一致。

## atomicAdd 帮不上忙

多线程对同一地址 `atomicAdd` 浮点数，写入顺序不固定，和的 bit 级结果不同。这是 **非确定性来源**，不是修复。要修：换成确定性 reduction（固定顺序、固定 tree）、batch-invariant kernel（对单个请求的归约不依赖邻居）、或 verify-rollback。原子加只保证「没有丢失更新」，不保证「两次加法同一 bit」。

MoE 路由、FP8 动态 scale、非确定的 expert 负载均衡会再加一层漂移。评测和训练日志不要混用「温度 0 = 可复现」。

## 追问

- **温度 0 为什么还会漂？** greedy 仍走浮点 logits。argmax 在两个 logit 极近时会因末位翻转切到另一个 token，后面整段都分叉。
- **RL 的 old logprob 要不要确定性？** 训练图重算 logp 时，用的是 trainer kernel。引擎侧非确定只影响采样路径，不影响 ratio 的 $\pi_\theta$。但评测对比必须锁同一引擎配置。
- **关 continuous batching 能换确定性吗？** 能换一部分，吞吐会掉回去。生产上通常接受 serving 非确定，把金标回归放到 bs=1 + invariant 模式。
