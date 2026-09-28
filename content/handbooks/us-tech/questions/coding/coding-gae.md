---
id: coding-gae
section: coding
order: 41
level: S
title: 白板：GAE 反向递推，done、截断和 value clip 各在哪一行
quick: >-
  $\delta_t = r_t + \gamma(1-d_t)V_{t+1} - V_t$，$A_t = \delta_t + \gamma\lambda(1-d_t)A_{t+1}$，从后往前。
  回合结束时两处都要乘 $(1-d_t)$；被长度截断的不是结束，要用 $V$ 自举。
  回报目标 $A_t + V_t$ 必须 detach。value clip 取 max，是悲观的那一边。
tags:
  - Coding
  - PPO
  - RLHF
realInterview: false
status: published
format: markdown
updatedAt: 2026-09-28
sources:
  - title: High-Dimensional Continuous Control Using Generalized Advantage Estimation
    url: https://arxiv.org/abs/1506.02438
    type: primary
  - title: The 37 Implementation Details of Proximal Policy Optimization
    url: https://iclr-blog-track.github.io/2022/03/25/ppo-implementation-details/
    type: secondary
  - title: Proximal Policy Optimization Algorithms
    url: https://arxiv.org/abs/1707.06347
    type: primary
---

## 题怎么来的

GRPO 用组内均值当 baseline，不需要 critic。经典 PPO-RLHF 还是要 value model 和 GAE。白板常见的形式：给一段 GAE，一维，找 bug；再补 value loss。PPO 的 ratio 和 clip 见 `openai-ppo-clip`。

给你的代码：

```python
def gae(rewards, values, dones, gamma=0.99, lam=0.95):
    # rewards, values, dones: [T]，dones[t]=1 表示 t 之后回合结束
    T = len(rewards)
    adv = torch.zeros(T)
    last = 0.0
    for t in reversed(range(T)):
        next_v = values[t + 1] if t + 1 < T else 0.0
        delta = rewards[t] + gamma * next_v - values[t]
        last = delta + gamma * lam * last
        adv[t] = last
    return adv, adv + values
```

## 错在哪

**done 没用上。** 一段 buffer 里可能拼了好几个回合。回合在 $t$ 结束时，$V_{t+1}$ 属于下一个回合，不能自举进来，$A_{t+1}$ 也不能递推回来：

$$
\delta_t = r_t + \gamma(1-d_t)V_{t+1} - V_t,\qquad A_t = \delta_t + \gamma\lambda(1-d_t)A_{t+1}
$$

**buffer 尾部当成了结束。** `t + 1 == T` 时 `next_v = 0`，等于说回合在这里终止。如果只是 buffer 装满了、回合还没完（被截断），应该用 $V(s_T)$ 自举。LLM 里对应的是：回答被 max length 截断，和正常输出 EOS 结束，是两种情况。

**回报目标带着梯度。** `values` 来自 critic 前向，`adv + values` 当 value loss 的目标，梯度会同时穿过预测和目标。目标要 detach。

```python
@torch.no_grad()
def gae(rewards, values, dones, last_value, gamma=0.99, lam=0.95):
    # last_value: V(s_T)，buffer 最后一步之后那个状态的值；真结束时传 0
    T = len(rewards)
    adv = torch.zeros_like(rewards)
    last = 0.0
    for t in reversed(range(T)):
        next_v = values[t + 1] if t + 1 < T else last_value
        not_done = 1.0 - dones[t]
        delta = rewards[t] + gamma * next_v * not_done - values[t]
        last = delta + gamma * lam * not_done * last
        adv[t] = last
    return adv, adv + values
```

## LLM 上长什么样

一条回答是一个回合，token 是时间步。通常 $\gamma = 1$、$\lambda$ 取 0.95 或 1。奖励模型的分数只加在最后一个 token 上，每个 token 另有 $-\beta(\log\pi - \log\pi_{\mathrm{ref}})$ 的 KL 惩罚。$\lambda = 1$ 时 $A_t = \sum_{k\ge t} r_k - V_t$，就是蒙特卡洛回报减 baseline。

批量写法：`[B, T]` 上沿 $T$ 反向循环，用 response mask 代替 done。pad 位置的 reward 和 value 都要置 0，否则会被递推进有效 token。

## value loss 和 value clip

```python
def value_loss(v_pred, v_old, returns, mask, clip=0.2):
    v_clipped = v_old + (v_pred - v_old).clamp(-clip, clip)
    loss = torch.maximum((v_pred - returns) ** 2, (v_clipped - returns) ** 2)
    return 0.5 * (loss * mask).sum() / mask.sum().clamp(min=1)
```

取 max 而不是 min：和 policy 的 min 一样是悲观的一边，value 这一步走太远就不给它额外的奖励。"37 implementation details" 那篇指出 value clip 在不少实验里没有帮助甚至有害，面试时说得出这一点就够了。

## 追问

**advantage 要不要再归一化？** PPO 常见做法是在 mini-batch 内减均值除 std。归一化在 GAE 之后做，回报目标用归一化之前的 $A + V$。

**$\lambda$ 的作用？** $\lambda = 0$ 是一步 TD，偏差大方差小；$\lambda = 1$ 是蒙特卡洛，无偏方差大。GAE 在两者之间插值。

**critic 从哪初始化？** 常见是从奖励模型初始化，最后一层换成标量头。critic 训练不稳时 advantage 全是噪声，这是 GRPO 去掉 critic 的主要理由之一。
