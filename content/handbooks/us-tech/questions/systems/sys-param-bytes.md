---
id: sys-param-bytes
section: systems
order: 42
level: A
title: 系统：一个参数在训练里占多少字节，ZeRO 之后剩多少？
quick: "混合精度 Adam 训练里，一个参数的模型状态约占 16 字节：权重和梯度各 2 字节，fp32 主权重及两个动量各 4 字节。ZeRO-3 按数据并行度分摊这些状态，激活、KV 和冻结的参考模型还要另算。"
tags:
  - Pretrain
  - Memory
  - ZeRO
realInterview: false
status: published
format: markdown
updatedAt: 2026-09-24
sources:
  - title: ZeRO
    url: https://arxiv.org/abs/1910.02054
    type: primary
  - title: ZeRO-Offload
    url: https://arxiv.org/abs/2101.06840
    type: primary
---

按混合精度 Adam 来估算，一个参数的模型状态约占 16 字节。先把这笔账算出来，再加激活和临时缓冲，才能判断模型能不能放进 GPU。比如白板题问 70B 能否放进 8 张卡，可以这样拆：

| 状态 | 字节 |
| --- | --- |
| bf16 或 fp16 权重 | 2 |
| 同精度梯度 | 2 |
| fp32 主权重 | 4 |
| Adam 一阶矩 | 4 |
| Adam 二阶矩 | 4 |

这里没有另加 weight decay 缓冲。合计 16 字节，70B 参数就是 $70 \times 10^9 \times 16 \approx 1.12 \times 10^{12}$ 字节，约 1.04 TiB。8 张 80GB 卡一共 640GB，普通数据并行还会在每卡复制一份状态，显然放不下。

ZeRO-1 把其中 12 字节的优化器状态按数据并行度 $N$ 分摊，权重和梯度仍然每卡一份；ZeRO-2 继续分摊梯度；ZeRO-3 则把全部 16 字节都分摊。$N=8$ 时，70B 每卡的状态仍约 130GB，还没加激活。各阶段的细节见 `sys-zero-stages`，这笔模型状态账来自 ZeRO 论文，题目不是某场面试的隐藏原题。

激活随序列长度、层数和 micro batch 增长，可以靠重计算减少。KV cache 属于推理和采样轨迹（rollout）的开销。后训练若有 KL 参考模型，还要加一份冻结的 bf16 权重，即每参数 2 字节，它没有 Adam。优化器临时 buffer 和 fp32 梯度 reduce buffer 也需要空间，粗估时再留一成，16 字节只是模型状态的估算值。

下面算的是 ZeRO-3 分片后的状态，以及未分片的参考模型权重：

```python
def adam_mixed_bytes(n_params, data_parallel):
    # bf16 weight, bf16 grad, fp32 master, Adam m, Adam v
    per_param = 2 + 2 + 4 + 4 + 4
    sharded = n_params * per_param // data_parallel
    ref_bf16 = n_params * 2  # frozen reference, no Adam
    return sharded, ref_bf16
```

## 追问

**fp32 主权重能省吗？**
可以全程用 bf16 更新，省下每参数 4 字节，但大模型上容易不稳定。估算默认保留它，除非题目明确用了 Kahan 或其他补偿。

**MoE 怎么算？**
总参数里的专家都要计入状态。单卡按它实际持有的专家参数算显存，all-to-all 通信另外算。
