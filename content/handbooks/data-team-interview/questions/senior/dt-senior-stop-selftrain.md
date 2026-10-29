---
id: dt-senior-stop-selftrain
section: senior
order: 11
level: S
title: Director 情景：self-training 连续三轮涨分，为什么你仍可能建议暂停？
quick: 连续涨分可能来自共同评价盲点、模板重复和对固定测试的过度适配。是否继续，应看独立迁移、覆盖、真实错误和单位预算收益，并让生成、筛选与最终验证保持足够独立。
companies:
  - apple
tags:
  - Apple
  - AFM 专项 2026-10
  - 情景练习
realInterview: false
status: published
format: markdown
collapseAnswer: true
updatedAt: '2026-10-26'
sources:
  - title: Apple Intelligence Foundation Language Models Tech Report 2025
    url: >-
      https://machinelearning.apple.com/research/apple-foundation-models-tech-report-2025
    type: primary
  - title: The FineWeb Datasets
    url: 'https://arxiv.org/abs/2406.17557'
    type: primary
---

## 题目描述

原创决策题。建议先用 90 秒给结论，再展开 20 分钟。

模型用自己生成的数据做了三轮 SFT，每轮内部 benchmark 都上涨；新模板盲测基本不动，生成样本重复率上升，审核员发现错误答案越来越流畅。负责人希望再给一轮两倍预算。

你会支持、缩小还是暂停？请提出可改变自己决定的证据，给出下一笔预算的使用方案，并解释何时将数据投入 pre-training、mid-training 或 post-training。以上为假设场景，不是内部事实。

## 解题思路与参考答案

当前证据下暂停扩倍，保留 checkpoint，将下一笔小预算用于独立评测和 verifier 审计。理由是内部指标与迁移脱节，继续放大可能强化共同错误；但还不能仅凭这些现象 assertion 已经发生 model collapse。

### 什么证据会改变决定

在未用于选数据和调参的新任务家族上，固定 inference budget 后稳定提升；重复 cluster 占比可控；独立验证的错误 acceptance rate 没有恶化；相对同预算的外部 teacher 或人工 seed 方案更有收益。应事先规定成功指标与停止规则，不能看到哪项涨就临时改目标。

### 下一笔预算怎么花

先从三轮数据各 sampling，追溯 seed、生成器、筛选器与 source groups，检查是否在循环放大相同模板。用独立验证补充过程和结果检查，并加入真实授权的新来源或专家设计的新任务 seed。再做同预算的小对照：原 self-training 配方，对比新增独立 seed 与验证机制的配方。人工审核应优先查错误高置信与新覆盖区，而不是重复审核高分简单题。

### 数据放在哪个阶段

基础知识或广泛语言覆盖缺口，考虑基础 pre-training 数据策略；已有基础能力但某个领域、模态或 long context 分布不足，可考虑 continued pre-training，也常被称为 mid-training，具体阶段定义依 training recipe 而定；行为格式、工具协议、偏好与拒答，通常先比较 SFT 或 preference optimization 等 post-training 干预。阶段名称不能代替实验：还要控制算力、遗忘风险和目标能力收益，不能所有问题都用 SFT 修。

## 面试追问

**没有外部 teacher 还能自我提升吗？** 可以通过执行环境、规则验证、搜索和新任务生成获得额外有效信号；核心是引入可验证的信息与选择压力，而非把同一错误重新改写。

**公开 benchmark 持续涨不也是证据吗？** 是证据之一，但反复用它决定数据与超参会产生适配，需独立家族和盲测验证迁移。

**高层回答该避免什么？** 避免只报算法名或笼统反对 self-training。要给当前决定、改变决定的证据、预算用途和可停止的条件。
