---
id: ali-grpo-kl-vs-ppo
section: alibaba
order: 6
level: A
title: GRPO 的 KL 和 PPO 的 KL 是一模一样的吗？
quick: >-
  目标都是约束 $\pi$ 靠近参考/旧策略，但实现细节常不同：参考对象（$\pi_{\mathrm{ref}}$ vs $\pi_{\mathrm{old}}$）、估计位置（token/sequence）、是否进 loss
  或做 early-stop。我会说清自己用的实现。
tags:
  - Alibaba
  - GRPO
  - PPO
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

错法：所有叫 KL 的项都是同一个 $\beta$。目标都是约束 $\pi$ 别跑飞，但锚定对象、方向、作用位置经常不同：$\pi_{\mathrm{ref}}$ vs $\pi_{\mathrm{old}}$、token vs sequence、进 loss vs early-stop。我会说清自己用的实现。两套 KL 的系统拆分见 `pt-trust-region-vs-drift-kl`；GRPO loss 骨架见 `ali-grpo-loss`。

## 相似点：防更新过猛和奖励劫持

PPO clip 近似相对 $\pi_{\mathrm{old}}$ 的信任域：本步 $\rho=\pi_\theta/\pi_{\mathrm{old}}$ 不能离 1 太远。RLHF 式 PPO 还常在奖励里减 $\beta\log(\pi_\theta/\pi_{\mathrm{ref}})$，这是相对冻结 SFT 的 drift KL，方向是 $D_{\mathrm{KL}}(\pi_\theta\|\pi_{\mathrm{ref}})$。GRPO 继承 clip（相对 old），DeepSeekMath 把相对 ref 的 $k_3$ 近似 KL 加进 loss，而不是扣进 reward。名字都带 KL，锚点不是同一个。

## 常见实现差异

- 参考谁：对齐阶段常用冻结 SFT 作 $\pi_{\mathrm{ref}}$；PPO 实现里也常见相对 $\pi_{\mathrm{old}}$ 的近似 KL。两者同时出现时，clip/信任域管本步，ref KL 管长期漂离。
- 怎么估：token-level 平均 KL、序列级 KL、或 $k_1/k_2/k_3$ 近似；系数 $\beta$ 调度也不同。
- 作用方式：有的进 loss，有的做 target/阈值 early-stop，有的自适应调 $\beta$。DAPO 一类甚至去掉 KL penalty，改靠 clip 与动态采样。

阿里面经喜欢追：你监控哪些指标（KL、entropy、reward、崩坏率）来判断 KL 项是否过强/过弱。KL 过大：不学习、reward 不动。过小：长度爆炸、格式崩、reward hacking（`ali-reward-hacking`）。重要性比 $\rho$ 爆炸是另一条线，见 `ali-importance-sampling`。

## 白板怎么收

先画两个锚：$\pi_{\mathrm{old}}$（本批 rollout 的行为策略）和 $\pi_{\mathrm{ref}}$（通常冻结 SFT）。然后说「我这份代码里 KL 加在哪、相对谁」。不要背「GRPO 的 KL 等于 PPO 的 KL」。Qwen GSPO 把 $\rho$ 改到序列级，KL/clip 的粒度也会跟着变，仍要先说锚点。监控清单：相对 old 的 KL（本步是否过大）、相对 ref 的 KL（是否漂离语言）、entropy、reward、崩坏/长度。四条曲线对不上号，多半是把两套 KL 调反了。

## 追问

- **只有 clip 没有 ref KL 行不行？** 可以短训。长训容易漂离可用语言分布，尤其是过程奖励可 hack 时。
- **$\beta$ 怎么调？** 看 KL 曲线和崩坏率，不要背一个常数。锚点越旧，同样 $\beta$ 越容易把探索掐死。
- **adaptive KL 是不是把两套合成一套？** 不是。它通常只调某一个系数，并不改变锚定对象。
