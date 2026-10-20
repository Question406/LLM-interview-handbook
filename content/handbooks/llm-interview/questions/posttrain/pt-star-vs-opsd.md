---
id: pt-star-vs-opsd
section: posttrain
order: 241
level: A
title: OPSD 和 STaR / Rejection Sampling 差在哪？为什么错解还能提供梯度？
quick: "STaR / RS 是硬蒸馏：只保留终局对的轨迹，再在那些前缀上做 监督微调（SFT），错的样本梯度为零。OPSD 是软蒸馏：教师不生成，只在学生自己的前缀（对错都算）上给下一 token 的分布。错解的中间步仍然有 $r_n=\\log p_T-\\log p_S$。"
tags:
  - OPSD
  - STaR
  - Rejection Sampling
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-21
sources:
  - title: STaR — Self-Taught Reasoner
    url: https://arxiv.org/abs/2203.14465
    type: primary
  - title: Self-Distilled Reasoner (OPSD)
    url: https://arxiv.org/abs/2601.18734
    type: primary
  - title: OPSD 作者博客（含与 STaR 对照）
    url: https://siyan-zhao.github.io/blog/2026/opsd/
    type: secondary
---

被追「这不就是 STaR / 拒绝采样再 SFT 吗」时，先答 **硬标签 vs 软分布、滤对 vs 对错都蒸、教师生不生成**。RS 何时该上见 `pt-rejection-sampling-vs-rl`；OPSD 机制见 `pt-opsd`。

## STaR：显式合理化 + 对了才留

STaR 让模型先写 rationale $r$ 再给答案 $y$，用 $R=\mathbf{1}[y=y^\star]$ 过滤，只对成功样本做 监督微调（SFT）。梯度近似序列级政策梯度

$$
\nabla J_{\mathrm{STaR}}\propto\mathbb{E}_{(r,y)\sim\pi_{\theta}}\big[\mathbf{1}[y=y^\star]\,\nabla\log\pi_{\theta}(r,y\mid x)\big].
$$

错的 rationale **整段扔掉**。每条成功轨迹里所有 token 共享同一个 $0/1$，没有中间 credit。后续 rationalization 还要模型把 $y^\star$ 写进上下文再 **生成** 一段解释，再决定是否留下。这是硬蒸馏：目标是一条离散文本。

Rejection sampling SFT 更粗：不要求先写解释，只筛成功 completion 再 交叉熵损失（CE）。同样是「对了才学、在成功前缀上模仿」。覆盖已经够时便宜、可审计；覆盖不够时 support 越滤越窄。

## OPSD：教师不说话，错前缀也有分布

OPSD 只有学生采样 $\hat{y}\sim p_S(\cdot\mid x)$。教师 $p_T(\cdot\mid x,y^\star)$ 对同一前缀做一次前向，不吐 token。合理化是隐式的。逐点可写成

$$
r_n=\log p_T(\hat{y}_n\mid x,y^\star,\hat{y}_{\lt n})-\log p_S(\hat{y}_n\mid x,\hat{y}_{\lt n}),
$$

stop-gradient 之后就是 token 级政策梯度。$\hat{y}$ 终局错了，$r_n$ 仍可非零：教师在「已经知道答案」的条件下，会压低学生正在走的坏 token、抬高更像正解的分叉。这就是「错解还能提供梯度」，信号在 **前缀的下一 token**，不在终局指示函数。

仓库里 `--use_tinker_loss` 走的是这条采样 token 的 PG，省全词表；默认则是全词表 $D(p_T\|p_S)$。面试被问实现时：全词表 covering 更稳、更吃显存；采样 token 更像反向 KL 的 PG，风格 token 不 clip 更容易炸。

## 一张表

| | 教师做什么 | 哪些样本进梯度 | 每个 token 的信号 |
| --- | --- | --- | --- |
| SFT on $y^\star$ | 无，示范前缀 | 示范本身 | 硬 CE，off-policy |
| STaR / RS | 生成（或直接筛）成功文本 | 仅终局对 | 序列 $0/1$ 摊到整段 |
| GRPO | 无教师 | 组内有方差才有 | 序列 $A$ 摊到整段 |
| OPSD | 只前向，不生成 | 学生轨迹，对错都算 | 稠密分布 / $r_n$ |

STaR 把错的扔掉；OPSD 把错的当成要纠正的前缀。题太难、教师看了 $y^\star$ 也不会 rationalize 时，OPSD 的 $r_n$ 是噪声，并不比丢掉错解更聪明，见 `pt-opsd` 容量限制。

## 追问

- **先 STaR 再 OPSD？** 可以。RS / STaR 先把格式和可读思维链（CoT） 拉进 support，再用 OPSD 在学生自己的错前缀上补恢复。不要颠倒成「OPSD 替代全部冷启动」。
- **为什么 OPSD 不必 $G$ 条？** 不靠组内相对优势。一条学生轨迹 + 一次教师前向就有逐 token 信号。u-OPSD 才重新引入 $G$，那是为了投票，见 `pt-u-opsd`。
- **STaR 的 rationalization 能不能当 $y^\star$？** 能，那是 OPSD 的特权上下文来源之一。别把「生成解释」和「用解释当教师条件」说成同一步。
