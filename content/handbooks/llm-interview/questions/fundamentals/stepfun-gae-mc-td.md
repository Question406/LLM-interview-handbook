---
id: stepfun-gae-mc-td
section: fundamentals
order: 142
level: S
title: 阶跃星辰：GAE 是什么？蒙特卡洛和 TD 有何差别？
quick: >-
  MC 用整段回报，无偏方差大；TD 用 $r+\gamma V(s')-V(s)$，方差小有偏。GAE 用 $\lambda$
  对多步 TD 残差做指数加权，在偏差和方差之间插值，PPO 里几乎标配。
tags:
  - StepFun
  - GAE
  - TD
realInterview: true
status: published
format: markdown
updatedAt: 2026-08-21
sources:
  - title: 阶跃星辰大模型算法实习面经
    url: https://www.nowcoder.com/feed/main/detail/933afb27edd84b438682fd5bba95fbb3
    type: candidate-first-hand
  - title: GAE
    url: https://arxiv.org/abs/1506.02438
    type: primary-paper
---

## 真题记录

- 公司：阶跃星辰（StepFun）
- 团队 / 岗位：大模型算法实习
- 届别 / 流程：实习；轮次未披露
- 面试时间：原帖未披露
- 来源类型与可信度：牛客候选人原帖，B
- 原始措辞：**“GAE是什么？”**；**“蒙特卡洛模拟和时序差分估计的区别？”**；**“偏差和方差是什么？”**

这块容易把 GAE 说成「就是 advantage」，或不写 $\lambda$ 如何插值。我会讲：MC 无偏方差大、TD 有偏方差小，GAE 用 $\lambda$ 对多步 TD 残差做指数加权。偏差是估计期望相对真值的偏移，方差是估计本身的波动。

## MC、TD 与 $n$ 步优势

Monte Carlo 用整段折扣回报，不依赖 $V$：

$$
\hat G_t=\sum_{k=0}^{T-t-1}\gamma^k r_{t+k}.
$$

轨迹走完才能算。$\mathbb{E}[\hat G_t]=V^\pi(s_t)$（策略评估意义下无偏），但噪声沿轨迹累加，长度一长方差就涨。TD(0) 每步可更新：

$$
\delta_t=r_t+\gamma V(s_{t+1})-V(s_t).
$$

$\delta_t$ 是一步残差。$V$ 若是错的，期望不等于真优势，这是偏差；但只引入一步随机性，方差小。$n$ 步优势把中间 $n-1$ 个残差展开后再用 $V$ bootstrap：

$$
\hat A_t^{(n)}=\sum_{l=0}^{n-1}\gamma^l\delta_{t+l}.
$$

$n=1$ 即 TD，$n\to\infty$ 即 MC。偏差随 $n$ 降、方差随 $n$ 升。

## GAE：对 $n$ 步优势做 $\lambda$ 加权

GAE 不是再发明一种回报，而是对所有 $n$ 步优势做指数混合：

$$
\hat A_t^{\mathrm{GAE}(\gamma,\lambda)}=(1-\lambda)\sum_{n=1}^{\infty}\lambda^{n-1}\hat A_t^{(n)}=\sum_{l=0}^{\infty}(\gamma\lambda)^l\delta_{t+l}.
$$

第二式由交换求和得到，实现上从后往前递推：$\hat A_t=\delta_t+\gamma\lambda\hat A_{t+1}$。$\lambda=0$ 只留 $\delta_t$，近 TD；$\lambda=1$ 变成 $\sum\gamma^l\delta_{t+l}$，在 $V$ 一致时近 MC。PPO 几乎标配这套 $\hat A$ 再做标准化。

LLM 里 token 当步，$r$ 常只在句末非零，GAE 仍能把终局分沿 $(\gamma\lambda)^l$ 往回传；$\gamma$ 接近 1 时主要靠 $\lambda$ 控方差。GRPO 不用 learned $V$，组内相对分数替代 advantage，「偏差方差」以组大小 $n$ 的形式回来：组太小，基线噪；组太大，算力换方差。

推导交换求和时，把 $\hat A_t^{(n)}=\delta_t+\gamma\delta_{t+1}+\cdots+\gamma^{n-1}\delta_{t+n-1}$ 代入 $(1-\lambda)\sum_n\lambda^{n-1}\hat A_t^{(n)}$，固定某个 $\delta_{t+l}$ 的系数为 $(1-\lambda)\lambda^l\sum_{k=0}^{\infty}(\gamma\lambda)^k$ 再整理，即得 $(\gamma\lambda)^l$。实现从尾部递推：最后一步 $\hat A_{T-1}=\delta_{T-1}$，向前 $\hat A_t=\delta_t+\gamma\lambda\hat A_{t+1}$。这和「先算完整 $G_t$ 再减 $V$」不同：中途就可以写完一段的优势，适合截断 rollout。偏差是 $\mathbb{E}[\hat A]-A^\pi$，来自错误的 $V$ 或过早 bootstrap；方差是 $\mathrm{Var}(\hat A)$，来自轨迹噪声。被问「偏差方差是什么」不要答成机器学习课本的 U 形曲线，要落到这条估计器上。

稀疏奖励的直观：只有 $r_T$ 非零时，$\delta$ 主要在最后几步非零（若 $V$ 还没学会终局），GAE 把它们按 $(\gamma\lambda)^l$ 涂回前面的 token。$\lambda$ 太小，前面的思考 token 几乎分不到优势，模型只学最后几个字；$\lambda$ 太大，一整段噪声都灌进早期 token。PPO 再对 $\hat A$ 做 batch 标准化，那是另一层方差控制，会再引入「相对本 batch」的偏差。和 `fund-biasvariance` 同一根轴：稳是用偏换来的。

## 偏差方差落到估计器

先定义偏差是 $\mathbb{E}[\hat A]-A$，方差是 $\mathrm{Var}(\hat A)$，不要画监督学习的 U 形交差。MC 整段回报，无偏、方差随长度涨；TD 用 $V$ bootstrap，方差小、有偏。GAE 是对多步优势的 $\lambda$ 指数混合，实现写成 $\hat A_t=\delta_t+\gamma\lambda\hat A_{t+1}$。$\lambda=0$ 近 TD，$\lambda=1$ 近 MC。LLM 句末稀疏奖励时，GAE 负责把终局分往回涂；$\lambda$ 太小则思考 token 没优势。GRPO 没有这套 $V$，但组大小承担类似的方差角色，bias 是抹掉题与题的绝对难度。被追「为什么不永远 MC」就答：无偏但训不动，工程上不优。把轴画出来，这题和 bias-variance 卡就接上了。

## 追问

- **$V$ 错了 GAE 还能用吗？** 能，但 $\lambda$ 越小越吃 $V$ 的偏差；$\lambda$ 接近 1 更信轨迹。Value 系统性低估长链时，低 $\lambda$ 会压掉长思考。
- **和 $G_t-V(s_t)$？** 那是 MC advantage；GAE 用残差链，不必等整段结束也能递推，截断轨迹也能用。
- **$\gamma$ 和 $\lambda$ 谁管折扣？** $\gamma$ 是环境折扣，改的是任务目标；$\lambda$ 是估计器的偏差-方差旋钮，不改变真实回报定义。
- **句末稀疏奖励要不要 $\lambda=1$？** 不必。$\lambda=1$ 方差往往不可接受；0.95 到 0.99 更常见。先保证 $V$ 能拟合终局，再降 $\lambda$。
- **GRPO 还要 GAE 吗？** 通常不要 learned $V$。组内减均值是另一条降方差，bias 是抹掉 prompt 间绝对难度。
