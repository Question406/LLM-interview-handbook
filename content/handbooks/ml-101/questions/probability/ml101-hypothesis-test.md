---
id: ml101-hypothesis-test
section: probability
order: 9
level: A
title: p 值、显著性和统计功效怎么解释？
quick: >-
  p 值是在零假设和检验模型成立时，出现至少同样极端统计量的概率，不是零假设为真的概率。显著性水平 α
  控制零假设成立时误拒绝的概率，功效则是某个指定真实效应下正确拒绝的概率。解释结果还要一起看效应大小、区间和 sampling 设计。
tags:
  - Machine Learning
  - probability
realInterview: false
status: published
format: markdown
updatedAt: 2026-10-22T00:00:00.000Z
sources:
  - title: 'SciPy: Independent Two-Sample t-Test'
    url: >-
      https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.ttest_ind.html
    type: primary
  - title: 'UC Berkeley STAT 210A: Hypothesis Testing'
    url: 'https://stat210a.berkeley.edu/fall-2024/reader/hypothesis-testing.html'
    type: primary
---

p 值衡量数据与零假设的相容程度，显著性水平是事前约定的误报控制，功效描述检验发现指定效应的能力。要让这些概率有意义，必须先写清零假设、统计量和数据怎样采集。

例如比较两组独立观测的均值，零假设是 $H_0:\mu_A=\mu_B$。双侧检验的 p 值是在零假设成立时，统计量的绝对偏离至少达到观测值的概率；具体“极端”方向由备择假设和统计量定义。[SciPy 的独立样本 t 检验文档](https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.ttest_ind.html)给出了这个解释，且 Welch 版本不要求两总体方差相等。

显著性水平 $\alpha$ 是整套检验在 $H_0$ 下拒绝的概率上限；常说的功效为 $1-\beta$，其中 $\beta$ 是某个指定备择效应下未拒绝的概率。功效取决于效应、方差、样本量、单双侧和检验设计，不能脱离效应只报一个数，见 [Berkeley 的显著性与功效讲义](https://stat210a.berkeley.edu/fall-2024/reader/hypothesis-testing.html)。

比如两组均值差为 0.1、标准误为 0.04，正态近似统计量是 2.5，双侧 p 值约为 0.012。它说明这个偏离在零假设下较少见；不能说“原假设有 1.2% 的概率正确”，也不能直接断言 0.1 的变化对产品有用。若同一用户贡献多条相关观测，却按独立样本算标准误，p 值可能过小。

## 追问

**p 大于 0.05 就证明没有效果吗？**
不能。可能确实没有，也可能样本不够。要看区间是否已经排除了有实际意义的效应；证明近似等效需要预设等效界限和对应检验。

**样本越多，越容易显著，是不是作弊？**
固定真实效应下，标准误通常随有效样本增加而下降，所以功效会上升。这也说明显著不等于重要，要同时报效应量。

**随机分组和独立观测是一回事吗？**
不是。随机分组帮助识别处理效应，但同一用户、团队或时间段内的结果仍可能相关；分析要匹配随机化和依赖单位。
