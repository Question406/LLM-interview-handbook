---
id: sys-batch-invariance
section: systems
order: 274
level: S
title: 什么是 batch invariance？atomicAdd 能让推理确定性吗？
quick: "Batch invariance 要求同一请求的结果不随同批请求、batch size 和调度改变。动态 batching 会改变 kernel shape 和浮点归约顺序，温度 0 也可能漂；`atomicAdd` 只避免丢更新，写入顺序仍不固定，需要固定归约或 batch-invariant kernel 才能处理这类差异。"
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

Batch invariance 指同一输入的计算结果不受同批其他请求影响，`atomicAdd` 本身无法保证这一点。比如温度 0 时，同一道题单独跑和放进在线 batch 里跑，仍可能生成不同 token；seed 只固定 RNG，不能固定浮点归约顺序。强化学习（RL）评测和回归测试都需要把这两类来源分开。

PyTorch 常用：

```python
torch.use_deterministic_algorithms(True)
torch.backends.cudnn.benchmark = False
torch.backends.cudnn.deterministic = True
```

并设置 `CUBLAS_WORKSPACE_CONFIG=:4096:8`，再固定 Python / NumPy / CUDA seed。这仍不能保证每个算子都有确定实现：没有确定 kernel 的 op 会直接报错或走慢路径。分布式还要固定 NCCL、集合通信顺序。RL 中生成训练轨迹的 rollout 引擎默认 **不** 保证可复现。

同一输入提示、同一权重、同一采样参数，输出不应取决于：

- 同一步逐 token 生成（decode）时还在处理哪些请求；
- `max_num_seqs` / 实际 batch；
- 处理输入并建立缓存的 prefill 阶段如何分块、等待队列顺序。

破坏它的是浮点非结合、reduction 树形状随 $B$ 变、softmax / RMSNorm 的 block 划分、以及原子操作的竞争。Continuous batching 几乎必然改变这些形状，见 `sys-cont-batch`。所以「离线 bs=1 过了、在线一上 serving 就漂」常常是执行路径变了，权重未必错。

vLLM 文档写得很直：默认不保证可复现。离线可关 V1 multiprocessing；在线最多启用 batch-invariant 路径，且只在相同硬件、相同版本下有意义。不要承诺跨机、跨版本 bit 一致。

多个线程对同一地址用 `atomicAdd` 累加浮点数时，写入先后不固定，所以和的 bit 级结果可能不同，这本身就会引入非确定性。解决时可以使用固定顺序、固定树形结构的归约，或使用不受同批其他请求影响的 batch-invariant kernel，也可以验证结果并在不一致时回滚。原子加只保证「没有丢失更新」，不保证「两次加法同一 bit」。

MoE 路由、FP8 动态 scale、非确定的 expert 负载均衡会再加一层漂移。评测和训练日志不要混用「温度 0 = 可复现」。

## 追问

**温度 0 为什么还会漂？**
greedy 仍走浮点 logits。argmax 在两个 logit 极近时会因末位翻转切到另一个 token，后面整段都分叉。
**RL 的 old logprob 要不要确定性？**
训练图重算 logp 时，用的是 trainer kernel。引擎侧非确定只影响采样路径，不影响 ratio 的 $\pi_\theta$。但评测对比必须锁同一引擎配置。
**关 continuous batching 能换确定性吗？**
能换一部分，吞吐会掉回去。生产上通常接受 serving 非确定，把金标回归放到 bs=1 + invariant 模式。
