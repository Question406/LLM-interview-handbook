---
id: pt-trust-region-vs-drift-kl
section: posttrain
order: 222
level: S
title: PPO 里的 Trust-Region KL 和 Drift KL 是同一个东西吗？
quick: "是两样东西。Trust-Region 相对每步都会替换的 $\\pi_{\\mathrm{old}}$，管单步别迈太大，PPO clip 是它的近似；Drift 相对冻结的 $\\pi_{\\mathrm{ref}}$，管长期偏离和 reward hacking。两者可以同时开，监控要分两条曲线。"
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

不是同一个东西。Trust-region KL 相对的是每一步都会替换的 $\pi_{\mathrm{old}}$，管这一步迈得大不大；drift KL 相对的是冻结的 SFT 模型 $\pi_{\mathrm{ref}}$，管整段训练漂了多远。两套 KL 经常被写成同一个 $\beta\mathrm{KL}$，所以我会先拆三件事：相对谁、哪一步、哪个方向。把 PPO 的自适应 KL penalty 和 RLHF 目标里对 $\pi_{\mathrm{ref}}$ 的 KL 说成一回事，是这题最常见的翻车。clip、penalty、controller 都只是实现，说清锚定对象这一步省不掉；名字都带 KL 或 adaptive，锚点却完全不同，混用会把监控曲线和调参旋钮对错号。

一个直观的情形：每一步更新都很温和，step-KL 一直很低，可很多步走下来，策略离 SFT 已经很远，开始靠空话刷奖励。只看 trust-region 发现不了这件事，要靠 drift 项。

## Trust-region：相对上一版策略

TRPO 的硬约束是，本步的新策略不能离行为策略、也就是上一迭代的 $\pi_{\mathrm{old}}$ 太远。常用的写法是

$$
D_{\mathrm{KL}}(\pi_{\mathrm{old}}(\cdot\mid s)\,\|\,\pi_\theta(\cdot\mid s))\le\delta.
$$

这里 $P=\pi_{\mathrm{old}}$ 固定，优化 $Q=\pi_\theta$，是正向、mean-seeking：旧策略认为好的动作，新策略不能一步把概率压没。PPO 的 ratio clip 是它的一阶工程近似，不一定真去算 KL。PPO 论文里的 KL-penalty 变体则把 $\beta\,D_{\mathrm{KL}}(\pi_{\mathrm{old}}\|\pi_\theta)$ 加进 surrogate，按本步实测的 KL 调 $\beta$，让每次更新落在目标带附近，目标半径通常很小，用来代替或辅助 clip。它自适应的是相对 $\pi_{\mathrm{old}}$ 的一步 KL，而旧策略每个 iteration 都会换成当前的采样策略，锚点一直在滑动。

所以 $\pi_{\mathrm{old}}$ 本身可能早就漂离了参考，只限制相对旧策略的距离，长期还是可以慢慢离开 $\pi_{\mathrm{ref}}$，后面必须另加 drift 项。拿这个 controller 的曲线去判断「对齐有没有黑奖」会误诊，step-KL 低只说明这几步更新幅度小，说明不了还在 SFT 附近。面试被追问「你们 PPO 不是已经有 KL 了吗」，先问对方说的是 clip、penalty 还是奖励里那一项，再把两个锚点画出来。

## Drift：相对冻结参考的目标项

InstructGPT / 标准 RLHF 的约束目标是

$$
\max_\pi\ \mathbb{E}_{y\sim\pi}[r(x,y)]-\beta\,D_{\mathrm{KL}}\big(\pi(\cdot\mid x)\,\|\,\pi_{\mathrm{ref}}(\cdot\mid x)\big).
$$

$\pi_{\mathrm{ref}}$ 通常是冻结的 SFT，整段训练不变。方向是反向的 $D_{\mathrm{KL}}(\pi_\theta\|\pi_{\mathrm{ref}})$，允许忘掉参考里的坏峰，但不许发明参考 support 外面的高分胡话。经典实现是扣进 token 奖励 $r-\beta\log(\pi_\theta/\pi_{\mathrm{ref}})$；GRPO 常把同一项以 $k_3$ 的形式放进损失；DPO 把同一个约束写进 $\beta\log(\pi/\pi_{\mathrm{ref}})$ 的间隔里，见 `pt-rlhf-why-reverse-kl`。DPO 虽然不显式写奖励，这一项仍然是 drift 项。

