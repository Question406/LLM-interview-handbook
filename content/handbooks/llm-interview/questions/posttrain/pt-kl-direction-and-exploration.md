---
id: pt-kl-direction-and-exploration
section: posttrain
order: 41
level: S
title: 为什么常见 reverse-KL reference regularization 可能让 RLVR 困在 base-model support？什么时候考虑不同 KL 方向或 reference reweighting？
quick: "reverse KL 倾向留在 reference 的高概率模式附近，稳定但可能抑制稀有新策略。若高 K 表明好轨迹稀少且 reward 可靠，可探索更宽的正则或重加权；若 reward 噪声大，过度扩张会直接放大 hacking。"
tags:
  - KL
  - Exploration
  - RLVR
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-21
sources:
  - title: Unlocking Reasoning via RL Exploration
    url: https://arxiv.org/abs/2510.03865
    type: primary
  - title: Direct Preference Optimization
    url: https://arxiv.org/abs/2305.18290
    type: primary
---

别把 KL 当成「再调一个系数」。方向决定惩罚落在哪一类 token 上：常见的 reverse KL 护栏会让策略不敢离开 $\pi_{\mathrm{ref}}$ 的高概率区域，于是稀有但可验证的正确路径采不到。这和「KL 太大所以学不动」是两件事。面试里把 $\beta$ 调小、看到训练 reward 上涨就宣布探索成功，最容易被追问 Pass@K 和熵：reward 可以来自更频繁地重复 reference 里已经会的题型，而不是 support 变宽。基于可验证奖励的强化学习（RLVR） 依赖长尾成功被采到；mode-seeking 正则和这个需求是对着干的，只有在奖励极干净、已经不缺覆盖时才该把反向 KL 当稳定器。

## reverse KL 为什么是 mode-seeking

基于人类反馈的强化学习（RLHF） / RLVR 里最常见的惩罚是

$$
D_{\mathrm{KL}}(\pi_\theta\|\pi_{\mathrm{ref}})=\mathbb{E}_{y\sim\pi_\theta}\big[\log\pi_\theta(y)-\log\pi_{\mathrm{ref}}(y)\big].
$$

期望在当前策略上取。$\pi_\theta$ 把质量放到 $\pi_{\mathrm{ref}}\approx 0$ 处，$\log$ 比会出现数值异常，所以策略不敢发明 reference 几乎不会说的续写。反过来，$\pi_{\mathrm{ref}}$ 有、$\pi_\theta$ 不去的那些峰根本不进期望，策略可以丢掉它们。这就是 mode-seeking：锁住参考分布里已经比较亮的模式。白板推导见 `fund-kl-directions`，对齐为什么特意选这个方向见 `pt-rlhf-why-reverse-kl`。

对聊天对齐，这是优点：不想覆盖 监督微调（SFT） 里残留的有害峰。对 RLVR 探索则可能是缺点：正确解若落在 base 的长尾，reverse KL 会把采样压回常见但解不出的套路。难题的正确轨迹可能在参考分布的低概率区域。只优化 Pass@1 容易进一步强化已有模式，需要看大 K 的曲线，判断稀有正确路径是否仍能被采到。聊天对齐通常希望收窄模式；推理强化学习有时需要扩大探索范围，前提是奖励可靠。

## 何时会困在 base support

RLVR 靠「偶尔采到可验证成功 → 提高该轨迹概率」。若成功轨迹相对 $\pi_{\mathrm{ref}}$ 的概率极低，两项会同时发生：

- Pass@1 几乎不动，但 Pass@K 在很大的 $K$ 上才翘头，说明覆盖率在长尾，不是不会算。
- 加大 $\beta$ 或始终挂着强 reverse KL 后，熵下降、模式变少、长度和套话上升，K 曲线也被压扁。

这时「稳定」来自 support 收缩，不是来自学到了新策略。不要把 KL 变小、reward 变高自动读成探索成功：分布可能只是在 reference 的几个峰上刷分。一个有用的对照实验是：冻结 KL 系数，只把采样温度或 $n$ 增大，看高 K coverage 是否出现。若更大采样也挖不出正确轨迹，瓶颈在 seed 或题目，改 KL 方向无效；若能挖出而训练时采不到，才轮到正则过紧。

## 放宽之前先测什么

决定换方向、降 $\beta$、做 reference reweighting 或单独开 exploration phase 之前，先回答三个问题：

