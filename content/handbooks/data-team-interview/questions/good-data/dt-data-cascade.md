---
id: dt-data-cascade
section: good-data
order: 4
level: A
title: Data Cascade：数据上的错，为什么会在很后面才爆？
quick: >-
  因为训练 loss 看不出来：上游数据错了，模型只是更好地拟合了错误数据，loss 照样往下走。抽取错误、阈值不合适、teacher
  版本变化、evaluation contamination 会沿处理流程一步步放大，最后才在下游任务里暴露，这就是 Data
  Cascade。每一步都留下处理原因和版本，出事时才能回溯。
companies:
  - apple
tags:
  - Apple
  - Data Quality
  - Lineage
realInterview: false
status: published
format: markdown
updatedAt: 2026-10-12T00:00:00.000Z
sources:
  - title: 'Everyone wants to do the model work, not the data work (CHI 2021)'
    url: 'https://dl.acm.org/doi/10.1145/3411764.3445518'
    type: primary
  - title: Data Cascades in Machine Learning (Google Research blog)
    url: 'https://research.google/blog/data-cascades-in-machine-learning/'
    type: secondary
  - title: Datasheets for Datasets
    url: 'https://arxiv.org/abs/1803.09010'
    type: primary
---

因为训练 loss 看不出来。上游数据错了，模型只是在更好地拟合错误的数据，loss 照样往下走。错误沿着处理流程一步步放大，往往要等到下游某个语言的指标掉了 4 个点才被发现。这种连锁问题叫 Data Cascade，对付它的办法是让每一步处理都留下查得到的原因和版本。

举个例子。抽取程序把网页导航当成了正文，质量分类器觉得它很像网页，给了高分；训练 mix 又按质量加权，于是模型反复在学 cookie 提示文案。pre-training loss 一点异常都没有，直到下游某个 evaluation slices 出了问题才暴露。

别的环节也是同一个套路。按英语设的过滤阈值，可能让 low-resource 语言的通过率掉一个数量级，multilingual 配额表面上填满了，留下的多是英语镜像和机器翻译页面，AFM 报告强调按语言选择标签也是这个原因。合成脚本没变、teacher model 升级了，数据的风格和 leakage 情况会跟着变，训练卡上却还叫 `synth_v3`，就分不清变化来自哪一版 teacher，见 `dt-repro-lineage`。评测题混进训练后，旧检查集分数上涨，按时间划分的新题却可能下降，只看旧题会以为这类数据有效，接着扩大 contamination。收集协议和 annotator 激励对不上时，可能到上线才发现原以为可靠的标签互相矛盾，对应的检查见 `dt-annotator-protocol`、`dt-kappa-code`。

CHI 2021 有一项研究访谈了 53 位高风险场景的从业者，讲的就是数据工作被低估之后的连锁问题。他们总结 Data Cascade 普遍存在、早期不明显、影响延迟出现，而且很多本来可以避免。如果只拿 loss 当数据健康指标，出了问题再加量，可能会继续放大原来的错。

## 怎样早点发现、止住扩散

我会让每一步输出都带一个 `reason`，写清它是被硬性规则拦掉了、拿了什么模型分数，还是进了隔离区（quarantine）。dataset card 记下过滤器 git 版本、teacher 版本和规范化（canon）规则，这是 Datasheets 落到工程里最基本的可追踪信息。

有了这些记录，下游出问题时才有路可以往回走。安全检查集被训练 data contamination 的处理见 `dt-contam-hold`。Culture 轮问「你停过哪一批数据」，看的也是你能不能主动截断这种连锁影响，见 `dt-killed-dataset`。

## 追问

**这和技术债有什么区别？**
两者很像，区别在数据错误容易表现成模型能力问题。原因误判了、一直去调架构，可能越调越偏。

**小团队没有平台，怎么做？**
先不用搭大平台。每周维护一份按 evaluation slices 的指标表，再抽查隔离区，就能比只看 loss 更早发现问题。

**能引用论文里的 92% 吗？**
可以，同时说明这是研究样本里的比例，用来说明论文观察到这种问题很普遍。它代表不了某家公司，也不是行业普查。

**下游指标掉了，第一步做什么？**
先暂停发布，再沿着每一步的 `reason` 和版本记录往回查，找到是哪一步开始出错的。
