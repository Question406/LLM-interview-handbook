---
id: dt-novel-bootstrap
section: labs
order: 2
level: S
title: OpenAI：无标语料里怎么挖「新」数据并 bootstrap？
quick: "从少量种子开始迭代：种子取自冻结评测的失败案例、研究集和许可领域难例，用小分类器给未标注数据打分，综合质量、新颖程度和不确定性挑出值得人看的样本，标完更新分类器再筛下一轮。分类器可用合成标签启动，按语言校准；每轮看冻结评测是否真的改善，边际收益停了就停。"
companies:
  - apple
tags:
  - OpenAI
  - Active Learning
  - Data Flywheel
  - Apple
realInterview: true
status: published
format: markdown
updatedAt: 2026-10-12
sources:
  - title: Novel Data Mining from Large Unlabeled Datasets (AceOffer, OpenAI reports)
    url: https://aceoffer.app/interviews/oai_novel_data_mining_from_large_unlabeled_datasets_system_desig
    type: secondary
  - title: "openai ML Tech Phone Screen: Data Flywheel, Discover and Bootstrap Novel Data (1Point3Acres)"
    url: https://www.1point3acres.com/interview/thread/1149074
    type: candidate-first-hand
  - title: FineWeb-Edu
    url: https://huggingface.co/spaces/HuggingFaceFW/blogpost-fineweb-edu
    type: primary
---

思路是一个从少量种子出发、反复迭代的挖掘循环：先找种子，训一个小分类器给未标注池打分，挑出最值得人看的候选，标完再更新分类器。种子来自冻结评测的失败案例、研究集和许可领域的难例，候选池来自网页抓取、许可数据和验证过的合成。

## 为什么要迭代

一个常见的不足是做一次无监督聚类就收工。新颖和离群是两回事，离群点里很多只是垃圾；只聚一次类，挑出来的多半是乱码和模板页。分类器在人工反馈下一轮轮更新，才能慢慢分清「没见过的好数据」和「没见过的垃圾」。

## 循环怎么搭

1. **找种子。** 来源是冻结评测的失败案例、内部研究集和许可领域的难例。未标注的候选池来自网页抓取、许可库和验证过的合成数据。
2. **训分类器。** 用少量种子训练。种子不够时，可以像 FineWeb-Edu 那样用合成标签起盘，并按语言校准，见 `dt-quality-clf-synth`。
3. **打分挑候选。** 综合质量、新颖程度和不确定性三个维度，人工优先检查分数高、又和已有种子不同的候选。人看的协议和金标见 `dt-annotator-protocol`。
4. **更新再筛。** 用标注结果更新分类器，继续下一轮。每轮都看冻结评测集上的 $\Delta$，防止飞轮自我表扬，见 `dt-data-flywheel`。
5. **停止。** 新增类别带来的边际 $\Delta$ 不再增加，或者污染率上升，就停。

分布外数据（OOD，即与训练数据明显不同的数据）还要单独处理：做漂移监控，并额外强制从新簇里抽样。否则旧分类器会把新出现的失败当成噪声过滤掉。

## 「新颖」具体指什么

「新颖」往往是评测还没覆盖到的类别，比如某个 locale 的指令、工具调用第二跳返回空结果。找到这类缺口和 `dt-see-around-corners` 是同一个动作，只是题面写成了挖掘系统。

## 题目来源

AceOffer 记录过这道 OpenAI 系统设计题，设定包括网页、图和病历，在极少标签下冷启动；一亩三分地也有一篇标题为「Data Flywheel + Discover and Bootstrap Novel Data」的 phone screen 面经。OpenAI 面经常把这题和 data flywheel 绑在一起问。

## 追问

- **病历、图那种设定怎么办？** 先问许可和 PII。没有许可我就拒题，不设计一条爬取病历的管线。
- **不确定度会不会挖出来的全是噪声？** 会。只看熵会挖到乱码，所以要用不确定度、和种子的距离、域配额三个维度一起打分。
- **和拒绝采样什么关系？** 拒绝采样是在已有题目上筛出对的轨迹；这题是在还没有题目的池子里找新题。
