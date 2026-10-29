---
id: coding-rloo-advantage
section: coding
order: 37
level: A
title: 白板：RLOO 的 leave-one-out baseline，向量化写法和它跟 GRPO 差在哪
quick: >-
  RLOO 把同组其余 $G-1$ 条奖励的均值当 baseline，用 `(sum - r) / (G - 1)` 就能向量化计算。它的 advantage
  是减组均值的 $\frac{G}{G-1}$ 倍；GRPO 还会除以每个 prompt 自己的 std，所以不同题的缩放也会不同。
tags:
  - 完整编程练习
  - Coding
  - GRPO
  - RLHF
realInterview: false
status: published
format: markdown
updatedAt: 2026-10-18T00:00:00.000Z
sources:
  - title: >-
      Back to Basics: Revisiting REINFORCE Style Optimization for Learning from
      Human Feedback in LLMs
    url: 'https://arxiv.org/abs/2402.14740'
    type: primary
  - title: 'Buy 4 REINFORCE Samples, Get a Baseline for Free!'
    url: 'https://openreview.net/forum?id=r1lgTGL5DE'
    type: primary
  - title: 'DeepSeekMath, GRPO'
    url: 'https://arxiv.org/abs/2402.03300'
    type: primary
---

## 题目描述

一批 prompt 各生成 G 条 rollout，奖励按 prompt 分组连续存放。为每条 rollout 计算 leave-one-out 优势：以同组其他回答的平均奖励为 baseline，并返回与输入排列一致的一维优势数组。

以下为手册重构练习约定，不表示面经披露了这些完整接口。默认输入满足合法约束，不要求额外的非法输入校验。

### 接口、输入与输出

- `rloo_advantage(rewards, G) -> [B * G]`：`rewards` 是 `[B * G]` 的标量奖励，每个 prompt 的 $G$ 条 rollout 连续排布。每条回答的 baseline 是同组其余 $G-1$ 条奖励的均值，不包含自己，也不做 std 归一。
- 约束：$G \ge 2$，奖励个数能被 $G$ 整除。

### 示例

```text
rewards = [1, 0, 0], G = 3   -> [1, -0.5, -0.5]
rewards = [3, 1],    G = 2   -> [2, -2]
rewards 跨两个 prompt 时，只在各自的 G 条之间比较，不能混组
```

## 解题思路与参考答案

我会把奖励 reshape 成每个 prompt 一行，先求组内总和，减掉当前回答，再除以其余回答的数量，最后用当前奖励减去这个 baseline。比如两条回答时，它们直接互相作 baseline。关键是先确认 rollout 排布，避免把不同 prompt 的回答混进同一组。


## 完整编程练习（手册重构版）

> 下面的接口、约束和测试是手册补的练习约定。Python 3 + PyTorch，CPU 上验证。

### 题面、接口与约束

- `rloo_advantage(rewards, G) -> [B * G]`：`rewards` 是 `[B * G]` 的标量奖励，每个 prompt 的 $G$ 条 rollout 连续排布。每条回答的 baseline 是同组其余 $G-1$ 条奖励的均值，不包含自己，也不做 std 归一。
- 约束：$G \ge 2$，奖励个数能被 $G$ 整除，否则抛 `ValueError`。

### 输入输出示例

```text
rewards = [1, 0, 0], G = 3   -> [1, -0.5, -0.5]
rewards = [3, 1],    G = 2   -> [2, -2]
rewards 跨两个 prompt 时，只在各自的 G 条之间比较，不能混组
```

### 解题思路与正确性

先 `reshape(-1, G)`，每一行就是一个 prompt 的一组回答。组内总和减去自己，再除以 $G-1$，得到排除自身的均值，这一步对整行向量化完成。

每组 advantage 之和为 0：$\sum_i (r_i - b_i) = \sum_i r_i - \frac{1}{G-1}\sum_i\sum_{j\ne i} r_j = \sum_i r_i - \sum_j r_j = 0$。测试里也检查了它恰好是「减组均值」的 $\frac{G}{G-1}$ 倍。

