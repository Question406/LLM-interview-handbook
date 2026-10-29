---
id: ml101-multiple-testing
section: probability
order: 11
level: A
title: "同时比较很多模型为什么需要多重检验意识？"
quick: "同时检验很多候选时，即使每个都用 0.05 阈值，也会更容易挑出偶然显著的赢家。要先定义哪些比较属于同一组，再按目标选择控制至少一次误报的 FWER，或控制错误发现比例期望的 FDR。反复用同一验证集选模型还会产生选择乐观，需要独立评估。"
tags:
  - Machine Learning
  - probability
realInterview: false
status: published
format: markdown
updatedAt: 2026-10-22
sources:
  - title: "SciPy: False Discovery Rate Control"
    url: https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.false_discovery_control.html
    type: primary
---

比较很多模型时，最大的提升可能只是噪声里挑出来的极值。每个检验单独控制 5% 误报，并不等于“挑出的赢家只有 5% 概率是误报”，也不等于整组比较的误报率只有 5%。

举个容易算的例子：20 个真实零效应的检验彼此独立，每个按 0.05 水平拒绝，至少一次误报的概率是 $1-0.95^{20}\approx64.2\%$。模型间的比较往往相关，这个数不能照搬，但“比较次数改变整体错误控制”这个问题仍在。

若上线决策要求整组至少一次假阳性的概率不超过 $\alpha$，可以控制家族错误率 FWER。Bonferroni 把 m 次检验的每次阈值设成 $\alpha/m$；只要各个 p 值本身有效，利用概率的并集上界就能控制 FWER，不要求检验独立，但可能保守。

探索性筛选若允许少量错误发现，可以考虑 FDR：$E[V/\max(R,1)]$，其中 V 是错拒的零假设数，R 是总拒绝数。它控制的是发现集合里错误比例的期望，不是保证每次都只有那个比例。Benjamini–Hochberg 方法适用于独立或某些正依赖条件；更一般依赖下可以考虑更保守的 Benjamini–Yekutieli。方法和依赖要求见 [SciPy 的 FDR 文档](https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.false_discovery_control.html)。

我会事前固定主要比较和指标，把探索与最终确认分开。用同一验证集不断改超参、最后只报最好的结果，会让报告值乐观；多重检验校正也不能替代一个未参与选择的最终测试集。

## 追问

**只报告最好的模型，其他没写出来，也算多重比较吗？**
算。选择发生在报告之前，隐藏失败的尝试不会消除筛选带来的偏差，应该记录实际尝试的模型和指标。

**FDR 控制为 5%，是不是每个入选模型有 95% 概率真的更好？**
不是。FDR 是重复整个筛选流程时错误发现比例的期望，不是单个模型的 posterior probability。

**所有模型都在同一批样本上评测，怎么办？**
应保留配对结构来估计性能差异，并选适合依赖关系的多重校正。不能把每个模型的准确率当成来自独立测试集，也不能假定比较之间独立。
