---
id: code-weight-tying
section: coding
order: 56
level: A
title: 手写 embedding / lm_head 权重共享：同一块存储，梯度怎么流
quick: >-
  共享就是让 `lm_head.weight` 和 `emb.weight` 指向同一块存储，$V\times d$ 只存一份。前向 $\mathrm{logits}=h W^\top$，反向时 embedding 的 gather 梯度和 lm_head 的外积梯度加到同一张表上。别 `clone` 成两份 Parameter，那样既不省参数，梯度也对不上；bias 通常没有。
tags:
  - WeightTying
  - Embedding
  - Coding
realInterview: false
status: published
format: markdown
updatedAt: 2026-09-28
sources:
  - title: Using the Output Embedding to Improve Language Models
    url: https://arxiv.org/abs/1608.05859
    type: primary
---

## 题目描述

实现输入embedding与输出词表投影真正共享同一参数的极简语言模型，使两条路径的梯度累积到同一份权重。

下面的函数接口、输入表示和边界口径是本卡采用的手册练习约定；公开面经未披露完整题干的部分，不视为面试官原文。默认输入满足约束，无需额外编写非法输入校验。

### 接口与输入

实现 `TiedLM(vocab,d)` 及 `forward(ids)`。embedding权重为[vocab,d]，`lm_head`为无bias的d到vocab投影；ids为[B,T]合法整数token编号。

### 输出与约束

emb.weight和`lm_head`.weight必须是同一个Parameter对象，而非初始化时数值相同的副本。forward先查embedding再投影，返回[B,T,vocab] logits。无需softmax、位置编码或Transformer。

### 示例

```text
vocab=d=2，手动设共享权重为[[1,0],[0,1]]，ids=[[0,1]]
输出logits=[[[1,0],[0,1]]]，形状[1,2,2]。
修改任一入口的权重后，另一入口应立即看到相同变化。
```

## 解题思路与参考答案

权重共享的写法就一行，`self.lm_head.weight = self.emb.weight`：两层指向同一块存储，$V\times d$ 只存一份，反向时两边的梯度叠加到同一张表上。

面试里常见的问法是「为什么 7B 的 embedding 和输出层参数对不上 2 倍词表」，这时先确认这个模型有没有 tying。GPT-2 和很多小模型默认 tying；LLaMA 不 tying，`lm_head` 是独立的 $d\times V$。

## 写法

$$
h=\mathrm{Emb}(x),\quad \mathrm{logits}=h W^\top,\quad W=\mathrm{Emb}.\mathrm{weight}.
$$

```python
import torch.nn as nn

class TiedLM(nn.Module):
    def __init__(self, vocab, d):
        super().__init__()
        self.emb = nn.Embedding(vocab, d)
        self.lm_head = nn.Linear(d, vocab, bias=False)
        self.lm_head.weight = self.emb.weight          # 同一块存储

    def forward(self, idx):
        return self.lm_head(self.emb(idx))            # [B,T,V]
```

检查时看两边的 `data_ptr()` 相不相同。优化器里这两层别注册成两个独立参数，否则 Adam 状态翻倍、更新也写两次；`named_parameters()` 去重看 `id(p)`。

不共享时，两张表各算各的梯度，输出层可以学到和输入嵌入不同的几何。大词表加大 $d$ 时不 tying 更常见，因为输出层想要的特征和输入嵌入不一定一样。

## 简单测试怎么写

把上面的实现保存为 `solution.py`，以下测试放在实现之后。数值测试使用参考实现相同的 PyTorch 或 NumPy 环境；浮点结果用带容差的比较。运行 `python3 solution.py`，成功时输出 `simple tests passed`，失败时按断言报错行定位。不要加 `-O`，它会跳过 `assert`。

除了输出形状，必须用 is 检查两个层引用同一个 Parameter，仅数值相等不能证明共享。反向传播后也应看到同一份梯度。

```python
import torch
model = TiedLM(vocab=5, d=3)
assert model.emb.weight is model.lm_head.weight
out = model(torch.tensor([[0, 1]]))
assert out.shape == (1, 2, 5)
out.sum().backward()
assert model.emb.weight.grad is model.lm_head.weight.grad
print("simple tests passed")
```

## 追问

**能省多少参数？**
一份 $V d$。$V=128\mathrm{k}$、$d=4096$ 时，fp16 大约 1 GB。

**和 LoRA 一起用会怎样？**
只在 `lm_head` 或只在 `emb` 上挂 LoRA 时，另一侧不会自动有低秩更新，除非共享那张 $\Delta W$。

**两边的梯度会不会冲掉 embedding？**
会叠加。输入侧学习率偏大时，给 emb 用较小的 lr，或者单独 clip。
