---
id: stepfun-gae-mc-td
section: fundamentals
order: 142
level: S
title: 阶跃星辰：GAE 是什么？Monte Carlo 和 TD 有何差别？
quick: >-
  MC 用整段回报，无偏但方差大；TD 用 $r+\gamma V(s')-V(s)$，方差小但 $V$ 不准就有偏。GAE 用 $\lambda$ 对多步
  TD 残差做指数加权，在两者之间插值，PPO 里几乎是标配。
tags:
  - StepFun
  - GAE
  - TD
realInterview: true
status: published
format: markdown
updatedAt: 2026-08-21T00:00:00.000Z
sources:
  - title: 阶跃星辰大模型算法实习面经
    url: 'https://www.nowcoder.com/feed/main/detail/933afb27edd84b438682fd5bba95fbb3'
    type: candidate-first-hand
  - title: GAE
    url: 'https://arxiv.org/abs/1506.02438'
    type: primary-paper
---

## 真题记录

- 公司：阶跃星辰（StepFun）
- 团队 / 岗位：大模型算法实习
- 届别 / 流程：实习；轮次未披露
- 面试时间：原帖未披露
- 来源类型与可信度：牛客候选人原帖，B
- 原始措辞：“GAE 是什么？”；“Monte Carlo 模拟和时序差分估计的区别？”；“偏差和方差是什么？”

GAE 是一种 advantage estimation 器：它用 $\lambda$ 对多步 TD 残差做指数加权，在 Monte Carlo 和 TD 之间插值。Monte Carlo 用整段回报，无偏但方差大；TD 只看一步再用 $V$ bootstrap，方差小，但 $V$ 不准就有偏。这里的偏差是估计的期望相对真值的偏移，方差是估计本身的波动。

把 GAE 说成「就是 advantage」，或者不写 $\lambda$ 怎么插值，是这题最常见的丢分。

## MC、TD 和 $n$ 步优势

Monte Carlo 用整段折扣回报，不依赖 $V$：

$$
\hat G_t=\sum_{k=0}^{T-t-1}\gamma^k r_{t+k}.
$$

轨迹走完才能算。$\mathbb{E}[\hat G_t]=V^\pi(s_t)$（策略评估意义下无偏），但噪声沿轨迹累加，长度一长方差就涨。TD(0) 每一步都能更新：

$$
\delta_t=r_t+\gamma V(s_{t+1})-V(s_t).
$$

$\delta_t$ 是一步残差。$V$ 如果是错的，它的期望就不等于真优势，这是偏差；但它只引入一步的随机性，方差小。$n$ 步优势把中间的残差展开后再用 $V$ bootstrap：

$$
\hat A_t^{(n)}=\sum_{l=0}^{n-1}\gamma^l\delta_{t+l}.
$$

$n=1$ 就是 TD，$n\to\infty$ 就是 MC。偏差随 $n$ 降，方差随 $n$ 升。

## GAE 对 $n$ 步优势做 $\lambda$ 加权

GAE 没有发明新的回报，它对所有 $n$ 步优势做指数混合：

$$
\hat A_t^{\mathrm{GAE}(\gamma,\lambda)}=(1-\lambda)\sum_{n=1}^{\infty}\lambda^{n-1}\hat A_t^{(n)}=\sum_{l=0}^{\infty}(\gamma\lambda)^l\delta_{t+l}.
$$

第二个等号来自交换求和：把 $\hat A_t^{(n)}=\delta_t+\gamma\delta_{t+1}+\cdots+\gamma^{n-1}\delta_{t+n-1}$ 代入 $(1-\lambda)\sum_n\lambda^{n-1}\hat A_t^{(n)}$，固定某个 $\delta_{t+l}$，它的系数是 $(1-\lambda)\lambda^l\sum_{k=0}^{\infty}(\gamma\lambda)^k$，整理后就是 $(\gamma\lambda)^l$。$\lambda=0$ 只剩 $\delta_t$，接近 TD；$\lambda=1$ 变成 $\sum\gamma^l\delta_{t+l}$，在 $V$ 一致时接近 MC。

实现上从尾部往前递推：最后一步 $\hat A_{T-1}=\delta_{T-1}$，再往前 $\hat A_t=\delta_t+\gamma\lambda\hat A_{t+1}$。这和「先算完整的 $G_t$ 再减 $V$」不一样，中途就能写完一段的优势，适合截断的 sampling 轨迹（rollout）。PPO 几乎标配这套 $\hat A$，然后再做 standardization。

被问「偏差方差是什么」，别答成机器学习课本里的 U 形曲线，要落到这条估计器上。偏差是 $\mathbb{E}[\hat A]-A^\pi$，来自错误的 $V$ 或过早 bootstrap；方差是 $\mathrm{Var}(\hat A)$，来自轨迹噪声。

## 放到 LLM 上

LLM 里把一个 token 当一步，$r$ 常常只在句末非零。比如只有 $r_T$ 非零、$V$ 还没学会终局时，$\delta$ 主要集中在最后几步，GAE 再按 $(\gamma\lambda)^l$ 把它们传回前面的 token。$\lambda$ 太小，前面的思考 token 几乎分不到优势，模型只学最后几个字；$\lambda$ 太大，一整段噪声都灌进早期 token。$\gamma$ 接近 1 时，主要靠 $\lambda$ 控方差。PPO 再对 $\hat A$ 做 batch standardization，那是另一层方差控制，也会再引入「相对本 batch」的偏差。这和 `fund-biasvariance` 是同一根轴：稳是用偏差换来的。

GRPO 不用 learned $V$，用组内相对分数代替 advantage，偏差方差的问题以组大小 $n$ 的形式回来：组太小，基线噪声大；组变大要更多算力，但能降低基线方差。

## 追问

**$V$ 错了，GAE 还能用吗？**
能，但 $\lambda$ 越小越吃 $V$ 的偏差，$\lambda$ 接近 1 更信轨迹。Value 如果系统性低估很长的推理过程，低 $\lambda$ 会把长思考压掉。

**和 $G_t-V(s_t)$ 有什么区别？**
那是 MC advantage。GAE 用残差链，不必等整段结束就能递推，截断的轨迹也能用。

**$\gamma$ 和 $\lambda$ 谁管折扣？**
$\gamma$ 是环境折扣，改的是任务目标；$\lambda$ 是估计器的偏差-方差旋钮，不改变真实回报的定义。

**句末稀疏奖励要不要设 $\lambda=1$？**
不必。$\lambda=1$ 的方差往往不可接受，0.95 到 0.99 更常见。先保证 $V$ 能拟合终局，再降 $\lambda$。

**GRPO 还要 GAE 吗？**
通常不要 learned $V$。组内减均值是另一条降方差的路，它的 bias 是抹掉了 prompt 之间的绝对难度。
