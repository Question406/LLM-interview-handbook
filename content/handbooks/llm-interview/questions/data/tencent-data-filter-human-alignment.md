---
id: tencent-data-filter-human-alignment
section: data
order: 102
level: S
title: 腾讯大模型实习：怎样证明自动数据筛选与人工标准对齐？
quick: "用独立、分层抽样的人审数据作 gold set，对比自动筛选与人工判断，测精确率、召回率、分数校准和标注者一致性。高风险样本单独报告；有分歧时检查标准、筛选器或阈值，并持续监控线上分布变化，不能只报通过率。"
tags:
  - Tencent
  - Data Filtering
  - Calibration
  - Human Alignment
realInterview: true
status: published
format: markdown
updatedAt: 2026-08-21
sources:
  - title: 腾讯大模型实习一面 1h（候选人原帖）
    url: https://www.nowcoder.com/feed/main/detail/046ac6fcaf4c4b0696c6573416712416
    type: candidate-first-hand
---

## 真题记录

- 公司：腾讯
- 团队 / 岗位：大模型
- 届别 / 流程：实习；一面（1 小时）
- 面试时间：原帖未披露；帖子发布于 2026-03-12
- 来源类型与可信度：牛客候选人原帖，B（公司、岗位和轮次明确；届别、面试日期未披露）
- 原始措辞：**“介绍一下如何筛选数据(大模型从哪几个维度)，怎么确定模型筛选一定能和人工对齐?”**

常见误区是：承诺「一定对齐」或只报过滤通过率。自动筛选相对人标是分类器，对齐只能被检验、不能被一次证明。正确叙事：rubric → 独立 gold set → precision / recall / 校准 → 高风险切片 → disagreement 回流 → 分布漂移时重标定。标注一致性见 `data-annotator-agreement`，分数校准见 `data-reward-calibration`、`fund-calibration`。

## 维度、gold set 与指标

先在内容质量、事实性、指令遵循、安全、去重 / contamination、任务难度和领域覆盖上写成可操作 rubric，而不是口头「质量好」。Gold set 必须：**未参与调阈值**、分层抽样（领域、长度、安全、语言），并报告标注者一致性。每个 filter 当二分类器：人标「该留 / 该丢」对照自动决策，看 precision、recall 和校准曲线。通过率高但 recall 低，等于把难例滤掉。标签质量门禁同 `meituan-label-quality`。

整体平均会掩盖风险。必须单列安全、长尾领域、长答案、低资源语言与边界样本。安全 slice 假阴性（该丢却留）优先于多滤掉一些无害样本。

## 回流、影子实验与漂移

把人审 disagreement、false-positive / false-negative 回流成 hard case，改 rubric、规则或模型阈值，而不是只调一个全局 cutoff。用 shadow filter / canary 比较「过新滤器」与「过旧滤器」对下游 eval 的影响，避免滤器自嗨、训练指标不动。新数据源、新教师模型或新安全政策出现时，重新标定，不要沿用旧阈值。评测泄漏与近重复仍走 `data-contamination`、`data-sft-pipeline` 的去污步骤。

失败模式：用调阈值的同一批人审报「对齐良好」；只优化通过率导致难例被杀；线上 query 漂移后仍信旧校准。

## 把「对齐」写成可审计协议

面试官要听的是协议而不是形容词。书面约定至少包括：rubric 版本号、gold 抽样框（按领域 / 长度 / 安全分层）、双人标注与仲裁规则、每个 filter 的决策表（过 / 不过 / 人工复核）、以及阈值锁定日期。调阈值用的开发集与最终报数的 gold set 必须分开，否则「对齐良好」是信息泄漏。一致性只报一个总 κ 不够，要按字段或错误类型分层，见 `data-annotator-agreement`。

自动筛选常见是多级门：规则（PII、语言、schema）→ 近重复 / 评测重叠（`data-contamination`）→ 模型质量分 → 安全分类器。每一级都是分类器，都要有自己的 precision / recall，不要只报级联后的通过率。安全假阴性（该丢却留）的代价远高于多丢一些无害样本，阈值应根据业务损失设置，而不是对着「过多少才够训」。模型打分还要看校准：分数 $0.9$ 是否真有 $90\%$ 人审通过，曲线见 `fund-calibration`、`data-reward-calibration`。

线上要有漂移检测：新数据源、新教师、新安全词表都触发重标定。Canary 是两份滤器并行，比较下游 holdout 与安全 slice，而不是比较「看起来更干净」。滤器改动记入 `dataset_version`，训练 run 必须能回溯当时用的哪一版门禁。对齐证据是一张会过期的校准表：分布一变，旧 precision / recall 立刻失效。高风险 slice 的假阴性要单独设告警，不能被整体通过率稀释。人审 disagreement 不是噪声，而是 rubric 缺口；不回流就会在下一批评测里重复同一类错杀或漏放。

## 追问

- **「一定对齐」怎么答？** 不承诺。给出可复现的 gold set 协议、分组统计指标和回流节奏。对齐是持续检验，不是一次证明。
- **人审太贵怎么办？** 分层抽、高风险过采样、模型预筛后再人审；定期校准，不是一次性标完。贵的是不抽检导致的静默偏差。
- **过滤和训练指标打架？** 以 holdout 任务与安全 slice 为准，用 canary 看滤器改动的边际增益。通过率升、任务掉，说明难例被杀。
- **gold set 能不能用来调阈值？** 开发切片可以，最终报告必须用未调参的 holdout，否则精度被高估。
- **多级 filter 如何归因？** 每级单独留日志：被谁杀掉、人审抽样确认。只看最终通过名单无法改 rubric。
