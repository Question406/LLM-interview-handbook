---
id: coding-gae
section: coding
order: 41
level: S
title: 白板：GAE 反向递推，done、截断和 value clip 各在哪一行
quick: >-
  从后往前递推 $\delta_t$ 和 $A_t$，回合真正结束时两处都乘 $(1-d_t)$；长度截断不算结束，要用 $V(s_T)$ 自举；回报目标 detach，value clip 取 max。
tags:
  - 完整编程练习
  - Coding
  - PPO
  - RLHF
realInterview: false
status: published
format: markdown
updatedAt: 2026-10-18
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

## 完整编程练习（手册重构版）

> 下面的接口、约束和测试是手册补的练习约定，不是面试官原题。Python 3 + PyTorch，只在 CPU 浮点张量上验证，没有验证 GPU、多卡或性能。

### 题面、接口与约束

- `gae(rewards, values, dones, last_value, gamma, lam) -> (advantages, returns)`：`rewards`、`values`、`dones` 都是长度 $T$ 的一维浮点张量。`dones[t] = 1` 只表示第 $t$ 步之后回合真正结束（terminal）。`last_value` 是 buffer 最后一步之后那个状态的值 $V(s_T)$，buffer 在回合中途被截断时用它自举；最后一步是 terminal 时它会被 `(1 - done)` 屏蔽掉。返回的 `returns = advantages + values`，不带梯度。
- `value_loss(v_pred, v_old, returns, mask, clip) -> scalar`：带 value clip 的均方误差，只在 `mask = 1` 的位置求平均，`mask` 全 0 时返回 0。
- 同一个 buffer 里不包含「时间限制截断后又开始新回合」的边界：那种边界既要切断递推、又要用真实的 next value 自举，一个 `done` 表达不了（见复杂度与追问）。

### 输入输出示例

```text
gamma = lam = 1, rewards = [1, 2], values = [0, 0], dones = [0, 1]
-> advantages = [3, 2], returns = [3, 2]

gamma = lam = 1, rewards = [1], values = [0], dones = [0], last_value = 5
-> advantages = [6]      # 没结束，用 V(s_T) = 5 自举
```

### 解题思路与正确性

从最后一步往前算，用一个变量缓存后一步的优势 $A_{t+1}$。第 $t$ 步的 TD 残差和优势是

$$
\delta_t = r_t + \gamma(1-d_t)V_{t+1} - V_t,\qquad A_t = \delta_t + \gamma\lambda(1-d_t)A_{t+1}.
$$

在 terminal 处，两项都要乘 `not_done`：前一项阻止把下一个回合的 $V_{t+1}$ 自举进来，后一项阻止下一个回合的优势沿 trace 传回来。只屏蔽其中一项，回合之间就会互相泄漏。

最后一步的 $V_{t+1}$ 用 `last_value`。整个函数在 `torch.no_grad()` 下运行，所以 `returns` 是常量，当作 value loss 的目标时梯度只穿过预测值。

value clip 把新预测限制在旧预测附近 `clip` 的范围内，再对「未裁剪」和「裁剪后」两种误差取较大的那个。

### 完整参考实现（Python 3）

```python
import torch


@torch.no_grad()
def gae(rewards, values, dones, last_value, gamma=0.99, lam=0.95):
    """反向递推 GAE。所有输入都是 [T]；last_value 是 V(s_T)，用于截断时自举。

    返回 (advantages, returns)，returns = advantages + values，不带梯度。
    """
    num_steps = len(rewards)
    advantages = torch.zeros_like(rewards)
    next_advantage = 0.0
    for t in reversed(range(num_steps)):
        next_value = values[t + 1] if t + 1 < num_steps else last_value
        not_done = 1.0 - dones[t]
        delta = rewards[t] + gamma * next_value * not_done - values[t]
        next_advantage = delta + gamma * lam * not_done * next_advantage
        advantages[t] = next_advantage
    return advantages, advantages + values


def value_loss(v_pred, v_old, returns, mask, clip=0.2):
    """带 value clip 的 0.5 * MSE，按 mask 求平均；取两种误差中较大的一个。"""
    v_clipped = v_old + (v_pred - v_old).clamp(-clip, clip)
    unclipped_error = (v_pred - returns) ** 2
    clipped_error = (v_clipped - returns) ** 2
    loss = torch.maximum(unclipped_error, clipped_error)
    return 0.5 * (loss * mask).sum() / mask.sum().clamp(min=1)
```

### 可执行测试

