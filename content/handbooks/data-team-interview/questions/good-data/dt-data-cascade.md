---
id: dt-data-cascade
section: good-data
order: 4
level: A
title: Data Cascade：数据上的错，为什么会在很后面才爆？
quick: "Data Cascade 指上游数据错误没有及时被发现，沿处理流程逐步放大，最后在下游任务中暴露。抽取错误、过滤阈值不合适、教师版本变化或评测污染，都可能在训练 loss 仍下降时发生。每一步都要留下处理原因和版本，才能回溯问题。"
companies:
  - apple
tags:
  - Apple
  - Data Quality
  - Lineage
realInterview: false
status: published
format: markdown
updatedAt: 2026-10-12
sources:
  - title: "Everyone wants to do the model work, not the data work (CHI 2021)"
    url: https://dl.acm.org/doi/10.1145/3411764.3445518
    type: primary
  - title: Data Cascades in Machine Learning (Google Research blog)
    url: https://research.google/blog/data-cascades-in-machine-learning/
    type: secondary
  - title: Datasheets for Datasets
    url: https://arxiv.org/abs/1803.09010
    type: primary
---

上游数据出错，训练 loss 仍可能继续下降，因为模型正在更好地拟合错误的数据。问题往往要到下游某个地区语言（locale）的指标掉了 4 个点，才被发现。这就是为什么每一步数据处理都要留下可查的原因和版本。

CHI 2021 的研究访谈了 53 位高风险场景从业者，讨论数据工作被低估后出现的连锁问题。Data Cascade 的特点是：普遍存在、早期不明显、影响延迟出现，而且很多本来可以避免。只把 loss 当作数据健康指标，发现问题后再加量，可能继续放大原来的错误。

## 错误如何传到下游

抽取程序可能把网页导航当成正文。质量分类器觉得它很像网页，给了高分；训练 mix 又按质量加权，于是模型反复学习 cookie 提示文案。预训练 loss 看不出异常，产品文案切片却会出问题。

按英语设置的过滤阈值，可能让低资源语言的通过率下降一个数量级。多语配额表面上填满了，实际保留的却多是英语镜像和机器翻译页面。因此，AFM 强调按语言选择标签。

合成脚本没变，教师模型却升级了，数据的风格和泄漏情况也可能随之改变。如果训练卡仍只叫 `synth_v3`，就无法判断变化来自哪一版教师，见 `dt-repro-lineage`。

评测题混入训练后，旧检查集的分数会上升，按时间划分的新题却可能下降。如果只看旧题，会误以为加这类数据有效，继续扩大污染。

收集协议与标注员的激励也可能不一致。直到模型上线才发现，原以为可靠的标签之间互相矛盾。对应的检查见 `dt-annotator-protocol`、`dt-kappa-code`。

## 怎样早点发现、停止扩散

每一步输出都带 `reason`，写清是被硬性规则拦截、获得了什么模型分数，还是进入了隔离区（quarantine）。dataset card 记录过滤器 git 版本、教师版本和规范化（canon）规则。这些是 Datasheets 在工程中最基本的可追踪信息。

如果到了下游才发现错误，先暂停发布，再沿版本记录回溯。安全检查集被训练数据污染时，见 `dt-contam-hold`。Culture 轮问「你停过哪一批数据」，也在看你能否主动截断这种连锁影响，见 `dt-killed-dataset`。

## 追问

- 和技术债有什么区别？两者相近，但数据错误容易表现成模型能力问题。如果误判原因，一直调架构，可能越调越偏。
- 小团队怎么做？不用先搭大平台。每周维护一份按切片的指标表，并抽查隔离区，就能比只看 loss 更早发现问题。
- 能引用论文中的 92% 吗？要说明这是研究样本中的比例，不是苹果的数据，也不是行业普查。可以据此说明论文观察到这种问题很普遍。
