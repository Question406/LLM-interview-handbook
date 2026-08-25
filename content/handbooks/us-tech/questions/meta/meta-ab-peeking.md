---
id: meta-ab-peeking
section: meta
order: 7
level: A
title: Meta：A/B 提前偷看为什么会通胀显著度，序贯检验怎么讲
quick: >-
  固定样本检验的 $p$ 值只在「预先定好 $n$、只看一次」时控制第一类错误。中途反复偷看、看到 $p<0.05$ 就停，假阳性会远高于
  $5\%$。正确做法是预先定 $n$、或用 always-valid p-value / mSPRT 这类任意时刻都有效的序贯方法。
tags:
  - Meta
  - Experimentation
  - A/B Testing
  - Sequential Testing
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-23
sources:
  - title: Always Valid Inference — Continuous Monitoring of A/B Tests
    url: https://arxiv.org/abs/1512.04922
    type: primary
  - title: Peeking at A/B Tests — Why It Matters, and What to Do About It (KDD 2017)
    url: https://dl.acm.org/doi/10.1145/3097983.3097992
    type: primary
  - title: Designing and Deploying Online Field Experiments (PlanOut)
    url: https://research.facebook.com/publications/designing-and-deploying-online-field-experiments/
    type: primary
---

Ads / Feed / Growth 的 MLE 和数据科学岗几乎都会问实验。Meta 公开过 PlanOut 这类大规模实验框架；偷看问题本身是统计事实，不必编造某次 onsite 的题号。现场用 Johari 等人的 peeking 论文和 always-valid inference 就能把机制讲清楚。

## 为什么偷看会通胀显著度

经典 $z$ 检验 / $t$ 检验的 Type I error $\alpha=0.05$ 有一个前提：**样本量 $n$ 事先定死，只在结束时看一次 $p$ 值。** Dashboard 每天刷新，等于你在做多次检验。任意一天 $p<0.05$ 就宣称「赢了」并停实验，拒绝域被扫过很多次，假阳性会明显高于 $5\%$。

直觉：即使 $H_0$ 为真（处理效应是 $0$），累计均值的轨迹像随机游走。你盯着它看的次数越多，越容易在某次波动里穿过 $1.96$ 这条线。提前停还会让估计的效应量偏大：你刚好在噪声往上跳的时候停。

这和「样本不够」不是一件事。样本很大仍然会 peeking：你只是把游走看得更细。也和 CUPED / 分层这些降方差技巧无关——那些减的是方差，不修复多次查看的 Type I。更不是「再跑一天就更准」：在 $H_0$ 下你多看一天，只是又一次穿过阈值的机会。

错误答法：「我们内部用贝叶斯，所以可以天天看。」普通后验 $P(\delta>0\mid\mathrm{data})$ 天天看，同样有选择性停止问题，除非你用的是为序贯设计的决策规则。

## 序贯检验怎么说

三条都能上台面，选一条讲深：

1. **固定视界：** 预先用 MDE（最小可检测效应）、$\alpha$、功效算出 $n$，到期再看。中途可以看护栏（崩溃、完整度），但**主指标不拿来早停**，除非预先写进协议。这是最干净、也最难忍的。
2. **Always-valid p-value / 置信序列：** Johari 等人把序贯分析接到 A/B。任意时刻的 $p(t)$ 都满足 $\Pr(\exists t: p(t)\le\alpha)\le\alpha$。可以天天看、随时停，代价是同样 $n$ 下更保守，实验要跑更久或效应要更大才显著。
3. **mSPRT（mixture SPRT）：** 对效应大小放一个先验混合，似然比越过边界就停。实现上常和 always-valid 是同一族。要能说出：边界由 $\alpha$ 和先验决定，不是把 $1.96$ 改成 $3$ 这么简单。

$\alpha$-spending（O'Brien–Fleming 等）也可以提：预先规定第 $1,2,\ldots,K$ 次查看各花掉多少 $\alpha$。它要求查看次数/时间点大致预先知道；随时刷新的 dashboard 更贴 always-valid。现场若被问「那我们把阈值改成 $0.001$ 行不行」：任意偷看次数下，固定更小的 $\alpha$ 只是把通胀压低，没有给出任意时刻都有效的 Type I 控制，还是不如 always-valid 干净。

和 Feed 权重（`meta-newsfeed-rank`）、广告校准（`meta-ads-calibration`）连起来：线上改 $w_k$ 或校准层，必须当实验，不能看两小时 CTR 涨了就全量。护栏指标（完整度投诉、延迟、花费）同样不能偷看乱停，否则你只是换了一个被通胀的 $p$ 值。

## 一个具体数字直觉

假设真效应为 $0$，每天看一次、连续看 $14$ 天，用普通 $0.05$ 阈值早停，假阳性可以到百分之十几甚至更高（具体倍数依赖相关性和停时规则）。面试不必背表，但要说：**偷看次数越多，通胀越狠；正确的序贯方法把这个倍数压回 $\alpha$。** 反向：always-valid 在第 $3$ 天还不显著，不代表第 $14$ 天也不会显著，只代表你现在还没赚够证据。


现场还可以补一句：偷看通胀的是 **false positive 率**，不是功效。功效不够时，正确做法是预先加大 $n$ 或用 CUPED 降方差，而不是把 dashboard 当序贯检验来用。

这和「每天看一下护栏有没有炸」不冲突：护栏可以看，但不能用主指标的 $p$ 值做可选停止。

## 追问

- **可以先看方向再加样本吗？** 这就是可选停止。除非用序贯方法，否则 $p$ 值失效。正确做法是预先写「最多 $n_{\max}$、可在 $n_{\max}$ 前用 always-valid 停」。
- **多个指标怎么办？** 主指标一条，护栏预先定义。十个指标里挑一个显著，是另一重多重比较，要用 Bonferroni / FDR，或预先指定单一决策指标。
- **和 Peeking 论文的关系？** KDD 2017 的 Peeking at A/B Tests 把「工业界天天看 dashboard」这件事写清楚，并给出序贯修正。always-valid 论文是同一条线的理论。
- **PlanOut 解决偷看吗？** 不。PlanOut 解决的是实验分配和叠实验的工程。统计有效性要另做。
- **CUPED 能代替序贯吗？** 不能。CUPED 降方差、缩短达到功效的时间，偷看规则仍然要单独设计。
- **可以看护栏但不看主指标吗？** 可以，前提是护栏的决策规则也预先写好。用护栏「看起来没事」当主指标早停的借口，仍然是偷看。
