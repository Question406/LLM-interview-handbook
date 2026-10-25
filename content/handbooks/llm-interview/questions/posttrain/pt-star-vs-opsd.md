---
id: pt-star-vs-opsd
section: posttrain
order: 241
level: A
title: OPSD 和 STaR / Rejection Sampling 差在哪？为什么错解还能提供梯度？
quick: "STaR / RS 是硬蒸馏：只留终局答对的轨迹，在这些前缀上做监督微调（SFT），错的样本梯度为零。OPSD 是软蒸馏：教师不生成，只在学生自己的前缀上（对错都算）给下一 token 的分布，所以错解的中间步仍有 $r_n=\\log p_T-\\log p_S$。"
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

差别有三条。STaR / 拒绝采样给的是硬标签，OPSD 给的是软分布；前者只留答对的轨迹，后者对错都蒸；前者要教师（或模型自己）生成文本，OPSD 的教师只做前向、不生成。错解还能提供梯度，是因为 OPSD 的信号落在前缀的每个下一 token 上，跟终局对不对无关。被追问「这不就是 STaR 吗」时，我会先把这三条摆出来。拒绝采样什么时候该上见 `pt-rejection-sampling-vs-rl`，OPSD 的机制见 `pt-opsd`。

举个例子。学生解一道题，前三步都对，第四步算错，最后答案错了。STaR 会把整条轨迹扔掉，前三步的正确和第四步的错误都学不到；OPSD 的教师看着标准答案读这条轨迹，到第四步时会压低学生正在走的那个错 token，抬高更像正解的分叉。

## STaR：先写解释，答对了才留

STaR 让模型先写 rationale $r$ 再给答案 $y$，用 $R=\mathbf{1}[y=y^\star]$ 过滤，只对成功的样本做监督微调（SFT）。梯度近似一个序列级的策略梯度：

$$
\nabla J_{\mathrm{STaR}}\propto\mathbb{E}_{(r,y)\sim\pi_{\theta}}\big[\mathbf{1}[y=y^\star]\,\nabla\log\pi_{\theta}(r,y\mid x)\big].
$$

错的 rationale 整段扔掉。每条成功轨迹里所有 token 共享同一个 $0/1$，中间步没有 credit。后面的 rationalization 还要模型把 $y^\star$ 放进上下文，再生成一段解释，然后决定留不留。所以这是硬蒸馏，目标是一条离散文本。

Rejection sampling SFT 更粗，不要求先写解释，只筛出成功的 completion 再算交叉熵损失（CE），同样是「对了才学、在成功前缀上模仿」。覆盖已经够的时候它便宜、好审计；覆盖不够的时候，support 会越滤越窄。

## OPSD：教师不说话，错前缀也有分布

OPSD 里只有学生采样 $\hat{y}\sim p_S(\cdot\mid x)$。教师 $p_T(\cdot\mid x,y^\star)$ 对同一个前缀做一次前向，不吐 token，合理化是隐式完成的。逐点可以写成

$$
r_n=\log p_T(\hat{y}_n\mid x,y^\star,\hat{y}_{\lt n})-\log p_S(\hat{y}_n\mid x,\hat{y}_{\lt n}),
$$

做了 stop-gradient 之后，这就是 token 级的策略梯度。$\hat{y}$ 终局错了，$r_n$ 照样可以非零：教师在已经知道答案的条件下，会压低坏 token、抬高正解方向的分叉，前面例子里的第四步就是这样被纠正的。

实现上，仓库里 `--use_tinker_loss` 走的是只算采样 token 的 PG，省掉全词表；默认是全词表 $D(p_T\|p_S)$。被问到实现时可以这么说：全词表偏 covering，更稳，但更吃显存；只算采样 token 更像反向 KL 的 PG，风格 token 不 clip 更容易炸。

下面这张表把四种做法放在一起：

| | 教师做什么 | 哪些样本进梯度 | 每个 token 的信号 |
| --- | --- | --- | --- |
| SFT on $y^\star$ | 无，示范前缀 | 示范本身 | 硬 CE，off-policy |
| STaR / RS | 生成（或直接筛）成功文本 | 仅终局对 | 序列 $0/1$ 摊到整段 |
| GRPO | 无教师 | 组内有方差才有 | 序列 $A$ 摊到整段 |
| OPSD | 只前向，不生成 | 学生轨迹，对错都算 | 稠密分布 / $r_n$ |

STaR 把错的扔掉，OPSD 把错的当成要纠正的前缀。不过题太难、教师看了 $y^\star$ 也合理化不出来的时候，OPSD 的 $r_n$ 就是噪声，不见得比丢掉错解聪明，见 `pt-opsd` 里讲的容量限制。

## 追问

**能不能先 STaR 再 OPSD？**
可以。先用 RS / STaR 把格式和可读的思维链（CoT）拉进 support，再用 OPSD 在学生自己的错前缀上补恢复能力。顺序别颠倒，OPSD 替代不了全部冷启动。

**为什么 OPSD 不需要采 $G$ 条？**
它不靠组内相对优势，一条学生轨迹加一次教师前向就有逐 token 信号。u-OPSD 才重新引入 $G$，那是为了投票，见 `pt-u-opsd`。

**STaR 生成的 rationalization 能不能当 $y^\star$ 用？**
能，那是 OPSD 特权上下文的来源之一。但「生成解释」和「把解释当教师的条件」是两步，别说成一回事。
