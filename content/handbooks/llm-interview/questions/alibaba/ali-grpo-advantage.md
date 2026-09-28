---
id: ali-grpo-advantage
section: alibaba
order: 4
level: S
title: GRPO 的 Advantage 怎么算？为什么不能直接用 raw reward？
quick: >-
  同 prompt 采一组样本，用组内 reward 均值/方差做相对标准化得到 A。直接用 raw reward
  尺度不稳、同组不可比，也分不清「都还行」和「明显更好」。
tags:
  - Alibaba
  - GRPO
  - Advantage
realInterview: true
status: published
format: markdown
provenance: legacy-handbook-v2
updatedAt: 2026-08-21
sources:
  - title: ↗ 阿里国际大模型算法一面
    url: 'https://www.nowcoder.com/feed/main/detail/27a27fc44b8a4613ae790ba27add8850'
    type: legacy-reference
---

错法：「就是 reward」或「就是 PPO 的 GAE」。GRPO 用同一 prompt 的一组样本做相对标准化，代替 critic 的 $V(s)$。直接用 raw reward：尺度不稳、不同题不可比，也分不清「都还行」和「明显更好」。白板先写公式，再讲为何不用绝对分。完整 loss 见 `ali-grpo-loss`，空组见 `ali-dapo-allcorrect`。

## 组内标准化

对同一 $x$ 采样 $G$ 条输出，得到 $r_1,\ldots,r_G$，令

$$
A_i=\frac{r_i-\mathrm{mean}(r)}{\mathrm{std}(r)+\varepsilon}.
$$

$A_i$ 再广播到该回复的生成 token（`ali-credit-token`）。实现会有 baseline 变体、length 归一、$\varepsilon$ 防除零。RLOO 用「不含自己的组均值」，更接近教科书 baseline。组均值不是 Value Function：没有逐步 future return，也不条件于前缀状态。

不用 raw reward 的原因：不同 prompt 难度不同，绝对分不可比；reward 尺度漂移会让更新过猛或过弱；相对优势更贴近「在当前组里谁更好」，方差通常更可控。数学/代码这类可验证任务，同题多样本天然构成对照，所以能去掉 critic（相对 PPO 的工程简化）。

## 全对/全错与 $\sigma$ 的副作用

若 group 内全对或全错，$A\approx 0$，学习信号消失。这正是 DAPO 等要处理的 failure mode。$\sigma$ 归一还会改变题间权重：低方差题（几乎全对但有一条稍差）会被放大。Dr.GRPO 指出去掉 std、小心 length 归一，就是在修这把尺子。监控要同时看组内 std 和无效组比例，不要只看平均 $r$。

选型上：有可验证/可打分目标才值得 GRPO；只有示范轨迹应先 SFT，只有偏好对应 DPO（`ali-grpo-vs-sft`、`ali-ppo-dpo-grpo-ask`）。Agent 轨迹若只有最终成功，组内相对优势仍然糊，需要过程分，见 `ali-agent-final-reward`。

白板别把 $A$ 说成 GAE：GAE 用 $V(s_t)$ 对前缀做逐步归因；GRPO 的 $A_i$ 是整条回复相对同题其它回复。同一套 clip 目标，差在 baseline 从哪来。$\varepsilon$ 防的是除零，不是「给空组造信号」。全对组加上噪声 $A$ 会毁格式。监控报表要有组内 std、无效组比例、`pass@k-pass@1`，三者一起才能判断相对优势还在不在。

## 追问

- **$G$ 取多少？** 常见 4-16。太小估计吵，太大 rollout 贵。空组多时应先改题难度，而不是只加 $G$。
- **能减一个学出来的 $V$ 吗？** 能，那就接近 PPO。GRPO 的卖点是同题组统计换 critic；再加 $V$ 要说清长 CoT 上 $V(s)$ 好不好估。
- **reward 是 0/1 还是连续分？** 都可以。0/1 时组内差异更稀疏，更容易空组；连续/过程分能加密信号，但要防 hacking。