### 完整参考实现（Python 3）

```python
import torch


def rloo_advantage(rewards, G):
    """RLOO advantage：每条回答减去同组其余 G - 1 条奖励的均值，不做 std 归一。

    rewards: [B * G]，按 repeat_interleave 排布，即每个 prompt 的 G 条 rollout 连续。
    返回同形状 [B * G]。
    """
    if G < 2:
        raise ValueError(f"leave-one-out needs G >= 2, got {G}")
    if rewards.numel() % G != 0:
        raise ValueError(
            f"{rewards.numel()} rewards cannot be split into groups of {G}"
        )
    grouped = rewards.reshape(-1, G)  # [B, G]
    baseline = (grouped.sum(dim=1, keepdim=True) - grouped) / (G - 1)
    return (grouped - baseline).reshape(-1)
```

### 简单测试怎么写

把完整参考实现和题中的可执行测试按顺序放进 `solution.py`，运行 `python3 solution.py`。测试依赖的库与参考实现相同。

例如，测试中的 `assert torch.allclose(adv, torch.tensor([1.0, -0.5, -0.5, 0.0, 0.0, 0.0]))` 就是一条结果检查；连同它前面的输入准备一起运行，不能只复制断言这一行。

数值结果用 `allclose` 一类带容差的断言检查，并同时确认形状；随机输入固定种子。手算预期值或选独立的参考公式，避免把待测实现再抄一遍当答案。

先确认一个小场景的预期值，再运行题中的完整测试；出现断言失败时，从第一条失败的检查定位。断言全部通过只说明已覆盖的场景通过，还需要按本题约束补充 edge-case tests。

### 可执行测试

```python
def expect_value_error(fn, *args):
    try:
        fn(*args)
    except ValueError:
        return
    raise AssertionError(f"{fn.__name__} should raise ValueError")


torch.set_num_threads(1)

# 两个 prompt 各 3 条：第一组 [1, 0, 0] -> [1, -0.5, -0.5]；奖励全相同的组 advantage 全 0
rewards = torch.tensor([1.0, 0.0, 0.0, 4.0, 4.0, 4.0])
adv = rloo_advantage(rewards, 3)
assert torch.allclose(adv, torch.tensor([1.0, -0.5, -0.5, 0.0, 0.0, 0.0]))

# 每组 advantage 之和为 0，不同 prompt 不混组
assert torch.allclose(adv.reshape(-1, 3).sum(-1), torch.zeros(2))

# 等于 G / (G - 1) 倍的「减组均值」
grouped = rewards.reshape(-1, 3)
centered = (grouped - grouped.mean(dim=1, keepdim=True)).reshape(-1)
assert torch.allclose(adv, centered * 3 / 2)

# G = 2：两条互为 baseline
assert torch.allclose(
    rloo_advantage(torch.tensor([3.0, 1.0]), 2), torch.tensor([2.0, -2.0])
)

# G < 2 或长度不能整除 G 时报错
expect_value_error(rloo_advantage, rewards, 1)
expect_value_error(rloo_advantage, rewards, 4)
```

### 复杂度与追问

设 prompt 数为 $B$、每组 $G$ 条。时间 $O(BG)$，额外空间 $O(BG)$（baseline 张量）。

- 追问「rollout 排布不是 `repeat_interleave` 而是 `repeat`」：同一个 prompt 的回答间隔 $B$ 个位置，要先 `reshape(G, B).T` 再算，或者让 sampling 端改排布；不改就会悄悄混组。

## 题怎么来的

每个 promptsampling $G$ 条回答，每条得到一个标量奖励。RLOO 用「其余 $G-1$ 条的平均奖励」当 baseline。题目让你写出向量化版本，再问它和 GRPO 的组内 normalization 是什么关系。

sampling 轨迹（rollout）按 `prompts.repeat_interleave(G)` 排布，也就是 `[p0, p0, ..., p0, p1, p1, ...]`。

