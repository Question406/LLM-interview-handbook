---
id: baidu-dpo-chosen-curve
section: posttrain
order: 205
level: A
title: 百度文心：DPO 对齐训练曲线长什么样？正例概率一定会上升吗？
quick: "直接偏好优化（DPO） 优化的是 chosen 相对 rejected 的对数概率差，不是单独抬高 chosen 似然。正例 $\\log\\pi(y_w)$ 可能下降，只要相对间隔拉大就行；过长回答，以及靠刷间隔做 钻奖励规则的空子，都是常见病态。"
tags:
  - Baidu
  - DPO
  - 2025-2026
realInterview: true
status: published
format: markdown
updatedAt: 2026-08-21
sources:
  - title: 腾讯/百度/minimax 大模型算法面经总结帖
    url: https://www.nowcoder.com/feed/main/detail/8cab51ef9458459595cf81fda43da279
    type: candidate-first-hand
  - title: Direct Preference Optimization
    url: https://arxiv.org/abs/2305.18290
    type: primary
---

## 真题记录

- 公司：百度 · 文心一言（总结帖收录）
- 原始措辞：**“DPO 对齐训练的曲线是怎么样的，正例的概率会提升吗？”**

这块容易把 直接偏好优化（DPO） 当成 监督微调（SFT） 来读曲线：以为 chosen 的 $\log\pi(y_w)$ 必须单调上升，下降就等于训练失败。损失只看见 margin。它从反向 KL 约束的最优策略反解而来，允许整体概率质量搬家，见 `fund-kl-directions`。现场先写间隔公式，再声明要同时画四条曲线：margin、chosen/rejected 绝对 logp、平均长度、对 ref 的 KL。只报一条「正例概率」会被追问拆穿。

## 优化的是间隔，不是正例似然

核心项

$$
\Delta=\beta\log\frac{\pi_\theta(y_w\mid x)}{\pi_{\mathrm{ref}}(y_w\mid x)}-\beta\log\frac{\pi_\theta(y_l\mid x)}{\pi_{\mathrm{ref}}(y_l\mid x)},
$$

损失 $\mathcal{L}=-\log\sigma(\Delta)$。梯度鼓励拉大 $\Delta$，不保证 $\pi(y_w)$ 上升，更不保证它相对 SFT 上升。常见健康现象：chosen 与 rejected 的绝对 log-prob 双降，但 $\Delta$ 升、离线胜率升、对 ref 的反向 KL 缓升。这是 mode-seeking：两边都让出一点质量，间隔拉开，比「正例越来越像 SFT」更常见。$\beta$ 大则 $\Delta$ 难拉开、更贴 ref；$\beta$ 小则间隔涨得快，KL 也涨得快。

病态曲线要对照着讲。只压 $y_l$、不抬 $y_w$ 的质量，间隔被刷大，用户侧观感不变。靠拉长堆总 logp，长度和 $\Delta$ 一起涨，这是长度 bias。过拟合偏好噪声：离线胜率提高，但线上或留出集表现下降。三者都不是「正例概率没升」能概括的。

## 监控清单与长度

同时画：$\Delta$、chosen/rejected 平均 logp、平均长度、重复 n-gram、$D_{\mathrm{KL}}(\pi_\theta\|\pi_{\mathrm{ref}})$、下游 winrate。KL 方向仍是反向，不要改成对 ref 的 交叉熵损失（CE），否则曲线含义全变，见 `ant-kl-vs-ce`。缓解过长：长度归一、SimPO、显式长度惩罚、标注时写明「短而对优于长而对」，见 `baidu-simpo-vs-dpo-length`。不要只加 $\beta$，$\beta$ 管贴 ref 的幅度，不直接控制 token 数。若后续切 GRPO，间隔健康不等于有效组够：组内全是「长而对」时优势照样可以塌成零或被长度尾巴拽走，见 `sys-rl-group-n`。

## 追问

- **正例 logp 下降是不是训废了？** 不一定。看 $\Delta$、KL 和 holdout 胜率。三者一起掉才是崩；只掉绝对 logp 可能是健康的 seeking。
- **和 SFT 曲线差在哪？** SFT 的正向 CE 会推高示范似然；DPO 可以双降。把 DPO 曲线按 SFT 读，会误杀健康 run。
- **如何缓解过长？** 平均 logp、SimPO、长度惩罚或控长标注。只加 $\beta$ 或只加学习率无效。
- **要不要 online DPO？** 线上分布漂了就该刷新 pair。那已经接近偏好版 on-policy，算力账回到 强化学习（RL），不是「再训一晚 DPO」。
- **rejected 也降，会不会把有用说法一起忘掉？** 会。硬负样本要覆盖「像对的错法」，不要用随机垃圾当 $y_l$，否则模型容易扩大间隔，却可能损失有用能力。
