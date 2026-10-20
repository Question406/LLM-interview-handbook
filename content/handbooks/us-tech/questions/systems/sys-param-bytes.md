---
id: sys-param-bytes
section: systems
order: 42
level: A
title: 系统：一个参数在训练里占多少字节，ZeRO 之后剩多少？
quick: >-
  Adam 混合精度下，一个参数大约 16 字节：bf16 权重 2、bf16 梯度 2、fp32 主权重 4、一阶矩 4、二阶矩 4。
  ZeRO-3 把这 16 字节除以数据并行度。激活、KV、参考模型不在这 16 里面。
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

## 题怎么来的

面试常让你在白板上估算「70B 放不放得进这 8 张卡」。数字来自 ZeRO 论文里的模型状态账，不是某一场的隐藏原题。阶段切分见 `sys-zero-stages`。

## 16 字节

混合精度、Adam、无 weight decay 的额外缓冲，按一个参数计：

| 状态 | 字节 |
| --- | --- |
| bf16 或 fp16 权重 | 2 |
| 同精度梯度 | 2 |
| fp32 主权重 | 4 |
| Adam 一阶矩 | 4 |
| Adam 二阶矩 | 4 |

合计 16。70B 参数是 $70 \times 10^9 \times 16 \approx 1.12 \times 10^{12}$ 字节，大约 1.04 TiB。8 张 80GB 卡一共 640GB，数据并行复制 8 份时连状态都放不下。

ZeRO-1 只把 12 字节的优化器状态除以 $N$，权重和梯度仍是每卡一份。ZeRO-2 再把梯度除以 $N$。ZeRO-3 把 16 字节都除以 $N$。$N=8$ 时 70B 的状态大约 130GB，再加激活才知道够不够。

## 不在这 16 里的

激活跟序列长度、层数、micro batch 走，重计算可以把它打下来。KV cache 是推理和 采样轨迹（rollout） 的账。后训练若开 KL，参考模型再加一份 bf16 权重（2 字节/参数），没有 Adam。优化器临时 buffer、梯度里的 fp32 reduce buffer，估算时加一成，不要假装 16 是上限。

## 代码

```python
def adam_mixed_bytes(n_params, data_parallel):
    # bf16 weight, bf16 grad, fp32 master, Adam m, Adam v
    per_param = 2 + 2 + 4 + 4 + 4
    sharded = n_params * per_param // data_parallel
    ref_bf16 = n_params * 2  # frozen reference, no Adam
    return sharded, ref_bf16
```

## 追问

**fp32 主权重能不能省？** 可以全程 bf16 更新，省 4 字节，大模型上容易不稳。面试里默认留着，除非对方说用了 Kahan 或别的补偿。

**MoE 怎么算？** 总参数按专家全算进 16 字节。一张卡若只放一部分专家，状态按它实际拥有的参数算，通信另算 all-to-all。