1. **Reward 的 false positive 有多高？** 规则 checker 的盲区、奖励模型（RM） 的风格偏置。噪声大时，扩张 support 等于给 hacking 开更大搜索空间，见 `pt-reward-ood-failure`。
2. **高 K coverage 是否真的存在？** 若 $K$ 已经很大仍几乎没有正确候选，瓶颈是 seed / 题目难度 / 验证器（verifier），不是 KL 方向。
3. **分布外数据（OOD，即与训练数据明显不同的数据） 与安全是否在回归？** 放宽正则必须配更密的 held-out 与 safety eval，不能只看训练 reward。

可尝试的手段包括：更小或自适应的 $\beta$（`pt-adaptive-kl-controller`）、正向或对称散度、对稀有高回报轨迹升权、先无 KL 探索再收紧。每一种都要把 verifier 收严，而不是只改公式。探索阶段建议设短预算和硬停止条件：gold 指标或安全评测一掉就收紧，而不是「先放飞再看」。和无 KL 的 DAPO 类配方衔接时，要承认你是在用数据与奖励质量换正则，不是发现了反向 KL 的数学错误。

不要把 PPO 的 KL 改成交叉熵来「换方向」：那会连采样分布一起反掉，见 `ant-kl-vs-ce`。现场若被要求手写惩罚项，先写期望在 $\pi_\theta$ 上，再写 $\log\pi_\theta-\log\pi_{\mathrm{ref}}$，最后才乘 $\beta$。左右写反是这题最常见的白板事故，比记不住公式更致命。

## 监控上怎么区分「探索」和「漂移」

不能只看 Pass@1。同时看：

- $K$ 曲线：Pass@1 不动而大 $K$ 在涨，是覆盖在长尾，KL 可能正在把这条尾巴掐掉。
- 熵、唯一轨迹数、n-gram 多样性：掉下去却伴着训练 reward 上升，多半是 mode-seeking 刷已知套路。
- 长度：变长不一定是更深搜索，也可能是在 reference 风格里注水，见 `pt-reasoning-token-cost-frontier`。
- KL 数值本身：很小说明贴着 $\pi_{\mathrm{ref}}$；很大且 gold 指标掉，是漂移而不是探索。
- Reward 与真实成功率的偏离：proxy 还在涨、可执行准确率不动，就是 hacking，再放宽 KL 会加速。

把这五项画在同一张训练曲线上，比单独汇报 $\beta$ 更有说服力。探索阶段允许熵上升，但 gold 与安全必须同时在图上，否则无法区分「在搜」和「在漂」。熵上升而 gold 不动，优先当 hacking 而不是当突破。安全切片也要进同一张图，否则探索阶段会把有害峰一起点亮。

Reference reweighting 的直觉：KL 项里 $\log\pi_{\mathrm{ref}}$ 对常见无回报 token 权太重时，把这些位置的参考概率下调，或对「最终可验证成功」的前缀上调，让护栏少误伤长尾正确路径。它改变的是锚定的形状，不是把反向 KL 偷偷换成正向。重加权要用独立于训练 reward 的信号，例如 held-out 成功标签，否则会把 hacking 前缀越加越亮。做完之后仍要看 K 曲线：若只是 Pass@1 涨、大 $K$ 不动，说明还在刷已知峰，重加权没有把 support 撑开。

## 追问

- **只看 Pass@1 为什么不够？** Pass@1 被 mode-seeking 优化得很漂亮时，K 曲线、熵、唯一轨迹数可能已经塌了。要把覆盖率和选择能力分开看，方法与 `pt-best-of-n-decomposition` 相同。Pass@1 涨、Pass@K 跌，常常是 support 收缩而不是变强。
- **Forward KL 就一定更好探索吗？** 不一定。正向 $D_{\mathrm{KL}}(\pi_{\mathrm{ref}}\|\pi_\theta)$ 会逼策略继续覆盖 reference 的所有峰，包括有害或无用模式，而且要从 $\pi_{\mathrm{ref}}$ 采样，和 on-policy 采样轨迹（rollout） 管道不一致。探索应用更松的反向或阶段性无 KL，而不是直接把方向写反。换方向等于换目标，要重做安全评测。
- **Reference reweighting 做什么？** 降低 reference 对「常见但无回报」token 的锚定，或提高稀有成功前缀的权重，让 KL 不再把长尾正确路径当离群点掐掉。要和更严的 verifier 一起上，否则升权的是 hacking 前缀。它改的是锚的形状，不是把反向 KL 改成正向。
- **Reward 不可靠时呢？** 先修 verifier，再谈扩张。宽松 KL 加噪声奖励，是最快的 hacking 配方。OOD 失效见 `pt-reward-ood-failure`。规则奖励也有盲区：格式对、语义错时，放宽探索只会更快找到 checker 漏洞。
