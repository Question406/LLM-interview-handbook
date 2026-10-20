---
id: pt-trust-region-vs-drift-kl
section: posttrain
order: 222
level: S
title: PPO 里的 Trust-Region KL 和 Drift KL 是同一个东西吗？
quick: "不是。Trust-Region 相对每步替换的 $\\pi_{\\mathrm{old}}$，管单步别迈太大，PPO clip 近似它；Drift 相对冻结的 $\\pi_{\\mathrm{ref}}$，管长期偏离和 reward hacking。"
tags:
  - KL
  - PPO
  - GRPO
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-21
sources:
  - title: A Guide to Reinforcement Learning Post-Training for LLMs
    url: https://huggingface.co/blog/karina-zadorozhny/guide-to-llm-post-training-algorithms
    type: secondary
  - title: Trust Region Policy Optimization
    url: https://arxiv.org/abs/1502.05477
    type: primary
  - title: Proximal Policy Optimization Algorithms
    url: https://arxiv.org/abs/1707.06347
    type: primary
---

两套 KL 经常被写成同一个 $\beta\mathrm{KL}$，我会先拆「相对谁、哪一步、哪个方向」。把 PPO 的自适应 KL penalty 和 RLHF 目标里对 $\pi_{\mathrm{ref}}$ 的 KL 说成一回事，是这题最常见的翻车：前者管本步更新，后者管长期偏离 SFT 模型。Clip、penalty、controller 都只是实现，不能替代说清锚定对象。Trust-region 问这一步相对 $\pi_{\mathrm{old}}$ 迈得大不大；drift 问整段训练相对冻结 SFT 漂了多远。名字都带 KL 或 adaptive，锚点却完全不同，混用会把监控曲线和调参旋钮对错号。

## Trust-Region：相对上一把策略

TRPO 的硬约束是：本步新策略不能离 **行为策略 / 上一迭代** $\pi_{\mathrm{old}}$ 太远。常用

$$
D_{\mathrm{KL}}(\pi_{\mathrm{old}}(\cdot\mid s)\,\|\,\pi_\theta(\cdot\mid s))\le\delta.
$$

$P=\pi_{\mathrm{old}}$ 固定，优化 $Q=\pi_\theta$，这是正向、mean-seeking：旧策略认为好的动作，新策略不能一步把概率压没。PPO 的 ratio clip 是它的一阶工程近似，**不一定真算 KL**。PPO 论文里的 KL-penalty 变体则把 $\beta\,D_{\mathrm{KL}}(\pi_{\mathrm{old}}\|\pi_\theta)$ 加进 surrogate，并按本步实测 KL 调 $\beta$，让每次更新落在目标带附近。自适应的是 **相对 $\pi_{\mathrm{old}}$ 的一步 KL**，旧策略每个 iteration 都会换成当前采样策略，锚定在滑动。

trust-region 问的是「这一步迈得大不大」，不是「离 SFT 多远」。$\pi_{\mathrm{old}}$ 本身可能已经漂离参考；只限制相对旧策略，长期仍可以慢慢离开 $\pi_{\mathrm{ref}}$，所以后面必须另加 drift 项。PPO 原论文里的 adaptive KL penalty 也属于这一支：它盯的是本 batch 相对行为策略的 KL，目标半径通常很小，用来代替或辅助 clip。把这个 controller 的曲线拿来当「对齐有没有黑奖」会误诊：step-KL 低只说明这几步更新幅度较小，不说明还在 SFT 附近。面试被追问「你们 PPO 不是已经有 KL 了吗」时，先问对方说的是 clip、penalty 还是 奖励里那一项，再画两个锚点。

## Drift：相对冻结参考的目标项

InstructGPT / 标准 RLHF 的约束目标是

$$
\max_\pi\ \mathbb{E}_{y\sim\pi}[r(x,y)]-\beta\,D_{\mathrm{KL}}\big(\pi(\cdot\mid x)\,\|\,\pi_{\mathrm{ref}}(\cdot\mid x)\big).
$$

$\pi_{\mathrm{ref}}$ 通常是 **冻结 SFT**，整段训练不变。方向是反向 $D_{\mathrm{KL}}(\pi_\theta\|\pi_{\mathrm{ref}})$：允许忘掉参考里的坏峰，但不许发明参考 support 外的高分胡话。经典实现是扣进 token 奖励 $r-\beta\log(\pi_\theta/\pi_{\mathrm{ref}})$；GRPO 常把同一项放进损失中的 $k_3$。DPO 把同一约束写进 $\beta\log(\pi/\pi_{\mathrm{ref}})$ 间隔，见 `pt-rlhf-why-reverse-kl`。

这项目的是减少利用奖励漏洞和语言质量下降的问题，不是防单次更新过大。$\beta$ 太大策略贴死参考、像没有通过强化学习获得改善；太小则 KL 飙升、变长空话，见 `pt-kl-too-large-too-small`。InstructGPT 一类流水线会对 **这一项** 再套自适应 controller：实测 $D_{\mathrm{KL}}(\pi_\theta\|\pi_{\mathrm{ref}})$ 高于目标就加大 $\beta$，反之减小。名字也叫 adaptive KL，锚定对象却是冻结参考，和 PPO-penalty 相对 $\pi_{\mathrm{old}}$ 的自适应不是同一个闭环。

