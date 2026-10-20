---
id: dt-good-data-map
section: good-data
order: 1
level: S
title: 通识：什么叫好数据，怎样才算把数据做对？
quick: "好数据应让固定评测中的目标任务变好，保住其他重要能力，并能追溯来源和版本。证明数据有效，要提出可被推翻的假设、做对照与消融，而非只提高质量分。这章用于准备 Panel / HM 的解释；具体实现题仍在 CoderPad 部分。"
companies:
  - apple
tags:
  - Apple
  - Data Quality
  - 备考地图
realInterview: false
status: published
format: markdown
updatedAt: 2026-10-12
sources:
  - title: A Survey on Data Selection for Language Models
    url: https://arxiv.org/abs/2402.16827
    type: primary
  - title: DataComp-LM
    url: https://arxiv.org/abs/2406.11794
    type: primary
  - title: Apple Intelligence Foundation Language Models Tech Report 2025
    url: https://machinelearning.apple.com/research/apple-foundation-models-tech-report-2025
    type: primary
---

Panel 从具体处理流程追问「什么数据值得留」时，先给出你的判断标准，再用论文的一条结论支持它。不要从论文时间线讲起。具体实现题见 `tech-screen`，其他公司的题见 `labs`。

Albalak 综述、DataComp-LM 和 AFM 2025，可以用来说明为什么要按任务选择数据、固定模型验证效果、保留来源和版本。面试需要你解释如何判断，不需要完整文献综述。

## 这章的题目关系

| 问法 | 可参考的公开材料 | 对应题目 |
| --- | --- | --- |
| 好数据到底指什么 | DataComp 固定模型只改变数据 | `dt-good-data-def` |
| 增加数量还是提高质量 | Halevy/Norvig；Chinchilla；Phi；Ng 的 data-centric | `dt-more-vs-better` |
| 数据错误为什么很晚才暴露 | Data Cascades（CHI 2021） | `dt-data-cascade` |
| 过滤前先了解语料 | WIMBD；Datasheets | `dt-inspect-corpus` |
| 过滤太严格会怎样 | FineWeb；AFM 减弱启发式 | `dt-filter-too-hard` |
| 精标 1000 条是否足够 | LIMA；False Promise | `dt-lima-vs-scale` |
| unique token 不够能否重复训练 | Muennighoff datablations，$\sim 4$ epoch | `dt-repeat-epoch` |
| 标签本身是否可靠 | Confident Learning；人际一致性 $\kappa$ | `dt-label-noise` |
| 怎么证明数据有效 | DataComp / FineWeb-Edu 消融 | `dt-hold-model-vary-data` |
| 如何解释选择函数 | Albalak survey：效用与选择机制 | `dt-utility-select` |
| 用 LLM 改写网页是否有效 | WRAP | `dt-wrap-rephrase` |
| 过滤排除了哪些内容或群体 | Dodge 等对 C4 的分析 | `dt-c4-side-effect` |
| 许可和 PII 是否属于质量 | Apple 公开口径；WIMBD 的 PII 分析 | `dt-license-is-quality` |
| 一次数据干预怎样完成 | 持续迭代流程中的具体步骤 | `dt-data-intervention` |

HM 问「你做过最值得的一次数据工作」时，可以用 `dt-good-data-def` 的标准解释收益，再按 `dt-data-story` 讲自己的例子。Director 追问投入是否值得，见 `dt-cost-per-gain`。

苹果的数据限制贯穿这章：许可语料、公开页面、经过验证的合成数据；用户交互默认不进入基础模型。涉及数量和指标，只引用论文或 AFM 明确写过的数字，不推测内部实现。

## 追问

- 和质量分类器那题有什么关系？`dt-quality-clf-synth` 解释质量分如何产生，这章解释为什么分数高还不足以证明数据有用。
- 面试可以引用这些论文吗？可以说论文名字和与问题相关的一条结论。数字要来自论文或 AFM 的公开材料。
