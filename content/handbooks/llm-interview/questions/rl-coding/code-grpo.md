---
id: code-grpo
section: rl-coding
order: 6
level: S
title: 手写 GRPO group advantage：$\mathrm{std}\approx 0$ 怎么处理？
quick: "按 prompt 分组，在组内算 $A=(r-\\mathrm{mean})/(\\mathrm{std}+\\mathrm{eps})$。$\\mathrm{std}\\approx 0$ 说明整组全对或全错、没有相对信号，要记录下来再过滤或重采；`eps` 只是防除零，造不出信号。"
tags:
  - GRPO
  - PyTorch
realInterview: false
status: published
format: markdown
provenance: legacy-handbook-v2
updatedAt: 2026-08-21
sources:
  - title: DeepSeekMath / GRPO
    url: https://arxiv.org/abs/2402.03300
    type: primary
---

## 题目描述

实现 `group_advantage(rewards,eps=1e-6)`，为同一 prompt 的多条回答计算组内标准化优势，并标记存在奖励差异的组。

`rewards` 为有限浮点 PyTorch 张量 `[N,G]`，N 为正，G>=2；每一行是同一 prompt 的 G 条回答的奖励，不同行属于不同 prompt。eps 为正。返回 `(adv,informative)`：adv 为 `[N,G]` 浮点张量，informative 为 `[N]` 布尔张量。

本手册练习约定使用**总体标准差**（方差分母为G），不是样本标准差。每组优势定义为 `(reward-组均值)/(组总体标准差+eps)`。informative 当且仅当该组标准差大于 eps 时为 True。整组奖励相同应得到全零优势和 False 标记。函数只计算并标记，不删除、重排或重新采样任何组。

### 示例

```text
输入：rewards=[[1,3],[2,2]]，eps=0.000001
输出：adv=[[-0.999999...,0.999999...],[0,0]]
informative=[True,False]
```

浮点检查可使用容差；本接口不计算概率比、KL 或完整策略损失。

## 解题思路与参考答案

$\mathrm{std}\approx 0$ 说明整组全对或全错、没有相对差别，优势就该是 0，这一步更新无效；分母上的 `eps` 只防 NaN，造不出学习信号。所以实现时要在 group 维上标准化，同时把这种组标记出来，过滤掉或者重采。

比如一道题采 4 条，奖励是 `[1, 1, 1, 1]`。均值 1，分子全是 0，不管 `eps` 取多大，$A$ 都是 0。代码照样能跑，可这 4 条 rollout 的预算等于白花了。

## 组内标准化：维度要对，unbiased 要和论文一致

同一个输入提示采 $G$ 条，奖励 $r\in\mathbb{R}^{N\times G}$：

$$
A_{i}=\frac{r_{i}-\mathrm{mean}_{G}(r)}{\mathrm{std}_{G}(r)+\varepsilon}.
$$

mean 和 std 一定要在 group 维上求。把不同题混在一个 batch 里减全局均值，题目难度就会漏进优势里。

```python
import torch

def group_advantage(rewards, eps=1e-6):
    # rewards: [N_prompts, G]
    mean = rewards.mean(dim=1, keepdim=True)
    std = rewards.std(dim=1, keepdim=True, unbiased=False)
    adv = (rewards - mean) / (std + eps)
    informative = std.squeeze(1) > eps
    return adv, informative
```

`torch.std` 默认 `unbiased=True`，也就是除以 $G-1$。$G$ 小的时候，样本标准差和总体标准差数值不一样；$G=1$ 时 unbiased std 没有定义。实现要和 DeepSeekMath 或框架的约定一致，通常用 population std（`unbiased=False`）。$G=1$ 本来也不是 GRPO，见 `pt-grpo`，组大小 $n\gt 1$ 的定义见 `sys-rl-group-n`。

## $\mathrm{std}\approx 0$：过滤或改采样，别指望 eps

binary 的奖励分数（reward）下，全 0 或全 1 中心化后都是 0，`std=0`。加上 `eps` 以后 $A$ 还是约等于 0，因为分子本来就是 0，看起来「能跑」，但 informative 标志一定要记下来：零方差组占着采样轨迹（rollout）的预算。工程上会监控 zero-variance group rate，DAPO 的 Dynamic Sampling 就是让这些组少进训练 batch，见 `slime-dynamic-partial`、`byte-grpo-all-same-zero-adv`。

还有几个变体要心里有数。Dr.GRPO 这类 objective 可能去掉除以 std 这一步，只减均值，见 `pt-drgrpo`。多路奖励（正确性 + 格式 + 长度）要先定好：先合成一个标量再做 group-norm，还是每个分量单独 norm 再加权，两种做法的系数不能混着调。token 级通常把同一个 $A_i$ 广播到每个 token，别对每个 token 再减一次均值。

## 简单测试怎么写

把上面的实现保存为 `solution.py`，以下测试放在实现之后。数值测试使用参考实现相同的 PyTorch 或 NumPy 环境；浮点结果用带容差的比较。运行 `python3 solution.py`，成功时输出 `simple tests passed`，失败时按断言报错行定位。不要加 `-O`，它会跳过 `assert`。

奖励 [1,3] 用总体标准差归一化后约为 [-1,1]，均值为零；整组奖励相同则优势为零，informative=False。

```python
adv, informative = group_advantage(torch.tensor([[1., 3.], [2., 2.]]))
torch.testing.assert_close(adv[0], torch.tensor([-1., 1.]), atol=2e-6, rtol=1e-5)
torch.testing.assert_close(adv[1], torch.zeros(2))
assert informative.tolist() == [True, False]
print("simple tests passed")
```

## 追问

**`unbiased=True` 有什么影响？**
$G$ 小的时候数值偏大，$G=1$ 直接出 NaN，所以要和论文或 veRL 的定义对齐。

**把 eps 改成 $10^{-2}$，能不能制造出信号？**
不能。分子已经是 0，放大分母只会让结果更接近 0。要换题，或者调高温度把组采散。

**先组合 reward 还是先分别 norm？**
各分量尺度不同时，先分别 norm 更稳；先加权再 norm，大尺度的分量会主导组内排序。

**和 PPO 的价值评估模型（critic）比呢？**
GRPO 不训 $V(s)$，baseline 就是组均值。PPO 可以 $n=1$，见 `code-ppo-clip`。

**全对是不是说明已经学会了？**
对这道题来说是零信息。降难度或者动态重采，别去加学习率。

相关：`stepfun-grpo-loss-handwrite`（手撕完整 surrogate）、`code-ppo-grpo-gspo`（PPO / GRPO / GSPO 放进同一次更新，并对照 TRL 和 verl 的开关）
