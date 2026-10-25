---
id: stepfun-grpo-loss-handwrite
section: rl-coding
order: 7
level: S
title: 阶跃星辰：手撕 GRPO 时 loss 和组内优势分别怎么写？
quick: "同一输入提示采 $G$ 条回答，奖励在组内标准化得到 $A_i$，再套 $\\min(\\rho A,\\mathrm{clip}(\\rho)A)$，KL 可以另加。没有 critic，baseline 就是组均值；$\\mathrm{std}=0$ 时整组梯度为 0，要过滤或改采样，光加 `eps` 只是假装有信号。"
tags:
  - StepFun
  - GRPO
  - Coding
realInterview: true
status: published
format: markdown
updatedAt: 2026-08-21
sources:
  - title: 阶跃星辰大模型算法实习一面
    url: https://www.nowcoder.com/feed/main/detail/5cb1ebe809fd402d844cce47380a926f
    type: candidate-first-hand
---

## 题目描述

实现最小 GRPO 策略损失 `grpo_loss(logp,old_logp,rewards,clip_eps=0.2,adv_eps=1e-6)`。面经只披露“手撕grpo”，以下序列级接口和归约方式为手册重构练习约定。

三个输入都是 `[N,G]` 的有限浮点 PyTorch 张量：同一行属于同一 prompt 的 G 条回答；logp 和 `old_logp` 是这些回答已计算好的当前/旧策略**序列对数概率**，rewards 是固定的回答奖励。N 为正、G>=2；`0 < clip_eps < 1`，`adv_eps`>0。输入差值保证指数有限。本题不再处理 token mask、时间移位或序列长度归约。

在每行内用总体标准差（分母G）计算优势：`A=(rewards-行均值)/(行标准差+adv_eps)`。定义 `rho=exp(logp-old_logp)`，返回 `min(rho*A,clamp(rho,1-clip_eps,1+clip_eps)*A)` 对 N×G 个元素平均后的负值。输出为可对 logp 求梯度的标量张量。旧策略和奖励由调用者固定；不包含 critic、value loss 或额外 KL 正则。

### 示例

```text
输入：logp=[[0,0]]，old_logp=[[0,0]]，rewards=[[1,1]]
输出：0

输入：logp=[[0,log(1.1)]]，old_logp=[[0,0]]，rewards=[[0,1]]
clip_eps=0.2，adv_eps=0.000001
输出：约-0.0499999
```

第二例的组内优势约为[-0.999998,0.999998]，用于明确损失的符号和数值约定。

## 解题思路与参考答案

## 真题记录

- 公司：阶跃星辰（StepFun）
- 团队 / 岗位：大模型算法实习
- 届别 / 流程：实习；一面
- 面试时间：原帖未披露；帖子发布于 2026-03-27
- 来源类型与可信度：牛客候选人原帖，B
- 原始措辞：手撕 **“top-p sampling、grpo”**

我会分两步写：先在 $G$ 维上把奖励标准化成组内优势，再写 PPO 式的 clipped surrogate，不写 value loss。GRPO 不训价值评估模型（critic），baseline 就是组内均值。常见的错法是把它写成带 critic 的 PPO，或者 `std=0` 时只加一个 `eps` 了事。现场顺序是先写优势张量，再写 `ratio.clamp` 和 `min`。

## 优势：在 $G$ 维标准化

同一输入提示采 $G$ 条回答，$r\in\mathbb{R}^{N\times G}$：

$$
A_i=\frac{r_i-\mathrm{mean}(r)}{\mathrm{std}(r)+\varepsilon}.
$$

`std` 用 population（`unbiased=False`），和论文、框架对齐。全对或全错时分子是 0，$A=0$，这一个 step 无效，要记下来并动态换题，见 `byte-grpo-all-same-zero-adv`。

## Loss：clipped surrogate，没有 critic

$$
\rho=\exp(\log\pi_\theta-\log\pi_{\mathrm{old}}),\qquad
L=\min\bigl(\rho A,\;\mathrm{clip}(\rho,1-\varepsilon,1+\varepsilon)A\bigr).
$$

目标是最大化 $L$，代码里写成 `-L.mean()`。可以再加一项到 ref 的 KL，系数单独调，见 `xiaohongshu-grpo-drop-kl`。Clip 不会把真实的 $\rho$ 拉回区间，只让越界且「有利」那一侧的梯度为 0，见 `code-ppo-clip`。

```python
import torch

def grpo_loss(logp, old_logp, rewards, clip_eps=0.2, adv_eps=1e-6):
    # logp/old_logp/rewards: [N, G]  (token 级则先在 seq 维 reduce 再广播 A)
    mean = rewards.mean(dim=-1, keepdim=True)
    std = rewards.std(dim=-1, keepdim=True, unbiased=False)
    adv = (rewards - mean) / (std + adv_eps)
    rho = (logp - old_logp).exp()
    unclipped = rho * adv
    clipped = rho.clamp(1 - clip_eps, 1 + clip_eps) * adv
    return -torch.minimum(unclipped, clipped).mean()
```

token 级的 $\log\pi$ 要对齐 completion token；用序列级 $\rho$ 的话，先对 token 求和再进 clip（GSPO 就是把比率收到序列级，见 `stepfun-rl-moe-gspo`）。两题一起出时，形状这样串：优势是 `[N,G]`，`rho` 同形，然后 `minimum`。

## 简单测试怎么写

把上面的实现保存为 `solution.py`，以下测试放在实现之后。数值测试使用参考实现相同的 PyTorch 或 NumPy 环境；浮点结果用带容差的比较。运行 `python3 solution.py`，成功时输出 `simple tests passed`，失败时按断言报错行定位。不要加 `-O`，它会跳过 `assert`。

整组奖励相同时优势都为零，损失应为零且有限；再用不相同的奖励和不同概率比率，确认存在有效学习信号。

```python
logp = torch.zeros(1, 2, requires_grad=True)
loss = grpo_loss(logp, torch.zeros(1, 2), torch.ones(1, 2))
torch.testing.assert_close(loss, torch.tensor(0.))
loss = grpo_loss(torch.tensor([[0., 0.1]], requires_grad=True), torch.zeros(1, 2), torch.tensor([[0., 1.]]))
assert torch.isfinite(loss) and loss.item() < 0
loss.backward()
print("simple tests passed")
```

## 追问

**和 PPO 差在哪？**
没有 critic，也没有 GAE，组内均值就是 baseline。PPO 可以 $n=1$，GRPO 不行，见 `sys-rl-group-n`。

**KL 放在哪？**
两种都有：加在 surrogate 外面当正则，或者像部分实现那样从奖励里扣。要说清楚你们用的是哪一种。

**$\log\pi$ 用 token 平均还是求和？**
要和采样长度、loss 聚合方式一致，见 `baidu-grpo-loss-agg`。混着用会让模型偏长或偏短。

**std=0 怎么办？**
过滤掉这个组，或者改采样。eps 只防 NaN，造不出信号。

**top-p 和 GRPO 先写哪个？**
先写对 nucleus 采样，再写 loss。采样错了，优势算得再对，也是在错的分布上更新。

相关：`code-sampling`（完整采样）、`code-grpo`、`stepfun-grpo-group-advantage`（组优势的边角情况）、`code-ppo-grpo-gspo`（GSPO 序列比和 TRL / verl 开关）、`stepfun-rl-moe-gspo`（MoE+强化学习（RL），和损失公式分开讲）
