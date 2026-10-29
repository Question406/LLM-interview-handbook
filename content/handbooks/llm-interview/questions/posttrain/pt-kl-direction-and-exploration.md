---
id: pt-kl-direction-and-exploration
section: posttrain
order: 41
level: S
title: 为什么常见 reverse-KL reference regularization 可能让 RLVR 困在 base-model support？什么时候考虑不同 KL 方向或 reference reweighting？
quick: "reverse KL 的期望在当前策略上取，策略不敢去 reference 几乎不说的地方，稳定，但稀有的正确新路径也会被压掉。高 K 曲线显示好轨迹确实存在但稀少、而且 reward 可靠时，可以试更宽的正则或 reference 重加权；reward 噪声大时放宽只会放大 hacking。"
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
常见的 reverse KL 护栏是 mode-seeking 的：策略只敢待在 $\pi_{\mathrm{ref}}$ 的高概率区域里，正确解如果落在 base 模型的长尾，就很难被采到，RLVR 也就学不到。这和「KL 系数太大学不动」是两回事，方向决定了惩罚落在哪类 token 上。要不要换方向或者做 reference 重加权，取决于两件事：高 K 下好轨迹确实存在，而且 reward 足够可靠。

最容易被追问的做法是把 $\beta$ 调小，看到训练 reward 上涨，就宣布探索成功。面试官会接着问 Pass@K 和熵，因为 reward 上涨可能只是更频繁地重复 reference 里已经会做的题型，support 一点没变宽。RLVR 靠的是偶尔采到长尾里的成功，mode-seeking 正则和这个需求是相冲的，只有奖励非常干净、已经不缺覆盖的时候，才适合把 reverse KL 当稳定器。

## reverse KL 为什么是 mode-seeking

RLHF 和 RLVR 里最常见的惩罚是

$$
D_{\mathrm{KL}}(\pi_\theta\|\pi_{\mathrm{ref}})=\mathbb{E}_{y\sim\pi_\theta}\big[\log\pi_\theta(y)-\log\pi_{\mathrm{ref}}(y)\big].
$$

期望在当前策略上取。$\pi_\theta$ 一旦把概率放到 $\pi_{\mathrm{ref}}\approx 0$ 的地方，$\log$ 比就会变得很大，所以策略不敢发明 reference 几乎不会说的续写。反过来，$\pi_{\mathrm{ref}}$ 有、$\pi_\theta$ 不去的峰根本不进期望，策略可以把它们丢掉。这就是 mode-seeking，锁住参考分布里已经比较亮的模式。白板推导见 `fund-kl-directions`，对齐为什么特意选这个方向见 `pt-rlhf-why-reverse-kl`。

对聊天对齐来说这是优点，没人想去覆盖 SFT 里残留的有害峰。对 RLVR 探索就可能是缺点：难题的正确轨迹可能就在参考分布的低概率区域，reverse KL 会把 sampling 压回常见但解不出的套路。只优化 Pass@1 又会进一步强化已有模式，所以要看大 K 的曲线，判断稀有的正确路径还能不能被采到。聊天对齐通常希望收窄模式，推理 RL 有时需要扩大探索，前提是奖励可靠。

## 怎么判断困在了 base support 里

RLVR 的机制是偶尔采到一次可验证的成功，然后提高这条轨迹的概率。如果成功轨迹相对 $\pi_{\mathrm{ref}}$ 的概率极低，会同时看到两个现象。一是 Pass@1 几乎不动，Pass@K 要到很大的 $K$ 才翘起来，说明覆盖在长尾，模型并不是不会算。二是加大 $\beta$ 或一直挂着强 reverse KL 以后，熵下降、模式变少、长度和套话增加，K 曲线也被压扁了。这时候的「稳定」来自 support 收缩，策略并没有学到新东西。

KL 变小、reward 变高，也别自动读成探索成功，分布可能只是在 reference 的几个峰上刷分。有一个很有用的对照实验：冻结 KL 系数，只把 sampling 温度或 $n$ 调大，看高 K coverage 会不会出现。更大的 sampling 也挖不出正确轨迹，瓶颈就在 seed 或题目上，改 KL 方向没用；sampling 能挖出来、训练时却采不到，才说明是正则太紧了。

## 放宽之前先测什么

