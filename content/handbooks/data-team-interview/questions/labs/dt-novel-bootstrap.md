---
id: dt-novel-bootstrap
section: labs
order: 2
level: S
title: OpenAI：无标语料里怎么挖「新」数据并 bootstrap？Apple 怎么改口？
quick: "从冻结评测的失败案例和许可数据中找种子，再用小分类器给未标注数据评分。结合质量、新颖程度和不确定性，挑出值得人工检查的样本，更新分类器后继续筛选。分类器可用合成标签启动，但要按语言校准，并监控新数据是否真正改善评测。"
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

种子可以来自冻结评测失败、内部研究集和许可领域的难例。未标注候选来自 Applebot、许可库以及验证过的合成数据。用少量种子训练分类器，结合质量、新颖程度和不确定性评分，人工优先检查高分且不同于已有种子的候选。再把标注结果用于更新分类器，继续筛选。如果新增类别带来的边际 $\Delta$ 不再增加，或污染率上升，就停止。

不这么选的理由：OpenAI 面经把这题和 data flywheel 绑在一起，标准答从用户日志起盘。把那套原样搬过来，通道就不成立。上一个无监督聚类就收工也不够：新颖不等于离群垃圾。

接到苹果：bootstrap 分类器可以按 FineWeb-Edu 那样用合成标签起盘，按语言校准，见 `dt-quality-clf-synth`。人看的协议和金标见 `dt-annotator-protocol`。每圈看冻结集 $\Delta$，防飞轮自我表扬，见 `dt-data-flywheel`。分布外数据（OOD，即与训练数据明显不同的数据） 要有漂移监控，再加一刀强制抽新簇，旧分类器会把新失败当噪声。「新颖」往往是产品路径还没写进门禁的类：某种海报版式、某 locale 的指令、工具第二跳空结果。和 `dt-see-around-corners` 同一动作，只是题面写成了挖掘系统。

公开锚点：AceOffer 记过 OpenAI 系统设计（网页、图、病历，极少标签冷启动）；一亩三分地有「Data Flywheel + Discover and Bootstrap Novel Data」phone screen 标题。

## 追问

- **病历 / 图那种设定怎么办？** 先问许可和 PII。没有许可我就拒题，不设计一条爬取病历的管线。
- **不确定度会不会全是噪声？** 会。不确定 × 和种子的距离 × 域配额，三维打分。只看熵会挖到乱码。
- **和拒绝采样什么关系？** 拒绝采样是已有题上滤对的轨迹。本题是在还没有题的池子里找新题。