## 故意错误的起始片段（用于找 bug）

下面是旧版教学里要修复的错误片段，不是参考答案。对照上面的题面，找出它偏离接口的地方；正确实现和测试在前面的练习部分。

```python
def rloo_advantage(rewards, G):
    # rewards: [B * G]
    r = rewards.view(G, -1)
    baseline = (r.sum(dim=0, keepdim=True) - r) / G
    return (r - baseline).reshape(-1)
```

## 错在哪

有两处错误。

第一处是 `view(G, -1)`。它按行切，第一行是前 $B$ 个奖励。但排布是 `repeat_interleave`，同一个 prompt 的 $G$ 条是连续的，应该用 `view(-1, G)`，并沿 `dim=1` 求和。写反以后，一个「组」里混着不同 prompt 的回答，baseline 就没有意义了。这个 bug 不会报错，$B = G$ 时连形状都完全一样。

第二处是分母，应该是 $G-1$。除以 $G$ 得到的 baseline 是 leave-one-out 均值的 $\frac{G-1}{G}$ 倍。奖励非负时 baseline 偏小，advantage 整体往正方向偏，每条回答都被推高一点。

## 为什么不用自己

baseline 不能依赖 $y_i$ 本身。$\mathbb{E}[b\,\nabla\log\pi(y_i)] = 0$ 成立的前提是 $b$ 和 $y_i$ 独立。其余 $G-1$ 条回答和 $y_i$ 是独立 sampling 的，所以 leave-one-out baseline 不引入偏差。

不过，包含自己的组均值和它其实只差一个常数倍：

$$
r_i - \bar r = r_i - \frac{r_i + \sum_{j\ne i} r_j}{G} = \frac{G-1}{G}\Big(r_i - \frac{1}{G-1}\sum_{j\ne i} r_j\Big)
$$

也就是说，减组均值等于 RLOO advantage 乘以 $\frac{G-1}{G}$。梯度方向仍然无偏，只是尺度变小，相当于学习率小了一点。面试里能讲出这一步，比代码写对更重要。

## 和 GRPO 的区别

GRPO 的 advantage 是 $(r_i - \bar r)/\mathrm{std}(r)$。减均值的部分和 RLOO 只差常数倍，但除以 std 不是常数：每个 prompt 的 std 不同，奖励差异小的 prompt（几乎全对或几乎全错）会被放大。Dr. GRPO 认为这是一种按题目难度的偏置，建议去掉。全对或全错时 std 为 0，处理方法见 `anthropic-grpo-debug`。

## 追问

**组里奖励全是 0 或全是 1 怎么办？** leave-one-out 之后 advantage 全是 0，这个 prompt 不产生梯度。和 GRPO 一样，采到这种组等于浪费算力；DAPO 的动态 sampling 就是把这些组过滤掉，再补采。

**奖励里有 per-token 的 KL 惩罚怎么办？** RLOO 论文把 KL 并进序列级奖励，先算 $r - \beta\,\mathrm{KL}$，再做 leave-one-out。KL 放在奖励里还是放在损失（loss）里，见 `sys-kl-place`。

**$G = 2$ 时是什么？** $A_1 = r_1 - r_2$，$A_2 = r_2 - r_1$。两条回答互为 baseline，形式上很像一对偏好数据。

## 相关题

- [[sys-adv-bcast]]：算出每条回答的标量优势之后，怎么乘到 token 上、哪些位置必须 mask 成 0。
- [[align-grpo]]：口述 GRPO 用组均值当 baseline、为什么不要 critic，是这里「和 GRPO 的区别」的概念版。
- [[sys-group-size]]：$G$ 取多大的显存和方差账，RLOO 的 $G-1$ 个对照同样受它约束。
- [[sys-kl-place]]：这里追问 KL 并进序列奖励再做 leave-one-out，那张讲 KL 写进奖励和写进 loss 的梯度差别。