决定换方向、降 $\beta$、做 reference reweighting 或者单独开一个 exploration 阶段之前，我会先回答三个问题。reward 的 false positive 有多高，规则 checker 有没有盲区，reward model（RM）有没有风格偏置？噪声大的话，扩大 support 就等于给 hacking 更大的搜索空间，见 `pt-reward-ood-failure`。高 K coverage 是不是真的存在？$K$ 已经很大还几乎没有正确候选，瓶颈是 seed、题目难度或验证器（verifier），跟 KL 方向无关。out-of-distribution 数据（OOD，即与训练数据明显不同的数据）和安全有没有在回归？放宽正则就得配更密的 held-out 和 safety eval，训练 reward 说明不了这些。

能试的手段有：更小或自适应的 $\beta$（`pt-adaptive-kl-controller`）、正向或对称散度、给稀有的高回报轨迹升权、先不加 KL 探索再收紧。每一种都要同时把 verifier 收严，光改公式不够。探索阶段最好设一个短预算和硬停止条件，gold 指标或安全评测一掉就收紧。和无 KL 的 DAPO 类配方衔接时，要承认这是在用数据和奖励质量换正则，并没有发现 reverse KL 的数学错误。

也别想着把 PPO 的 KL 改成 cross entropy 来「换方向」，那样会连 sampling 分布一起反掉，见 `ant-kl-vs-ce`。现场要手写惩罚项，就先写期望在 $\pi_\theta$ 上，再写 $\log\pi_\theta-\log\pi_{\mathrm{ref}}$，最后乘 $\beta$。左右写反是这题最常见的白板事故，比记不住公式更致命。

## 监控上怎么区分探索和漂移

我会把五样东西画在同一张训练曲线上。先看 $K$ 曲线，Pass@1 不动而大 $K$ 在涨，说明覆盖在长尾，KL 可能正在掐这条尾巴。再看熵、唯一轨迹数和 n-gram 多样性，这几个在掉、训练 reward 却在涨，多半是 mode-seeking 在刷已知套路。长度变长可能是搜索更深，也可能是在 reference 风格里注水，见 `pt-reasoning-token-cost-frontier`。KL 数值很小，说明贴着 $\pi_{\mathrm{ref}}$；很大而且 gold 指标在掉，就是漂移。最后是 reward 和真实成功率的偏离，proxy 还在涨、可执行准确率不动，就是 hacking，再放宽 KL 只会更快。

这样画比单独汇报一个 $\beta$ 有说服力。探索阶段允许熵上升，但 gold 和安全切片必须同时在图上，不然分不清是在搜还是在漂，探索阶段也可能把有害峰一起点亮。熵上升而 gold 不动，我会先当 hacking 处理，别当成突破。

## 追问

**只看 Pass@1 为什么不够？**
Pass@1 被 mode-seeking 优化得很漂亮的时候，K 曲线、熵、唯一轨迹数可能已经塌了。要把覆盖率和选择能力分开看，方法和 `pt-best-of-n-decomposition` 一样。Pass@1 涨、Pass@K 跌，常常是 support 在收缩，模型没变强。

**换成 Forward KL 就一定更好探索吗？**
不一定。正向 $D_{\mathrm{KL}}(\pi_{\mathrm{ref}}\|\pi_\theta)$ 会逼策略继续覆盖 reference 的所有峰，包括有害或者没用的模式，而且要从 $\pi_{\mathrm{ref}}$ sampling，和 on-policy 的 sampling 轨迹（rollout）管道对不上。想探索，用更松的 reverse KL 或者阶段性去掉 KL 更合适。换方向等于换目标，安全评测要重做。

**Reference reweighting 具体做什么？**
KL 项里 $\log\pi_{\mathrm{ref}}$ 对常见但没回报的 token 权重太重时，把这些位置的参考概率调低，或者把最终可验证成功的前缀调高，让护栏少误伤长尾里的正确路径。它改的是锚的形状，reverse KL 还是 reverse KL。重加权要用独立于训练 reward 的信号，比如 held-out 成功标签，否则升权的就是 hacking 前缀，所以也要和更严的 verifier 一起上。做完还要看 K 曲线，只有 Pass@1 涨、大 $K$ 不动，说明还在刷已知峰，support 没撑开。

**Reward 不可靠的时候呢？**
先修 verifier，再谈扩张。宽松的 KL 加上有噪声的奖励，是最快的 hacking 配方，OOD 失效见 `pt-reward-ood-failure`。规则奖励也有盲区，格式对、语义错的时候，放宽探索只会更快找到 checker 的漏洞。
