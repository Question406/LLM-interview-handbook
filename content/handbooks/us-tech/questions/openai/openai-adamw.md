---
id: openai-adamw
section: openai
order: 15
level: A
title: OpenAI：AdamW 为什么要把 weight decay 从自适应步长里拆出来
quick: >-
  Adam 把 $L_2$ 加进梯度后再除 $\sqrt{v}$，衰减被自适应步长缩放，大梯度坐标几乎不 decay。AdamW 在自适应更新
  之外做 $\theta\leftarrow\theta-\eta\lambda\theta$，和 SGD 的 weight decay 同义，$\lambda$ 才能跟学习率分开调。
tags:
  - OpenAI
  - AdamW
  - Optimizer
  - Training
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-23
sources:
  - title: Decoupled Weight Decay Regularization
    url: https://arxiv.org/abs/1711.05101
    type: primary
  - title: Language Models are Few-Shot Learners (GPT-3)
    url: https://arxiv.org/abs/2005.14165
    type: primary
  - title: OpenAI Research Engineer Interview Guide
    url: https://www.tryexponent.com/guides/openai-research-engineer-interview-guide
    type: secondary
---

## 题怎么来的

GPT-3 公开用 Adam，weight decay $0.1$，并注明 $\beta_2=0.95$ 一类设定；后来实现默认就是 AdamW。这不是某一份能点名的 debug 轮原题，是训练岗手撕优化器时的标准对照。论文是 Loshchilov & Hutter，不要引用错成 Switch Transformer 的编号。显存里 Adam 状态有多肥，见 `openai-grad-checkpoint` 和 `nvidia-trillion-train`。

## $L_2$ 进 Adam 为什么不是 weight decay

SGD 上，梯度加 $\lambda\theta$ 和每步 $\theta\leftarrow(1-\eta\lambda)\theta$ 再减梯度，只差一个学习率重标定，常被混着叫。Adam 不是。

Adam 先做

$$
g\leftarrow\nabla L+\lambda\theta,\quad
m\leftarrow\beta_1 m+(1-\beta_1)g,\quad
v\leftarrow\beta_2 v+(1-\beta_2)g^2,
$$

再

$$
\theta\leftarrow\theta-\eta\,\hat m/(\sqrt{\hat v}+\varepsilon).
$$

$\lambda\theta$ 这条衰减被 $1/\sqrt{v}$ 除过。$v$ 大的坐标（经常更新、梯度猛）decay 几乎没了；$v$ 小的坐标被过度衰减。$\lambda$ 和 $\eta$、和自适应尺度缠在一起，网格搜索会看到最优 $\lambda$ 随 $\eta$ 漂。

AdamW 把衰减从 $g$ 里拿出来：

$$
\theta\leftarrow\theta-\eta\,\hat m/(\sqrt{\hat v}+\varepsilon)-\eta\lambda\theta.
$$

第二项不进 $m,v$。每个参数按同一 $\lambda$ 朝 0 拉，和 SGD weight decay 同义。论文还观察到 $\eta$ 与 $\lambda$ 的最优区变得可分，这才是「为什么拆」的工程理由，不只是公式美观。

白板我会写两行伪代码，标出 `wd` 加在 `grad` 上还是加在 `param` 上。PyTorch 的 `Adam` 带 `weight_decay` 曾经是 $L_2$ 进梯度；`AdamW` 才是 decoupled。面试说错 API 比说错论文更致命。

## LLM 训练里我会补的细节

- **哪些参数 decay。** 常见：二维权重 decay，bias 和 LayerNorm / RMSNorm 的一维参数不 decay。否则归一化尺度被持续拉向 0。
- **和 lr schedule。** decay 项里有 $\eta_t$，余弦退火时衰减强度跟着 lr 走。这是 AdamW 原论文的写法；有人用固定 $\lambda$ 不乘当前 $\eta$，要说你跟的是哪份实现。
- **$\beta_2$。** 语言模型常用 $0.95$ 而不是默认 $0.999$，让二阶矩跟得上非平稳的 token 梯度。这和是否 decouple 正交，但常被一起问。
- **和 clip。** grad clip 发生在进 $m,v$ 之前；weight decay 仍走参数侧。不要把 grad clip 当成 decay。

错法：把 AdamW 说成「Adam + 更大的 $L_2$」；把 $\varepsilon$ 说成 weight decay。$\varepsilon$ 只是防除零。

## 追问

- **为什么 GPT 不用纯 SGD？** 大 batch、稀疏 token 梯度上 Adam 类自适应更稳。有人用 Lion 等替代，不是 OpenAI 公开默认。
- **decay 要不要对 embedding？** 有的实现 decay，有的排除。选一种并在消融里固定，不要现场发明。
- **和 L2 正则到 loss 上？** 那就是耦合进梯度的版本，Adam 下不等价于 AdamW。
- **ZeRO 改 AdamW 公式吗？** 不改。只是 $m,v$ 分片存储。语义仍是 decoupled decay。
