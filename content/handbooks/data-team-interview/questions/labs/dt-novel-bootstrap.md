---
id: dt-novel-bootstrap
section: labs
order: 2
level: S
title: OpenAI：无标 corpus 里怎么挖「新」数据并 bootstrap？
quick: >-
  从少量 seed 开始迭代：seed 来自冻结评测的失败案例、研究集和许可领域 hard
  examples，用小分类器给未标注数据打分，综合质量、新颖度和不确定性挑出值得人看的样本，标完更新分类器再筛下一轮。分类器可以用合成标签起步、按语言做
  calibration；每轮看冻结评测有没有真的改善，边际收益停了就停。
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
updatedAt: 2026-10-12T00:00:00.000Z
sources:
  - title: 'Novel Data Mining from Large Unlabeled Datasets (AceOffer, OpenAI reports)'
    url: >-
      https://aceoffer.app/interviews/oai_novel_data_mining_from_large_unlabeled_datasets_system_desig
    type: secondary
  - title: >-
      openai ML Tech Phone Screen: Data Flywheel, Discover and Bootstrap Novel
      Data (1Point3Acres)
    url: 'https://www.1point3acres.com/interview/thread/1149074'
    type: candidate-first-hand
  - title: FineWeb-Edu
    url: 'https://huggingface.co/spaces/HuggingFaceFW/blogpost-fineweb-edu'
    type: primary
---

思路是一个从少量 seed 出发、反复迭代的挖掘循环：找 seed，训个小分类器给未标注池打分，挑出最值得人看的候选，标完再更新分类器。seed 来自冻结评测的失败案例、研究集和许可领域的 hard examples，候选池来自网页抓取、许可数据和验证过的合成。

这里的「新」，往往是评测还没覆盖到的类别，比如某个 locale 的指令，或者 tool calls 第二跳返回了空结果。找到这类缺口和 `dt-see-around-corners` 是同一个动作，只是题面写成了挖掘系统。

要迭代，是因为新颖和离群是两回事。做一次无监督聚类就收工是常见的不足：离群点里很多只是垃圾，只聚一次类，挑出来的多半是乱码和模板页。分类器在人工反馈下一轮轮更新，才能慢慢分清「没见过的好数据」和「没见过的垃圾」。

循环具体这样搭。先用少量 seed 训分类器，seed 不够时可以像 FineWeb-Edu 那样用合成标签起盘，按语言做 calibration，见 `dt-quality-clf-synth`。然后综合质量、新颖程度和不确定性三个维度打分，人工优先看分数高、又和已有 seed 不同的候选，人看的协议和 gold labels 见 `dt-annotator-protocol`。标完更新分类器，进入下一轮。每轮都看冻结 evaluation set 上的 $\Delta$，防止飞轮自我表扬，见 `dt-data-flywheel`。新增类别带来的边际 $\Delta$ 不再增加，或者 contamination rate 上升，就停。

out-of-distribution (OOD) 数据（OOD，即和训练数据明显不同的数据）还要单独处理：做漂移监控，并额外强制从新 cluster 里 sampling。否则旧分类器会把新出现的失败当成噪声过滤掉。

## 追问

**这题在面试里是怎么出的？**
AceOffer 记录过这道 OpenAI 系统设计题，设定包括网页、图和病历，要在极少标签下冷启动；一亩三分地也有一篇标题为「Data Flywheel + Discover and Bootstrap Novel Data」的 phone screen 面经。OpenAI 面经常把这题和 data flywheel 绑在一起问。

**病历、图那种设定怎么办？**
先问许可和 PII。没有许可我就拒题，不设计一条爬取病历的 pipeline。

**用不确定度挑，会不会挖出来全是噪声？**
会。只看熵会挖到乱码，所以要用不确定度、和 seed 的距离、域配额三个维度一起打分。

**和 rejection sampling 是什么关系？**
rejection sampling 是在已有题目上筛出对的 trajectories；这题是在还没有题目的池子里找新题。