这一项是为了减少钻奖励漏洞和语言质量下降，防单次更新过大不归它管。$\beta$ 太大，策略贴死参考，像没经过强化学习改善；太小，KL 飙升、回答变成长空话，见 `pt-kl-too-large-too-small`。InstructGPT 一类流水线会对这一项再套一个自适应 controller：实测的 $D_{\mathrm{KL}}(\pi_\theta\|\pi_{\mathrm{ref}})$ 高于目标就加大 $\beta$，低了就减小。它也叫 adaptive KL，可锚定的是冻结参考，和 PPO-penalty 相对 $\pi_{\mathrm{old}}$ 的自适应是两个闭环。

工程上，token 级实现常写成 $r_t-\beta(\log\pi_\theta-\log\pi_{\mathrm{ref}})$，只加在 response mask 上。输入提示段也扣 KL 的话，等于把「读懂问题」当漂移来罚。监控 ref-KL 也要用同一个 mask，不然数字和梯度对不上。

## 自适应 KL 调的只是系数

听到「我们用了 adaptive KL」，我会先问控制器看的是哪一条 KL。常见的有三种：PPO-penalty 监控 $D_{\mathrm{KL}}(\pi_{\mathrm{old}}\|\pi_\theta)$，目标是本步的 trust-region 半径；RLHF controller 监控 $D_{\mathrm{KL}}(\pi_\theta\|\pi_{\mathrm{ref}})$，目标是长期离 SFT 多远；PPO clip 往往根本不算 KL，只用 ratio 截断 surrogate，它可以和 drift 项同时存在。

clip 为 0 时 drift 项可能还在工作；drift 的 $\beta=0$ 时，clip 照样限制单次更新。一个管步长，一个管锚点，把 clip 说成「就是 KL」，或者把 controller 说成「就是 RLHF 目标」，都没答到点上。

白板上可以画两列。左列是 $\pi_{\mathrm{old}}$，每步替换，正向 KL，管步长；右列是 $\pi_{\mathrm{ref}}$，全程冻结，反向 KL，管锚点。clip 或 PPO-penalty 管一步，reward 里的 $\log(\pi/\pi_{\mathrm{ref}})$ 管长期漂移。对照着问三个问题：相对上一迭代还是相对初始 SFT；期望从旧策略取还是从当前策略取；系数是固定的、按 step 自适应，还是按 ref-KL 自适应。自适应只出现在系数那一行，和「这是不是同一项 KL」无关。GRPO 同时有 clip 和 $k_3$ 时，两列都在，只是优势估计换成了组内归一化；把 $k_3$ 说成 trust-region，或者把 clip 说成防 hacking，都是把两列抄进了同一格。

汇报实验时，step-KL 和 ref-KL 分开画。前者跟着学习率、epoch、clip 走，后者跟着 $\beta$、奖励尺度、有没有黑奖走。只给一条「平均 KL」，面试官判断不了你是更新太猛，还是已经偏离参考在钻奖励漏洞。调参时也别拿 step-KL 去定 drift 的 $\beta$，别拿 ref-KL 去定 clip 的范围。被问「自适应 KL 是不是 RLHF 标配」，可以答：controller 只是调系数的办法，要说明监控的是 $\pi_{\mathrm{old}}$ 还是 $\pi_{\mathrm{ref}}$，InstructGPT 调的是后者，原版 PPO-penalty 调的是前者。

## 追问

**PPO clip 算不算 KL？**
不算。它是对 importance ratio 的一阶截断，意图是近似 trust-region，实现里可以完全不算 $D_{\mathrm{KL}}$。clip fraction 高说明本步更新猛，和 ref-KL 大是两种诊断。关掉 clip 后 ref-KL 仍然可控，说明 drift 项还在干活，不能说「没有 KL 了」。自适应 KL penalty 如果盯的是 $\pi_{\mathrm{old}}$，同样不是 drift 项。

**自适应 $\beta$ 改的是哪一项？**
先说清监控对象。相对 $\pi_{\mathrm{old}}$ 的 controller 钉不住长期漂移，相对 $\pi_{\mathrm{ref}}$ 的 controller 也保证不了单次更新安全，见 `pt-adaptive-kl-controller`。名字都叫 adaptive KL 时，先画锚点再谈系数。

**GRPO 的 $k_3$ 算哪一种？**
通常是 drift，就是 loss 里对冻结参考的 token 级反向 KL，跟相对 $\pi_{\mathrm{old}}$ 的 trust-region 无关；clip 如果还在，那是另一套。把 $k_3$ 调大，相当于加大 RLHF 目标里的 $\beta$，PPO 的步长半径并没变小。

**两个只留一个行不行？**
只留 clip，策略可以缓慢离开 SFT；只留 drift，单次更新仍可能过猛，重要性权重失效。对齐配方里两者常常同时在，见 `pt-ppo-clip`。关掉其中一个时，要说清剩下那个还在约束哪种偏离，并改掉监控图。
