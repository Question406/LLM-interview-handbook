---
id: tencent-data-filter-human-alignment
section: data
order: 102
level: S
title: 腾讯大模型实习：怎样证明自动数据筛选与人工标准对齐？
quick: >-
  「一定对齐」承诺不了，只能持续检验：先把筛选维度写成 rubric，再用独立、分层抽样、没参与调阈值的人审 gold set，把每个自动筛选器当二分类器测
  precision、recall 和分数 calibration，并报标注者一致性。高风险切片单独报，分歧用于改
  rubric、规则或阈值，数据源或分布一变就重新标定。
tags:
  - Tencent
  - Data Filtering
  - Calibration
  - Human Alignment
realInterview: true
status: published
format: markdown
updatedAt: 2026-08-21T00:00:00.000Z
sources:
  - title: 腾讯大模型实习一面 1h（候选人原帖）
    url: 'https://www.nowcoder.com/feed/main/detail/046ac6fcaf4c4b0696c6573416712416'
    type: candidate-first-hand
---

## 真题记录

- 公司：腾讯
- 团队 / 岗位：大模型
- 届别 / 流程：实习；一面（1 小时）
- 面试时间：原帖未披露；帖子发布于 2026-03-12
- 来源类型与可信度：牛客候选人原帖，B（公司、岗位和轮次明确；届别、面试日期未披露）
- 原始措辞：**“介绍一下如何筛选数据(大模型从哪几个维度)，怎么确定模型筛选一定能和人工对齐?”**

我不会承诺「一定对齐」。自动筛选相对人工标准就是一个分类器，对齐只能被检验，没法一次证明。我会讲一套协议：rubric，独立的 gold set，precision / recall / calibration，高风险切片，用 disagreement 更新 annotation guidelines，分布漂移时重新标定。只报过滤通过率是最弱的答法。标注一致性见 `data-annotator-agreement`，分数 calibration 见 `data-reward-calibration`、`fund-calibration`。

先说从哪几个维度筛。内容质量、事实性、指令遵循、安全、去重和 contamination、任务难度、领域覆盖，每一维都要写成可操作的 rubric，口头一句「质量好」没法核对。自动筛选通常是多级门：规则（PII、语言、schema），近重复和评测重叠（`data-contamination`），模型质量分，安全分类器。每一级都是分类器，都要有自己的 precision / recall，级联之后的通过率看不出是哪一级出了问题。

然后是怎么检验对齐。Gold set 有三个要求：**未参与调阈值**，按领域、长度、安全、语言分层抽样，报告标注者一致性。调阈值用的开发集和最终报数的 gold set 必须分开，否则「对齐良好」就是信息泄漏。拿人标的「该留 / 该丢」去对照自动决策，看 precision、recall 和 calibration 曲线。比如质量分 $0.9$ 的样本，人审是不是真有 $90\%$ 通过。通过率高、recall 低，等于把难例滤掉了。一致性只报一个总 κ 不够，要按字段或错误类型分层；标签质量的 acceptance checks 同 `meituan-label-quality`。书面协议里还要写 rubric 版本号、gold 抽样框、双人标注和仲裁规则、每个 filter 的决策表（过 / 不过 / 人工复核），以及阈值锁定的日期。

整体平均会掩盖风险，所以安全、长尾领域、长答案、低资源语言和 borderline examples 要单列。安全切片上的假阴性（该丢却留）代价远高于多滤掉一些无害样本，阈值按业务损失来设，别对着「过多少才够训」去定。这类假阴性还要单独设告警，免得被整体通过率稀释。

最后是 feedback incorporation 与 distribution drift。人审的 disagreement、false-positive / false-negative 都要整理成 hard case，去改 rubric、规则或模型阈值，只调一个全局 cutoff 解决不了。分歧本身就是 rubric 的缺口，不使用这些反馈的话，下一批评测里会重复同一类错杀或漏放。要看滤器在下游到底有没有用，就跑 shadow filter / canary：新旧两份滤器并行，比较下游 holdout 和安全切片，「看起来更干净」不算数，否则容易滤器自嗨、训练指标不动。新数据源、新 teacher model、新安全政策或新安全 vocabulary 一出现，就重新标定，别沿用旧阈值。滤器改动记进 `dataset_version`，训练 run 要能回溯当时用的是哪一版 acceptance checks。评测泄漏和近重复照样走 `data-contamination`、`data-sft-pipeline` 的去污步骤。这份对齐证据是一张会过期的 calibration 表，分布一变，旧的 precision / recall 就失效了。

常见的失败有三种：用调阈值的同一批人审数据报「对齐良好」；只优化通过率，把难例杀掉；线上 query 漂移了还信旧 calibration。

## 追问

**面试官就问「能不能保证一定对齐」，怎么答？**
不承诺。给出可复现的 gold set 协议、分组统计的指标和 feedback incorporation schedule，对齐是持续检验的事。

**人审太贵怎么办？**
分层抽，高风险 oversampling，模型预筛后再人审，定期 calibration，不用一次标完。不抽检导致的静默偏差更贵。

**过滤指标和训练指标打架怎么办？**
以 holdout 任务和安全切片为准，用 canary 看滤器改动的边际增益。通过率升、任务掉，说明难例被杀了。

**gold set 能拿来调阈值吗？**
开发切片可以。最终报告必须用没调过参的 holdout，否则精度会被高估。

**多级 filter 怎么归因？**
每一级单独留日志，记下样本被谁杀掉，再人审抽样确认。只看最终通过名单，没法改 rubric。
