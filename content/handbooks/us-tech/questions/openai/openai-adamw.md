---
id: openai-adamw
section: openai
order: 15
level: A
title: OpenAI：AdamW 为什么要把 weight decay 从自适应步长里拆出来
quick: "AdamW 把 weight decay 放到自适应梯度更新之外，直接做 $\\theta\\leftarrow\\theta-\\eta\\lambda\\theta$。如果把 $L_2$ 放进 Adam 的梯度，衰减也会被一二阶矩和自适应尺度改变；拆开后，同一次更新中参数按相同的比例收缩，调参时更容易分清学习率与衰减的作用。"
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

AdamW 把参数收缩和 Adam 的自适应梯度更新分开做。把 $L_2$ 正则项加进梯度后，它会一起进入一阶、二阶矩，再被各坐标不同的自适应尺度缩放；同一个衰减系数，最终对不同参数的作用就不一样。AdamW 直接在参数侧减去 $\eta\lambda\theta$，可以清楚地看到这次收缩了多少。

这是 Loshchilov 和 Hutter 的公开论文所讨论的问题。这张卡是优化器对照题，没有可点名的 OpenAI 原题记录；GPT-3 公开写过 Adam、weight decay $0.1$ 和 $\beta_2=0.95$ 等设定。Adam 状态的显存估算见 `openai-grad-checkpoint` 和 `nvidia-trillion-train`。

## $L_2$ 进 Adam 为什么不是 weight decay

先看 SGD：梯度加 $\lambda\theta$，可写成每步先做 $\theta\leftarrow(1-\eta\lambda)\theta$ 再减梯度，因此按对应的学习率标定后，常把两者一起称为衰减。Adam 的自适应缩放会改变这种对应关系。

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

$\lambda\theta$ 进入梯度后，也受到 $1/\sqrt{v}$ 的缩放。经常出现大梯度、$v$ 大的坐标，衰减会被削弱；$v$ 小的坐标则被相对放大。因此 $\lambda$ 的实际作用还依赖 $\eta$ 和历史梯度尺度，网格搜索会发现最优 $\lambda$ 随 $\eta$ 改变。

AdamW 把衰减从 $g$ 里拿出来：

$$
\theta\leftarrow\theta-\eta\,\hat m/(\sqrt{\hat v}+\varepsilon)-\eta\lambda\theta.
$$

额外的参数收缩项不进入 $m,v$。同一步里，各参数按同一 $\lambda$ 对应的比例向 0 收缩，符合 SGD weight decay 的含义。论文还观察到 $\eta$ 与 $\lambda$ 的最优区变得可分，这是「为什么拆」的工程理由，不只是公式好看。

核对实现时可以标清 `wd` 加在 `grad` 还是 `param`。PyTorch 的 `Adam` 带 `weight_decay` 历史上采用 $L_2$ 进梯度的做法，`AdamW` 则采用 decoupled 形式，阅读代码时要确认所用实现。

## LLM 训练里我会补的细节

实际配置通常让二维权重 decay，bias、LayerNorm / RMSNorm 的一维参数不 decay，避免持续把归一化尺度拉向 0。

衰减项还有当前学习率 $\eta_t$，余弦退火时它会一起变小，这是原论文的写法；也有实现用固定 $\lambda$ 而不乘当前 $\eta$，要交代采用哪种口径。语言模型常把 $\beta_2$ 设为 $0.95$，而非默认 $0.999$，使二阶矩更快跟随非平稳 token 梯度；这个选择与是否 decouple 分开调。

grad clip 在梯度进入 $m,v$ 前完成，weight decay 继续走参数侧。两者分别控制梯度更新和参数收缩。

因此增大 $L_2$ 不能变成 AdamW，$\varepsilon$ 也只负责防除零，不承担参数衰减。

## 追问

**为什么 GPT 不用纯 SGD？**
因为在大 batch、稀疏 token 梯度下，Adam 类自适应更新通常更稳。Lion 等是可讨论的替代方法，不能说成 OpenAI 公开默认。
**decay 要不要对 embedding？**
取决于实现，有的 decay、有的排除。选定后在消融里固定，明确报告自己的配置。
**和 L2 正则加到 loss 上？**
那就是耦合进梯度的版本，Adam 下不等价于 AdamW。
**ZeRO 改 AdamW 公式吗？**
不改。只是 $m,v$ 分片存储。语义仍是 decoupled decay。
