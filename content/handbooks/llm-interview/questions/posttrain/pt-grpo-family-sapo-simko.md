---
id: pt-grpo-family-sapo-simko
section: posttrain
order: 246
level: S
title: 相对 GRPO，SAPO / MaxRL / SimKO 各改哪一层？
quick: "三者都保留组相对优势。SAPO 把硬 clip 换成软门；MaxRL 把目标从 $\\mathbb{E}[p]$ 推向 $\\mathbb{E}[\\log p]$；SimKO 在高熵 token 上把正梯度摊给 top-$K$ 候选，防 pass@K 塌。"
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

DAPO / GSPO / CISPO / Dr.GRPO 手册里已有独立卡。面试若一次抛出 SAPO、MaxRL、SimKO，不要把它们答成「又一个 advantage 公式」。三篇改的层不同：clip 形状、训练目标、候选 support。组均值 baseline 都还在。

## 先把已有家族放到一张表

| 方法 | 改的旋钮 | 被修的病 |
| --- | --- | --- |
| DAPO | 不对称 clip、动态采样、token-mean、overlong | 零方差组、稀有的正优势 token、长度假标签，见 `pt-dapo` |
| GSPO | 序列 likelihood ratio | token 级 $\rho$ 方差、MoE 路由噪声，见 `pt-gspo` |
| CISPO | detach 后截断 IS 权重 | 越界 token 梯度变 0，见 `pt-cispo` |
| Dr.GRPO | 指出 std / 长度归一化的偏置 | 「默认 whitening 无偏」，见 `pt-drgrpo` |
| DPPO | 估 TV / KL 再 mask，代替 $\lvert\rho-1\rvert$ | clip 过罚低频、欠约束高频，见 `pt-dppo-areal-trust-region` |
| GFPO | 先按长度 / $R$ 每 token 过滤，再算组优势 | 正确但灌水仍拿正优势；DAPO overlong 改的是奖励形状，见 `pt-gfpo` |

缩写 DPPO 会撞车：2026 题单里和 TRPO / AReaL 并列时，默认是 Divergence PPO（`2602.04879`）。Distributed PPO 是采样与更新并行；Decoupled PPO 是把 IS 和近端约束拆开。AReaL 约束的是样本年龄，见 `sys-areal-vs-slime`。先问对方是哪一个。

## SAPO：硬 clip 换成软门

Qwen 的 SAPO 仍是组算法。token 级重要性比 $r_{i,t}$ 进一个 sigmoid 门：

$$
f(x)=\sigma\big(\tau(x-1)\big)\cdot\frac{4}{\tau},\qquad
\tau=\begin{cases}\tau_{\mathrm{pos}} & \hat A\gt 0\\ \tau_{\mathrm{neg}} & \text{otherwise}\end{cases}.
$$

$r\approx 1$ 时梯度几乎全留；偏离时平滑衰减，而不是像 PPO $\min(\rho A,\mathrm{clip}(\rho)A)$ 那样直接打成 0。论文强调两件事：序列上平均门会接近 GSPO 那种序列级信任域；个别 token 特别 off-policy 时，只打这些 token，不把整句梯度扔掉。负优势用更小温度，负更新衰减更快：往下压一个 token 会把概率摊到很多不该涨的词上，比正向更新更不稳。

代价是 $\tau_{\mathrm{pos}}/\tau_{\mathrm{neg}}$ 新超参。公开实践仍新，不要吹成已经取代 GSPO。

## MaxRL：期望奖励只是似然的一阶

任务奖励是终局 0/1 时，模型其实定义了 $p_\theta(\mathrm{correct}\mid x)$。标准强化学习（RL） 最大化 $\mathbb{E}_x[p_\theta(x)]$；最大似然最大化 $\mathbb{E}_x[\log p_\theta(x)]$，等价于把梯度再乘 $1/p_\theta(x)$，更打困难题。MaxRL 用可调的采样计算在「期望奖励」和「真最大似然」之间插值，实现往往是对现有 GRPO / RLOO 改一行加权。它吃的是可验证二元反馈和额外 采样轨迹（rollout）；开放式奖励模型（RM） 任务不要硬套。

## SimKO：保的是 next-token 的 top-$K$ support

基于可验证奖励的强化学习（RLVR） 之后常见 pass@1 涨、大 $K$ 的 pass@K 掉：每个位置的 top-1 候选把质量吸干，候选分布塌成一条链。SimKO（arxiv `2510.14807`，页面上也出现过 CaSP 这个名字）不改 奖励分数（reward），改高熵「分叉」token 上的梯度：

- 答对：正梯度在 top-$K$ 候选之间摊，而不是只强化被采样的那一个。
- 答错：更狠地打 top-1，把质量挤回其它候选。

这和「加熵奖励」不同。熵是标量，不管质量摊到近邻推理 token 还是摊到无关词。SimKO 明确保的是已经有质量的那几个候选。不要说成牺牲 pass@1 换 pass@K：论文主张两条曲线一起涨。

现场口令：SAPO 改 clip 硬还是软；MaxRL 改优化的是 $\mathbb{E}[p]$ 还是 $\mathbb{E}[\log p]$；SimKO 改有没有把 next-token support 掐死。三句话分得开，就比背论文标题像准备过。

## 追问

- **和 CISPO 谁更像？** CISPO 仍是硬截断权重，只是越界后还有 $\nabla\log\pi$。SAPO 连截断都变成连续门。一个改 clip 对象，一个改 clip 形状。
- **MaxRL 是不是 pass@K 损失（loss）？** 不是同一条公式。它逼近的是 $\log p(\mathrm{correct})$，采样越多越接近似然；pass@K 目标直接优化「$K$ 次里至少一次对」。两者都在纠正「只最大化平均 0-1 奖励」。
- **SimKO 要改采样吗？** 不必。还是 GRPO 式组采样，动的是正确 / 错误轨迹上 top 候选的梯度分配，尤其高熵位置。
- **MoE 优先哪篇？** token 级 $\rho$ 方差大，先 GSPO / SAPO；多样性塌了再看 SimKO。不要三篇一起开。
- **和 GFPO？** GFPO 先滤掉灌水回复再算组优势，动的是谁进梯度，见 `pt-gfpo`。SimKO 动的是留下的 token 上 top-$K$ 怎么分梯度。一个管长度，一个管候选 support。
