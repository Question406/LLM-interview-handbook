---
id: pt-grpo-family-sapo-simko
section: posttrain
order: 246
level: S
title: 相对 GRPO，SAPO / MaxRL / SimKO 各改哪一层？
quick: "三篇都保留组相对优势，改的是不同的层：SAPO 把硬 clip 换成按优势正负分温度的软门，MaxRL 把优化目标从 $\\mathbb{E}[p]$ 往 $\\mathbb{E}[\\log p]$ 推，SimKO 在高熵 token 上把正梯度摊给 top-$K$ 候选，防止 pass@K 塌掉。"
tags:
  - SAPO
  - MaxRL
  - SimKO
  - GRPO
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-23
sources:
  - title: Soft Adaptive Policy Optimization
    url: https://arxiv.org/abs/2511.20347
    type: primary
  - title: Maximum Likelihood Reinforcement Learning
    url: https://arxiv.org/abs/2602.02710
    type: primary
  - title: SimKO — Simple Pass@K Policy Optimization
    url: https://arxiv.org/abs/2510.14807
    type: primary
---
三篇改的层不一样：SAPO 改 clip 的形状，MaxRL 改训练目标，SimKO 改 next-token 候选怎么分梯度，组均值 baseline 三篇都还留着。面试官一次抛出这三个名字，最容易答成「又一个 advantage 公式」，所以我会先把这三层分开说。

DAPO、GSPO、CISPO、Dr.GRPO 手册里已经有独立卡。先把已有的家族放在一张表里，新方法往上一摆就知道它动的是哪个旋钮：

| 方法 | 改的旋钮 | 被修的病 |
| --- | --- | --- |
| DAPO | 不对称 clip、动态采样、token-mean、overlong | 零方差组、稀有的正优势 token、长度假标签，见 `pt-dapo` |
| GSPO | 序列 likelihood ratio | token 级 $\rho$ 方差、MoE 路由噪声，见 `pt-gspo` |
| CISPO | detach 后截断 IS 权重 | 越界 token 梯度变 0，见 `pt-cispo` |
| Dr.GRPO | 指出 std / 长度归一化的偏置 | 「默认 whitening 无偏」，见 `pt-drgrpo` |
| DPPO | 估 TV / KL 再 mask，代替 $\lvert\rho-1\rvert$ | clip 过罚低频、欠约束高频，见 `pt-dppo-areal-trust-region` |
| GFPO | 先按长度 / $R$ 每 token 过滤，再算组优势 | 正确但灌水仍拿正优势；DAPO overlong 改的是奖励形状，见 `pt-gfpo` |

DPPO 这个缩写会撞车。2026 题单里它和 TRPO、AReaL 并列出现时，默认指 Divergence PPO（`2602.04879`）；Distributed PPO 讲的是采样和更新并行，Decoupled PPO 是把 IS 和近端约束拆开。AReaL 约束的是样本年龄，见 `sys-areal-vs-slime`。听到 DPPO 先问一句对方指哪一个。

## SAPO：硬 clip 换成软门

Qwen 的 SAPO 还是组算法，只是 token 级重要性比 $r_{i,t}$ 不再硬截断，改成进一个 sigmoid 门：

$$
f(x)=\sigma\big(\tau(x-1)\big)\cdot\frac{4}{\tau},\qquad
\tau=\begin{cases}\tau_{\mathrm{pos}} & \hat A\gt 0\\ \tau_{\mathrm{neg}} & \text{otherwise}\end{cases}.
$$

$r\approx 1$ 时梯度几乎全留，偏离越多衰减越多，过程是平滑的。PPO 的 $\min(\rho A,\mathrm{clip}(\rho)A)$ 一越界就直接把梯度打成 0。论文强调了两点：在序列上平均这个门，效果接近 GSPO 那种序列级信任域；个别 token 特别 off-policy 时，只压这几个 token，整句的梯度还在。负优势用更小的温度，负更新衰减得更快，因为往下压一个 token，概率会摊到很多本来不该涨的词上，比正向更新更不稳。

代价是多了 $\tau_{\mathrm{pos}}/\tau_{\mathrm{neg}}$ 两个超参。公开实践还很新，别说成它已经取代了 GSPO。

## MaxRL：期望奖励只是似然的一阶近似

奖励是终局 0/1 时，模型其实定义了一个 $p_\theta(\mathrm{correct}\mid x)$。标准强化学习（RL）最大化的是 $\mathbb{E}_x[p_\theta(x)]$，最大似然最大化的是 $\mathbb{E}_x[\log p_\theta(x)]$，相当于把梯度再乘一个 $1/p_\theta(x)$，难题的权重就上去了。MaxRL 用可调的采样计算量在「期望奖励」和「真正的最大似然」之间插值，落到代码上往往是在现有 GRPO / RLOO 里改一行加权。它依赖可验证的二元反馈和额外的采样轨迹（rollout），开放式奖励模型（RM）任务就别硬套了。

## SimKO：保住 next-token 的 top-$K$ support

基于可验证奖励的强化学习（RLVR）之后常见的现象是 pass@1 涨了，大 $K$ 的 pass@K 却掉了。原因是每个位置的 top-1 候选把概率质量吸干，候选分布塌成一条链。SimKO（arxiv `2510.14807`，页面上也出现过 CaSP 这个名字）不动奖励分数（reward），改的是高熵「分叉」token 上的梯度。答对的时候，正梯度在 top-$K$ 候选之间摊开，被采样的那个之外的几个也一起强化；答错的时候，更狠地压 top-1，把质量挤回其它候选。

这和加熵奖励是两回事。熵是一个标量，它不管质量摊到了相近的推理 token 上，还是摊到了无关的词上；SimKO 明确保护的是本来就有质量的那几个候选。也别把它说成拿 pass@1 换 pass@K，论文的主张是两条曲线一起涨。

现场能用三句话把它们分开就够了：SAPO 看 clip 是硬是软，MaxRL 看优化的是 $\mathbb{E}[p]$ 还是 $\mathbb{E}[\log p]$，SimKO 看有没有把 next-token support 掐死。

## 追问

**SAPO 和 CISPO 谁更像？**
两个改的东西不同。CISPO 还是硬截断权重，只是越界以后仍保留 $\nabla\log\pi$，改的是 clip 作用的对象；SAPO 连截断都换成了连续的门，改的是 clip 的形状。

**MaxRL 是不是 pass@K 损失（loss）？**
不是同一条公式。MaxRL 逼近的是 $\log p(\mathrm{correct})$，采样越多越接近似然；pass@K 目标直接优化「$K$ 次里至少对一次」。两者想纠正的是同一件事，就是只最大化平均 0-1 奖励。

**SimKO 要改采样吗？**
不用。还是 GRPO 式的组采样，动的只是正确和错误轨迹上 top 候选的梯度怎么分，重点在高熵位置。

**MoE 模型先上哪篇？**
token 级 $\rho$ 方差大，先上 GSPO 或 SAPO；多样性塌了再看 SimKO。三篇别一起开，不然分不清是哪个起了作用。

**和 GFPO 怎么区分？**
GFPO 先把灌水的回复滤掉再算组优势，动的是哪些回复进梯度，见 `pt-gfpo`。SimKO 动的是留下来的 token 上 top-$K$ 怎么分梯度。一个管长度，一个管候选 support。
