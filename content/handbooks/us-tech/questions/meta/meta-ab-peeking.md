---
id: meta-ab-peeking
section: meta
order: 7
level: A
title: Meta：A/B 提前偷看为什么会通胀显著度，序贯检验怎么讲
quick: "普通固定样本检验若反复查看、普通阈值为 $0.05$，见 $p<0.05$ 就停，会让整体假阳性超过 $5\\%$，效应估计也可能偏大。可预先定样本量并按期决策，或使用 always-valid p-value、置信序列、mSPRT，提前写好主指标与护栏的停止规则。"
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

A/B 实验中反复看普通 $p$ 值、显著就停，会增加假阳性。原来的 $5\%$ 保证针对预先规定的检验方案；把每天的查看都变成一次胜出机会，就改变了整个实验的拒绝规则。

例如真效应为 $0$，每天看一次、连续 $14$ 天，见 $p<0.05$ 就停，假阳性可能达到百分之十几甚至更高，具体取决于相关性和停止规则。在 $H_0$ 下累计均值不断波动，反复查看就更容易某次穿过 $1.96$，还会恰好停在噪声上跳时，让效应量偏大。

经典 $z$ / $t$ 检验的 Type I error $\alpha=0.05$ 按固定样本量 $n$、结束时一次判断来控制。样本大也不能消除可选停止；CUPED 和分层降低方差，不修复停止规则。普通后验 $P(\delta>0\mid\mathrm{data})$ 每天看也不能自动获得同样的频率学保证，要有专门的序贯决策设计。这道统计题按 Johari 等人的 Peeking at A/B Tests、always-valid inference 整理，Meta PlanOut 是公开的实验工程背景，并非某场 onsite 原题。

## 可以采用哪些规则

最直接是固定视界：按 MDE、$\alpha$ 和功效预先算 $n$，到期再判断主指标。中途可以监控崩溃、完整度等护栏，但使用护栏做停止决策也要预先写规则，不能借“护栏没事”提前宣布主指标获胜。

需要随时决策时，可以使用 always-valid p-value 或置信序列，使任意时刻的 $p(t)$ 满足 $\Pr(\exists t: p(t)\le\alpha)\le\alpha$，即整个查看过程中误报仍受控。代价是同样 $n$ 下通常更保守，需要更多样本或更大效应。mSPRT 对效应大小做先验混合，用似然比越界来停止，边界由 $\alpha$ 与先验决定，不能简单把 $1.96$ 换成 $3$。

若大致知道查看的次数和时间，也可用 $\alpha$-spending，如 O'Brien-Fleming，为第 $1,2,\ldots,K$ 次查看分配错误率。随时刷新的 dashboard 则更适合 always-valid。固定把阈值降到 $0.001$ 能减少通胀，却没有给任意查看次数的 Type I 控制。

Feed 权重 $w_k$ 或广告校准层更新也遵循同样协议，不能 CTR 两小时上升就全量，见 `meta-newsfeed-rank`、`meta-ads-calibration`。完整度投诉、延迟、花费这些护栏同样要规定决策方式。Always-valid 第 $3$ 天不显著，不代表第 $14$ 天不会显著，只表示当前证据不足。功效不够应预先加 $n$ 或用 CUPED 降方差，偷看增加的是 false positive，不是在正确提高功效。

## 追问

**先看方向再加样本可以吗？**
这是可选停止。可以预先写最多 $n_{\max}$、允许在此之前用 always-valid 停，不能事后改普通检验的规则。

**多个指标怎么办？**
预先指定主决策指标和护栏。十个指标挑一个显著还有另一层多重比较，需要 Bonferroni / FDR 等处理。

**PlanOut 会解决偷看吗？**
不会，它处理分配和叠实验，统计有效性另行设计。

**CUPED 能替代序贯吗？**
不能，它缩短达到功效所需时间，查看与停止规则仍要单独约定。

**论文各说明什么？**
KDD 2017 的 Peeking at A/B Tests 讨论工业界持续看 dashboard 与序贯修正，always-valid 工作给同一路线的理论。