```python
torch.set_num_threads(1)

# 第二步 terminal：A = [1 + 2, 2]，values 为 0 时 returns 等于 advantages
advantages, returns = gae(torch.tensor([1.0, 2.0]), torch.zeros(2),
                          torch.tensor([0.0, 1.0]), 0.0, gamma=1.0, lam=1.0)
assert torch.equal(advantages, torch.tensor([3.0, 2.0]))
assert torch.equal(advantages, returns)

# 截断：没有 terminal，用 last_value 自举
advantages, _ = gae(torch.tensor([1.0]), torch.zeros(1), torch.zeros(1),
                    5.0, gamma=1.0, lam=1.0)
assert advantages.item() == 6

# 最后一步是 terminal 时 last_value 被屏蔽
advantages, _ = gae(torch.tensor([1.0]), torch.zeros(1), torch.ones(1),
                    5.0, gamma=1.0, lam=1.0)
assert advantages.item() == 1

# 中间的 terminal 阻止下一个回合的奖励反向泄漏
advantages, _ = gae(torch.tensor([1.0, 100.0]), torch.zeros(2), torch.ones(2),
                    0.0, gamma=1.0, lam=1.0)
assert torch.equal(advantages, torch.tensor([1.0, 100.0]))

# lam = 0 退化成一步 TD：A_t = r_t + gamma * V_{t+1} - V_t
advantages, _ = gae(torch.tensor([1.0, 1.0]), torch.tensor([0.5, 2.0]),
                    torch.zeros(2), 3.0, gamma=0.5, lam=0.0)
assert torch.allclose(advantages, torch.tensor([1.0 + 0.5 * 2.0 - 0.5, 1.0 + 0.5 * 3.0 - 2.0]))

# returns 不带梯度，即使 values 来自 critic 前向
critic_values = torch.zeros(2, requires_grad=True)
_, returns = gae(torch.ones(2), critic_values, torch.zeros(2), 0.0)
assert not returns.requires_grad

# value clip 取较大的误差：预测 0.4 被裁到 0.2，误差 (0.2 - 1)^2 = 0.64 胜出
v_pred = torch.tensor([0.4], requires_grad=True)
loss = value_loss(v_pred, torch.zeros(1), torch.ones(1), torch.ones(1))
assert torch.isfinite(loss)
assert torch.isclose(loss, torch.tensor(0.32))

# mask 全 0 时损失为 0，不会除以 0
loss = value_loss(v_pred, torch.zeros(1), torch.ones(1), torch.zeros(1))
assert loss.item() == 0
```

### 复杂度与追问

设 buffer 长度为 $T$。时间 $O(T)$，输出空间 $O(T)$。

- 追问「buffer 里有时间限制截断怎么办」：要拆成两个信号。`terminated` 控制是否自举，`episode_boundary` 控制 trace 是否切断；截断点还要提供该状态真实的 next value。把两者合成一个 `done`，要么丢掉自举，要么让 trace 跨回合。
- 追问「批量怎么写」：在 `[B, T]` 上沿 $T$ 反向循环，用 response mask 代替 done（见下文 LLM 部分）。

## 题怎么来的

GRPO 用组内均值当 baseline，不需要 critic（价值模型）；经典的 PPO-RLHF 仍然要 value model 和 GAE。白板上常见的形式是：给一段一维的 GAE 代码让你找 bug，再补上 value loss。PPO 的 ratio 和 clip 见 `openai-ppo-clip`。

## 故意错误的起始片段（用于找 bug）

下面是面试时给你的错误代码，不是参考答案。对照上面的接口找出它偏离的地方。

```python
def gae(rewards, values, dones, gamma=0.99, lam=0.95):
    # rewards, values, dones: [T]，dones[t] = 1 表示 t 之后回合结束
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

**done 没用上。** 一段 buffer 里可能拼了好几个回合。回合在第 $t$ 步结束时，$V_{t+1}$ 属于下一个回合，不能自举进来，$A_{t+1}$ 也不能递推回来，所以 $\delta_t$ 和 $A_t$ 里都要乘 $(1-d_t)$。

**buffer 尾部被当成了结束。** `t + 1 == T` 时 `next_v = 0`，等于宣布回合在这里终止。如果只是 buffer 装满了、回合还没完（被截断），应该用 $V(s_T)$ 自举。放到 LLM 里，回答被 max length 截断和正常输出 EOS 结束是两种情况。

**回报目标带着梯度。** `values` 来自 critic 的前向，`adv + values` 又被当作 value loss 的目标，梯度会同时穿过预测和目标。目标要 detach；参考实现用 `torch.no_grad()` 做到这一点。

## LLM 上长什么样

一条回答是一个回合，每个 token 是一个时间步，通常取 $\gamma = 1$、$\lambda$ 取 0.95 或 1。奖励模型的分数只加在最后一个 token 上，每个 token 另有 $-\beta(\log\pi - \log\pi_{\mathrm{ref}})$ 的 KL 惩罚。$\lambda = 1$ 时 $A_t = \sum_{k\ge t} r_k - V_t$，也就是蒙特卡洛回报减去 baseline。

批量写法是在 `[B, T]` 上沿 $T$ 反向循环，用 response mask 代替 done。pad 位置的 reward 和 value 都要置 0，否则会被递推进有效 token。

## value loss 和 value clip

value clip 取 max 而不是 min，和 policy 那边的 min 一样，选的是悲观的一边：value 这一步走得太远，就不给它额外的好处。"37 implementation details" 那篇指出，value clip 在不少实验里没有帮助甚至有害，面试时能说出这一点就够了。

## 追问

**advantage 要不要再归一化？** PPO 常见做法是在 mini-batch 内减均值、除以标准差。归一化放在 GAE 之后做，回报目标仍用归一化之前的 $A + V$。

**$\lambda$ 起什么作用？** $\lambda = 0$ 是一步 TD，偏差大、方差小；$\lambda = 1$ 是蒙特卡洛，无偏但方差大。GAE 在两者之间插值。

**critic 从哪初始化？** 常见做法是从奖励模型初始化，把最后一层换成标量头。critic 训练不稳时 advantage 全是噪声，这也是 GRPO 去掉 critic 的主要理由之一。

## 相关题

- [[openai-ppo-clip]]：GAE 算出的 advantage 进的就是 PPO 的 clipped 目标，那张讲 clip 管什么、ratio 爆了怎么收。
- [[openai-agent-rl]]：把 GAE 用到工具调用的多步轨迹上，追问环境观察要 mask、环境要重置，不写递推代码。