工程上 token 级实现常是 $r_t-\beta(\log\pi_\theta-\log\pi_{\mathrm{ref}})$，只加在 response mask 上；输入提示段若也扣 KL，等于把「读懂问题」当漂移来罚。监控 ref-KL 要用同一 mask，否则数字和梯度对不上。DPO 不显式写奖励，但 $\beta\log(\pi/\pi_{\mathrm{ref}})$ 仍是 drift 项，不是 trust-region。

## 自适应 KL 调的是系数，不是把两套 KL 合成一套

听到「我们用了 adaptive KL」，先问：**控制器看的是哪一条 KL？** 三种常见实现不要混：

- **PPO-penalty：** 监控 $D_{\mathrm{KL}}(\pi_{\mathrm{old}}\|\pi_\theta)$，目标是本步 trust-region 半径。
- **RLHF controller：** 监控 $D_{\mathrm{KL}}(\pi_\theta\|\pi_{\mathrm{ref}})$，目标是长期离 SFT 多远。
- **PPO clip：** 往往不算 KL，只用 ratio 截断 surrogate；它可以和 drift 项同时在。

Clip 为 0 时 drift 项仍可能在工作；drift $\beta=0$ 时 clip 仍限制单次更新。一个管步长，一个管锚点。把 clip 说成「就是 KL」、或把 controller 说成「就是 RLHF 目标」，都算没答到点上。监控上分两条曲线：对 $\pi_{\mathrm{old}}$ 的 step-KL，和对 $\pi_{\mathrm{ref}}$ 的 ref-KL。只报一个「平均 KL」无法判断是更新过猛还是已经偏离参考模型并利用奖励漏洞。

对照三问：相对 **上一迭代** 还是相对 **初始 SFT**；期望从 **旧策略** 取还是从 **当前策略** 取；系数是固定、按 step 自适应，还是按 ref-KL 自适应。白板可以画两列：左列 $\pi_{\mathrm{old}}$ 每步替换、正向 KL、管步长；右列 $\pi_{\mathrm{ref}}$ 全程冻结、反向 KL、管锚点。自适应只出现在系数那一行，不出现在「这是不是同一项 KL」那一行。GRPO 若同时有 clip 和 $k_3$，仍然是这两列都在，只是优势估计换成了组内归一化。把 $k_3$ 说成 trust-region，或把 clip 说成防 hacking，都是把两列抄到同一格里。

汇报实验时分开画 step-KL 与 ref-KL：前者跟学习率、epoch、clip 走，后者跟 $\beta$、奖励尺度、是否黑奖走。只给一条「平均 KL」的训练图，面试官无法判断你在约束哪一种偏离。若被问「自适应 KL 是不是 RLHF 标配」，答：controller 只是调系数的方法，必须声明监控的是 $\pi_{\mathrm{old}}$ 还是 $\pi_{\mathrm{ref}}$；InstructGPT 调的是后者，原版 PPO-penalty 调的是前者。现场先否定「是同一个 $\beta\mathrm{KL}$」，再分别给出锚点、方向、实现：clip 或 PPO-penalty 管一步，reward 里的 $\log(\pi/\pi_{\mathrm{ref}})$ 管长期漂移。两套可以同时开，监控必须分两条曲线；调参时不要用 step-KL 去决定 drift 的 $\beta$，也不要用 ref-KL 去决定 clip 范围。

## 追问

- **PPO clip 算不算 KL？** 不算。它是对 importance ratio 的一阶截断，意图近似 trust-region，实现里可以完全不计算 $D_{\mathrm{KL}}$。Clip fraction 高说明本步更新猛，和 ref-KL 大不是同一诊断。Clip 关掉之后若 ref-KL 仍可控，说明 drift 项还在干活，不能说「没有 KL 了」。自适应 KL penalty 若盯的是 $\pi_{\mathrm{old}}$，同样不是 drift 项。
- **自适应 $\beta$ 改的是哪一项？** 必须说监控对象。相对 $\pi_{\mathrm{old}}$ 的 controller 钉不住长期漂移；相对 $\pi_{\mathrm{ref}}$ 的 controller 也不保证单次更新安全。见 `pt-adaptive-kl-controller`。名字都叫 adaptive KL 时，先画锚点再谈系数。
- **GRPO 的 $k_3$ 是哪一种？** 通常是 drift：loss 里对冻结参考的 token 级反向 KL，不是对 $\pi_{\mathrm{old}}$ 的 trust-region。Clip 如果还在，那是另一套。把 $k_3$ 调大相当于加大 RLHF 目标里的 $\beta$，不是把 PPO 的 step 半径改小。
- **能不能只留一个？** 只留 clip：策略可以缓慢离开 SFT。只留 drift：单次更新仍可能过猛、重要性权重失效。对齐配方里两者常同时在，见 `pt-ppo-clip`。关掉其中一个时，要明确剩下那个还在约束哪一种偏离，并改监控图。
