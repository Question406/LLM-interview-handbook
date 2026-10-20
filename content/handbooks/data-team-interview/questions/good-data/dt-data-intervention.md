---
id: dt-data-intervention
section: good-data
order: 15
level: S
title: 怎样才算把数据做对：一次干预从假设跑到能不能上 mix？
quick: "先写一个可验证的假设，固定评测，再只改一项数据因素，例如来源、过滤或配比。用同模型、同预算的对照实验检查目标能力和其他能力，再核对污染、隐私、许可与版本记录。通过后才加入训练 mix，否则隔离并记录失败原因。"
companies:
  - apple
tags:
  - Apple
  - Data Flywheel
  - Data Quality
  - Evaluation
realInterview: false
status: published
format: markdown
updatedAt: 2026-10-12
sources:
  - title: DataComp-LM
    url: https://arxiv.org/abs/2406.11794
    type: primary
  - title: Datasheets for Datasets
    url: https://arxiv.org/abs/1803.09010
    type: primary
  - title: Apple Intelligence Foundation Language Models Tech Report 2025
    url: https://machinelearning.apple.com/research/apple-foundation-models-tech-report-2025
    type: primary
  - title: "Everyone wants to do the model work, not the data work (CHI 2021)"
    url: https://dl.acm.org/doi/10.1145/3411764.3445518
    type: primary
---

一次数据干预，要从「我怀疑问题出在这里」走到「实验是否支持这个判断、数据能否进入训练」。`dt-data-flywheel` 讲持续迭代的整体流程，这题讲每次迭代具体怎么做。

同时换来源、过滤器和配额，出了问题很难归因。训练过程中不断改过滤规则，再把 loss 下降归功于数据变好，也无法复现。DataComp-LM 的做法是固定模型，只改变数据；Datasheets 则帮助记录复盘需要的字段。

## 一次干预的步骤

1. 写出可能被实验推翻的假设。例如：「工具第二次调用失败，是因为 SFT 中没有合法处理失败的分支。」这比「我们缺数据」更具体。诊断方法见 `dt-benchmark-gap`。
2. 固定评测。开发集可以迭代，发布前必须通过的检查集不能跟着实验变。新标注的参考答案另页追加。
3. 一次只改一项：增加来源、调整阈值、改变配额，或加入经过验证的合成数据。效用函数见 `dt-utility-select`。开始前先确认来源合法；在苹果场景中，不能默认拿用户日志来训练。
4. 做对照。固定模型和预算，同时报告目标切片及用于检查其他能力的锚点指标，见 `dt-hold-model-vary-data`。
5. 检查副作用。核对评测污染、个人信息（PII）、许可，以及各语言通过率。发现错误开始沿处理流程扩散，就先停下回溯，见 `dt-data-cascade`。
6. 记录后再合并。写清来源、过滤器 git 版本、教师版本和指标变化 $\Delta$。检查不通过的数据进入隔离区（quarantine），不要加入训练 mix。

实验失败也有信息：原来的哪句假设不成立，下一步应该查什么。HM 问失败的数据尝试时，可以按这个过程讲，见 `dt-failed-data-bet`。

## 两种容易失去归因的做法

让当前模型给自己的新数据打标，再用受污染检查集的分数上涨来证明效果，会形成自污染，见 `dt-self-improve`。

一次上线「新爬取 + 新分类器 + 新配额」，也无法回答到底哪项值得投入。Director 问成本收益时，你无法单独删掉一项重跑对照，见 `dt-cost-per-gain`。

如果来源改成许可研究集或合成复现，后面的实验和检查步骤仍然适用。

## 追问

- 一轮需要多久？有验证器（verifier）的工具、数学任务可以按周迭代；主观人评则按抽检批次安排。目标是早于产品投诉发现问题，避免 cascade 中常见的延迟。
- 假设从哪来？从固定评测中的失败模式、WIMBD 式计数和人工标注争议中找。仅因为「业界都在合成」，还不足以提出具体假设。
- 苹果的数据限制在哪一步检查？在第 3 步之前，先确认能否合法使用来源。换成许可数据或合成数据后，仍要完成其他步骤。
