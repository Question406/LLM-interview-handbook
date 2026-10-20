---
schemaVersion: 1
id: data-team-interview
slug: data-team-interview
title: Apple Foundation Models · Data Team
shortTitle: Data Team 面
edition: V1
audience: Apple Foundation Models / data-centric LLM 岗 · Research Engineer、Data Scientist、MLE
description: >-
  按 Apple Foundation Models data team 的公开面试流程备考：HM 30 分钟讲数据故事，CoderPad 45 分钟写
  pipeline，Panel 四轮技术加一轮 Culture，以及 Director / VP 的立场题。  CoderPad 覆盖去重、污染扫描、
  流式抽样、PII / 密钥、抽取、LID、packing、verifier、图文 CLIP。另有一章通识：什么叫好数据、
  滤太狠、重复 epoch、标签噪声、DataComp 式消融。Panel 覆盖 data flywheel、合成、benchmark 诊断、
  偏好。后训练专章覆盖数学 TIR / Lean、代码 OSS-Instruct、SWE-Gym、工具合成和失败恢复，
  以及 Agent RL：环境即数据、任务过滤、奖励 hack、规模化环境、合成终端任务，
  以及 OpenAI / Meta / Gemini / Anthropic / Tinker 的公开配方。labs 另收别家基模组仍在问的评测台、
  诚实性、分类器笔试、合成坍缩、Phi 教科书、偏好采集。另有一章对照 frontier 发版：
  各家把哪份评测写进模型卡、数据怎么造、测的是哪项能力。
  依据公开 AFM 技术报告、官方数据口径和论文，不编造内部流程或未公开数字。
sections:
  - id: overview
    title: 01 · 备考地图
    description: 整条 loop 怎么排，每轮听什么，和 us-tech 里端侧 Apple 卡怎么分开用
  - id: hm-screen
    title: 02 · Hiring Manager Screen
    description: 数据故事、Why Apple、失败的数据下注、能力和隐私打架
  - id: tech-screen
    title: 03 · Technical Screen
    description: >-
      pipeline、MinHash / SimHash、精确和子串去重、污染 13-gram、水库抽样、PII / 密钥、
      质量 ppl、packing、verifier、CLIP、Count-Min
  - id: panel
    title: 04 · Panel 技术轮
    description: 飞轮、合成、诊断、配比、污染、教师偏差、负迁移、locale、接地、安全
  - id: culture
    title: 05 · Culture
    description: See Around Corners，以及你停过哪一批数据
  - id: senior
    title: 06 · Director / VP
    description: 全生命周期、蒸馏、adapter、ROI、lineage、guided generation、论文一分钟
  - id: labs
    title: 07 · 别家公开题怎么迁到 Apple
    description: >-
      后训练数据还覆盖代码执行合成、工具注入、GUI / 网页轨迹、跨次稳定、R1 蒸馏和政策进思考。
      另补 OpenAI 分类器笔试 / 聊天日志挖概念、Anthropic 诚实评测和 Sleeper、DeepMind 评测台、
      DeepSeek 合成坍缩、Phi 教科书、Cohere 偏好采集、Prompt vs RAG vs 微调。
      题面来自公开面经和论文，答法落到 AFM 约束
  - id: good-data
    title: 08 · 什么是好数据
    description: >-
      好数据的操作定义、多 vs 好、Data Cascade、先数再滤、滤太狠、LIMA、重复 epoch、
      标签噪声、DataComp 消融、改写网页、许可也是质量
  - id: posttrain-data
    title: 09 · 后训练数据
    description: >-
      数学难度带和 TIR、Lean 证明、代码 OSS-Instruct 与隐藏测、SWE-Gym、
      工具合成 / 并行调用 / 失败恢复。Agent RL：环境即数据、任务过滤、奖励 hack、规模化环境、
      合成终端任务，以及 OpenAI / Meta / Gemini / Anthropic / Tinker 的公开配方
  - id: frontier-release
    title: 10 · Frontier 发版报什么评测
    description: >-
      GPQA、HLE、SWE-bench、Terminal-Bench、BrowseComp、OSWorld、MRCR 怎么造，
      测哪项能力，以及 OpenAI / Anthropic / Google / Meta 在哪次发布里报了哪一项
---
