---
id: dt-good-data-map
section: good-data
order: 1
level: S
title: 通识：什么叫好数据，怎样才算把数据做对？
quick: >-
  这章回答两件事：什么数据值得留，怎样证明一批数据有用。好数据让固定评测里的目标任务变好、保住其他重要能力、能追溯来源和版本；证明它要靠可被推翻的假设、对照和
  ablation study，质量分只是其中一个信号。这章准备 Panel / HM 的解释，实现题在 CoderPad 部分。
companies:
  - apple
tags:
  - Apple
  - Data Quality
  - 备考地图
realInterview: false
status: published
format: markdown
updatedAt: 2026-10-12T00:00:00.000Z
sources:
  - title: A Survey on Data Selection for Language Models
    url: 'https://arxiv.org/abs/2402.16827'
    type: primary
  - title: DataComp-LM
    url: 'https://arxiv.org/abs/2406.11794'
    type: primary
  - title: Apple Intelligence Foundation Language Models Tech Report 2025
    url: >-
      https://machinelearning.apple.com/research/apple-foundation-models-tech-report-2025
    type: primary
---

这张卡用来找题：按面试官的问法在下面的表里找到对应的卡。整章其实就回答两件事，什么数据值得留，以及怎样证明一批数据确实有用。简单说，好数据要让固定评测里的目标任务变好，同时保住其他重要能力，还能追溯来源和版本；要证明它有效，就提一个能被推翻的假设，做对照和 ablation study，质量分只是其中一个信号。

Panel 常从一条具体的处理流程追问「什么数据值得留」。回答时先说你的判断标准，再拿一篇论文的一条结论撑一下，别从论文时间线讲起。Albalak 综述能说明为什么要按任务选数据，DataComp-LM 能说明为什么要固定模型验证效果，AFM 2025 能说明为什么要保留来源和版本。面试要听的是你怎么判断，文献点到为止就够了。具体的实现题在 `tech-screen`，其他公司的题在 `labs`。

## 这章的题目关系

| 问法 | 可参考的公开材料 | 对应题目 |
| --- | --- | --- |
| 好数据到底指什么 | DataComp 固定模型只改变数据 | `dt-good-data-def` |
| 增加数量还是提高质量 | Halevy/Norvig；Chinchilla；Phi；Ng 的 data-centric | `dt-more-vs-better` |
| 数据错误为什么很晚才暴露 | Data Cascades（CHI 2021） | `dt-data-cascade` |
| 过滤前先了解 corpus | WIMBD；Datasheets | `dt-inspect-corpus` |
| 过滤太严格会怎样 | FineWeb；AFM 减弱启发式 | `dt-filter-too-hard` |
| 精标 1000 条是否足够 | LIMA；False Promise | `dt-lima-vs-scale` |
| unique token 不够能否重复训练 | Muennighoff datablations，$\sim 4$ epoch | `dt-repeat-epoch` |
| 标签本身是否可靠 | Confident Learning；人际一致性 $\kappa$ | `dt-label-noise` |
| 怎么证明数据有效 | DataComp / FineWeb-Edu ablation study | `dt-hold-model-vary-data` |
| 如何解释选择函数 | Albalak survey：效用与选择机制 | `dt-utility-select` |
| 用 LLM 改写网页是否有效 | WRAP | `dt-wrap-rephrase` |
| 过滤排除了哪些内容或群体 | Dodge 等对 C4 的分析 | `dt-c4-side-effect` |
| 许可和 PII 是否属于质量 | Apple 公开说明；WIMBD 的 PII 分析 | `dt-license-is-quality` |
| 一次数据干预怎样完成 | 持续迭代流程中的具体步骤 | `dt-data-intervention` |

## 追问

**HM 问「你做过最值得的一次数据工作」，怎么接到这章？**
先用 `dt-good-data-def` 的标准讲清收益在哪，再按 `dt-data-story` 讲你自己的例子。

**Director 追问这些投入值不值，看哪题？**
看 `dt-cost-per-gain`，那题讲怎么把 token、费用和指标变化放在一起算。

**这章和质量分类器那题什么关系？**
`dt-quality-clf-synth` 讲质量分是怎么产生的，这章讲为什么分数高还证明不了数据有用。

**面试时可以引用这些论文吗？**
可以，说论文名和跟问题相关的一条结论就够了。涉及数量和指标时，只用论文或公开报告明确写过的数字，不推测内部实现。
