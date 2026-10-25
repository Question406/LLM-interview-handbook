---
id: ali-grpo-kl-vs-ppo
section: posttrain
order: 6
level: A
title: GRPO 的 KL 和 PPO 的 KL 是一模一样的吗？
quick: "目标相同，都是约束 $\\pi$ 靠近参考或旧策略，但实现细节常不一样：参考对象是 $\\pi_{\\mathrm{ref}}$ 还是 $\\pi_{\\mathrm{old}}$，在 token 还是 sequence 上估，进损失（loss）还是做 early-stop。我会先说清自己用的是哪种实现。"
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

不完全一样。两者都在限制 $\pi$ 偏移过大，但锚定对象、方向和作用位置经常不同：相对 $\pi_{\mathrm{ref}}$ 还是 $\pi_{\mathrm{old}}$，在 token 还是 sequence 上估，进损失（loss）还是做 early-stop。所有叫 KL 的项并不共用同一个 $\beta$，面试时我会先说清自己用的是哪种实现。

白板上先画两个锚。$\pi_{\mathrm{old}}$ 是本批采样轨迹（rollout）的行为策略，$\pi_{\mathrm{ref}}$ 通常是冻结的监督微调（SFT）模型。PPO 的 clip 近似一个相对 $\pi_{\mathrm{old}}$ 的信任域，本步 $\rho=\pi_\theta/\pi_{\mathrm{old}}$ 不能离 1 太远。基于人类反馈的强化学习（RLHF）式的 PPO 还常在奖励里减去 $\beta\log(\pi_\theta/\pi_{\mathrm{ref}})$，这是相对冻结 SFT 的 drift KL，方向是 $D_{\mathrm{KL}}(\pi_\theta\|\pi_{\mathrm{ref}})$。GRPO 继承了 clip（相对 old），DeepSeekMath 把相对 ref 的 $k_3$ 近似 KL 直接加进 loss，没有扣进奖励分数（reward）。名字都带 KL，锚点不是同一个。两者同时出现时，clip / 信任域管本步，ref KL 管长期漂离。这两套 KL 的系统拆分见 `pt-trust-region-vs-drift-kl`，GRPO loss 的骨架见 `ali-grpo-loss`。

实现上还有几处常见差异。参考对象上，对齐阶段常用冻结 SFT 作 $\pi_{\mathrm{ref}}$，PPO 实现里也常见相对 $\pi_{\mathrm{old}}$ 的近似 KL。估计方式上，有 token-level 平均 KL、序列级 KL，或者 $k_1/k_2/k_3$ 近似，系数 $\beta$ 的调度也不同。作用方式上，有的进 loss，有的做 target / 阈值 early-stop，有的自适应调 $\beta$；DAPO 一类甚至去掉了 KL penalty，改靠 clip 和动态采样。Qwen GSPO 把 $\rho$ 改到序列级，KL / clip 的粒度也会跟着变，讲的时候同样先说锚点。所以别背「GRPO 的 KL 等于 PPO 的 KL」，要说「我这份代码里 KL 加在哪、相对谁」。

阿里面经还喜欢追问你监控哪些指标，用来判断 KL 项过强还是过弱。KL 过大，模型不学习，reward 不动；过小，长度爆炸、格式崩、开始钻奖励规则的空子（`ali-reward-hacking`）。监控清单是相对 old 的 KL（本步是否过大）、相对 ref 的 KL（是否漂离语言）、entropy、reward、崩坏 / 长度。四条曲线对不上号，多半是把两套 KL 调反了。重要性比 $\rho$ 爆炸是另一条线，见 `ali-importance-sampling`。

## 追问

**只有 clip 没有 ref KL 行不行？**
可以短训。长训容易漂离可用的语言分布，过程奖励能被 hack 时尤其明显。

**$\beta$ 怎么调？**
看 KL 曲线和崩坏率，别背一个常数。锚点越旧，同样的 $\beta$ 越容易把探索掐死。

**adaptive KL 是不是把两套合成了一套？**
不是。它通常只调其中一个系数，锚定对象没变。
