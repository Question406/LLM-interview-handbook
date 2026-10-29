---
schemaVersion: 1
id: apple-interview
slug: apple-interview
title: Apple 面试 Question Book
shortTitle: Apple 面试题本
edition: V1
audience: >-
  Apple Foundation Models / Data Team / AIML / Siri · MLE、Research
  Engineer、Research Scientist
questionRefs: question-refs.json
answerGuides: answer-guides
description: >-
  整理 Apple 标签题与 Foundation Models Data Team 备考材料。专业术语使用英文，中文解释判断和原因；每题提供
  Situation、Task、Approach、Result callout 与口述回答，保留原始代码、测试、来源和技术备查。
sections:
  - id: guide
    title: 01 · 总览与练习路线
    description: 范围、来源边界、二面优先级与全轮次地图
  - id: tensor
    title: 02 · cumsum、Matrix Operations 与 Mask
    description: position IDs、文档编号、pack/unpack、attention、序列概率与matrix扫描
  - id: decoding
    title: 03 · Decoding 解码算法
    description: >-
      batch greedy/sampling 与完整 beam search、独立 EOS、left padding、position IDs、KV
      cache，以及原单序列和进阶 decoding 练习
  - id: coding
    title: 04 · Python 与 ML Coding
    description: 完整训练流程、kNN/k-means、normalization、sampling、缓存与通用编程
  - id: data
    title: 05 · Data Pipeline 与 Data Strategy
    description: 抽取、过滤、deduplication、contamination scan、sampling、data mix、版本与质量实验
  - id: synthetic
    title: 06 · Synthetic Data 与 Self-Improvement
    description: 数学、代码、任务生成、verifier、难度与课程迭代
  - id: evaluation
    title: 07 · Evaluation 与 Capability Debugging
    description: benchmark、evaluation slices、controlled substitution、统计、幻觉、RAG 与回归
  - id: alignment
    title: 08 · Reward、Preference 与 Alignment
    description: 偏好采集、RM、DPO、RL、judge、奖励偏差和安全边界
  - id: multimodal
    title: 09 · Multimodal：Vision、Audio 与 Video
    description: 图文grounding、视觉编码、语音语义、生成图像与时序数据
  - id: ondevice
    title: 10 · On-Device、Privacy 与 Inference
    description: ANE、quantization、KV、投机、on-device / server分工与隐私反馈
  - id: systems
    title: 11 · Agent 与系统设计
    description: tool-use trajectories、环境、失败恢复、搜索、服务与长视频摘要
  - id: projects
    title: 12 · 项目深挖与研究陈述
    description: 数据项目、Why Apple、方案辩护、研究价值与投入决策
  - id: culture
    title: 13 · Culture 与协作
    description: See Around Corners、简化、信任、失败、纠错与发布决策
  - id: mock
    title: 14 · 全流程模拟与个人材料
    description: 两套45分钟技术卷、附件诊断、feedback loop实验、五场Panel、Director及个人证据模板
  - id: research
    title: 15 · 研究案例与跨团队迁移
    description: 原 Data Team 手册的公开研究案例与其他实验室资料，保留归属
---

