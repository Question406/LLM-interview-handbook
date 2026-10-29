---
id: align-best-of-n
section: alignment
order: 13
level: A
title: 对齐：Best-of-N 推理时对齐，成本与 RM over-optimize
quick: 假设模型对同一问题生成五个回答，RM 从中选一个。Best-of-N 不改模型参数，它把更多 inference 计算花在产生候选和挑选回答上。
tags:
  - OpenAI
  - Inference
  - Best-of-N
  - Reward Model
  - 口述改写 2026-10-28
realInterview: false
status: published
format: markdown
updatedAt: '2026-10-28'
sources:
  - title: Scaling Laws for Reward Model Overoptimization
    url: 'https://arxiv.org/abs/2210.10760'
    type: primary
  - title: Training language models to follow instructions with human feedback
    url: 'https://arxiv.org/abs/2203.02155'
    type: primary
  - title: Direct Preference Optimization
    url: 'https://arxiv.org/abs/2305.18290'
    type: primary
---

## 回答思路

> **问题与场景：** 假设模型对同一问题生成五个回答，RM 从中选一个。
>
> **做法与原因：** 如果 RM 能正确排序，更多候选可能提高选中好答案的机会。
>
> **检查与取舍：** 我会固定生成预算，检查最终答案的独立正确性与选择成本，并比较不同 N 的收益。

## 可以这样回答

假设模型对同一问题生成五个回答，RM 从中选一个。Best-of-N 不改模型参数，它把更多 inference 计算花在产生候选和挑选回答上。

如果 RM 能正确排序，更多候选可能提高选中好答案的机会。但候选越多，也可能越容易找到能骗过 RM 的回答，所以不能只看最高 reward 是否上升。

我会固定生成预算，检查最终答案的独立正确性与选择成本，并比较不同 N 的收益。若 reward 涨了但答案质量下降，就需要先修评价或选择规则。

## 技术备查

Best-of-N 是在推理时多生成几条回答，再用 reward model 选一条，策略权重不变。它适合快速验证一种奖励是否有用，但预算增加后，质量与成本要分别检查，不能假定候选越多就越好。

策略 $\pi$ 按正常温度 sampling $N$ 条 $y_1,\ldots,y_N$，RM 打分后返回 $\arg\max_i r_\phi(x,y_i)$。因此改变的是输出分布，使它集中到 RM 喜欢的区域；$N=1$ 就是原策略。SFT、DPO、PPO 会改变 $\pi$，与它可以互补。Beam 优化模型自己的 logp，目标不同于 $r_\phi$，rejection sampling 则按阈值接收候选，BoN 的规则是固定预算取最大。

```python
def best_of_n(logps_rm, n):
    # logps_rm: [B, N]  scores from frozen RM
    idx = logps_rm.argmax(dim=-1)
    return idx
```

可验证任务能用对错或单测作 $r$，接近搜索；开放对话依赖 proxy RM，可能只挑中了它的偏好。DPO 的隐式奖励在同一 $x$ 下也可排序，因为 $Z(x)$ 公共，见 `align-dpo`，但不能跨 prompt 比绝对 $\log(\pi/\pi_{\mathrm{ref}})$。验收最好换独立 RM 或人工，避免选择与评估使用同一偏差。RM 训练见 `align-reward-model`。

## 多次 sampling 的成本与适用条件

朴素做法跑 $N$ 路 decode，生成 token 与耗时近线性增长。长系统提示和历史可以共享前缀 KV，只为分叉后的 response 付重复成本，见 `sys-prefix-cache`；continuous batching 能把各路放进同一 iteration，但活跃序列越多，显存越大，见 `openai-continuous-batching`。

我会先定总 token 预算，再定 $N$ 与单条最大长度。$N=64$ 配长回答可能打满 KV、推高 p95。可以让免费档用 $N=1$，难查询或付费档用较小的 $N$，短答案提前停，报告 throughput、p95 与 KV 页数。温度太低时，64 条可能几乎相同，先看 unique n-gram，确认多样性再加候选。

Gao 等人的研究把 BoN 与增加 RL 步数放到同类过优化问题中：proxy RM 分继续上升，held-out RM 或人工 gold 分却先升后降，见 `align-reward-hack`。更长回答更容易出现 RM 喜欢的 n-gram，length bias 也会被搜索放大，见 `align-length-bias`。因此扫 $N$ 时用 gold 曲线决定停止位置，可以加长度惩罚、按长度 normalization $r$，也可以保留 SFT 候选，减少偏离参考文风。

InstructGPT 用 BoN 作 RLHF 基线，这道题据此及 Gao 的工作整理。若再用 RM 排序生成 pair 来训 DPO，proxy 偏差会进入权重，风险比只做推理选择更持久，数据隔离与污染检查参照 `align-eval-contam`。

## 追问

**$N$ 越大越好吗？**
对 proxy 更容易高分，gold 可能过拐点后下降，要看独立评测。

**BoN 和 RL 哪个划算？**
低流量、快速试奖励时 BoN 直接；大流量、奖励稳定时，可以把能力训进 $\pi$，摊薄每次请求成本。

**过程奖励也能做吗？**
能按步骤搜索，见 `align-process-reward`，但步骤 RM 一样会过优化。

## 相关题

- [[align-overopt-rm]]：proxy 与 gold 分叉的 Goodhart 曲线。
- [[align-reward-model]]：RM 训练与可信的分差。
- [[align-grpo]]：也比较组内奖励，但会据此更新权重。
