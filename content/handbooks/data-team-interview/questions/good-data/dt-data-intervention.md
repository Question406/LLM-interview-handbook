---
id: dt-data-intervention
section: good-data
order: 15
level: S
title: 怎样才算把数据做对：一次干预从假设跑到能不能上 mix？
quick: "先写一个能被推翻的假设，固定评测，再只改一项数据因素，例如来源、过滤或配比。用同模型、同预算的对照实验检查目标能力和其他能力，再核对污染、隐私、许可与版本记录。通过后才加入训练 mix，否则隔离并记录失败原因。"
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

一次数据干预，要从「我怀疑问题出在这里」走到「实验支不支持这个判断、这批数据能不能进训练」。做法是：先写出能被推翻的假设，固定评测，一次只改一项数据因素，用同模型、同预算的对照检验，查完副作用、记好版本，再决定合并还是隔离。

之所以一次只改一项，是因为归因。同时换来源、过滤器和配额，出了问题很难说清是哪一项造成的；训练过程中不断改过滤规则，再把 loss 下降归功于数据变好，也无法复现。DataComp-LM 的做法是固定模型、只改变数据；Datasheets 则帮助记录复盘需要的字段。

## 一次干预的步骤

1. 写出可能被实验推翻的假设。例如：「工具第二次调用失败，是因为 SFT 中没有合法处理失败的分支。」这比「我们缺数据」具体得多。怎样从评测里诊断出这类假设，见 `dt-benchmark-gap`。
2. 固定评测。开发集可以跟着迭代，发布前必须通过的检查集在实验期间保持不变。新标注的参考答案另起一页追加。
3. 一次只改一项：增加来源、调整阈值、改变配额，或加入经过验证的合成数据，效用怎么定义见 `dt-utility-select`。动手之前先确认来源合法、允许用于训练。
4. 做对照。固定模型和预算，同时报告目标切片和用来检查其他能力的锚点指标，见 `dt-hold-model-vary-data`。
5. 检查副作用：评测污染、个人信息（PII）、许可，以及各语言的通过率。如果发现错误已经开始沿处理流程扩散，先停下来回溯，见 `dt-data-cascade`。
6. 记录后再合并。写清来源、过滤器 git 版本、教师版本和指标变化 $\Delta$。检查没通过的数据进入隔离区（quarantine），不加入训练 mix。

实验失败也有信息量：它告诉你原来哪句假设不成立、下一步该查什么。HM 问失败的数据尝试时，可以按这个过程讲，见 `dt-failed-data-bet`。整个持续迭代的流程见 `dt-data-flywheel`，这题讲的是其中一次迭代具体怎么做。

## 两种会丢掉归因的做法

一种是让当前模型给自己的新数据打标，再用已经被污染的检查集上的分数上涨来证明效果。这会形成自污染，见 `dt-self-improve`。

另一种是一次上线「新爬取 + 新分类器 + 新配额」。之后 Director 问成本收益，你没法单独删掉其中一项重跑对照，也就回答不了到底哪项值得投入，见 `dt-cost-per-gain`。

## 追问

- 一轮需要多久？有验证器（verifier）的工具和数学任务可以按周迭代；主观人评按抽检批次安排。目标是赶在产品投诉之前发现问题，避开 cascade 里常见的延迟。
- 假设从哪来？从固定评测中的失败模式、WIMBD 式的计数和人工标注争议中找。「业界都在做合成」提供不了具体假设。
- 许可和隐私在哪一步检查？在第 3 步之前，先确认来源能否合法使用。来源换成许可研究集或合成复现之后，后面的实验和检查步骤照样要做完。
