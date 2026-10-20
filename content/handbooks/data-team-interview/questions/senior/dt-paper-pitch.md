---
id: dt-paper-pitch
section: senior
order: 5
level: A
title: Director / VP：论文一分钟怎么讲，才像 data team 的贡献？
quick: "一分钟讲清论文的问题、与原方法的差别、一个可靠结果和局限，再说明适合哪段数据流程。不要从 related work 开始，或只说提出了框架。没有自己的论文也可介绍真正读过的工作，但要明确归属。"
companies:
  - apple
tags:
  - Apple
  - Paper Pitch
  - Publications
realInterview: false
status: published
format: markdown
updatedAt: 2026-10-12
sources:
  - title: Self-Instruct
    url: https://arxiv.org/abs/2212.10560
    type: primary
  - title: "Direct Preference Optimization"
    url: https://arxiv.org/abs/2305.18290
    type: primary
  - title: FineWeb-Edu
    url: https://huggingface.co/spaces/HuggingFaceFW/blogpost-fineweb-edu
    type: primary
  - title: Apple Intelligence Foundation Language Models Tech Report 2025
    url: https://machinelearning.apple.com/research/apple-foundation-models-tech-report-2025
    type: primary
---

一分钟介绍论文，可以先讲问题，再讲方法差别、实验结果或失败模式，最后说明对数据工作有什么用。如果没有发表经历，选一篇真正读过、与数据岗位相关的论文，并明确是介绍别人的工作。

不这么选的理由：guideline 要 NeurIPS / ICML / ICLR / CVPR / ACL 一类文章能在一分钟内讲清核心贡献。从 related work 讲起，或把贡献说成「我们提出了一个新型框架」，在这岗减分。贡献是「多了一个模块」的讲法，同样减分。

## 计时一分钟

先说当时缺少哪种监督或过滤。再解释相对原方法增加了什么检查、减少了什么假设。给出论文中的数字或固定模型只改数据的对照，并说明局限。最后指出它适合 pre / mid / post 或持续迭代的哪一步，见 `dt-pre-mid-post`。

计时 50 到 60 秒。VP 打断就停在完整句。详细方法留待追问。

## 三篇示范（别人的工作）

**Self-Instruct（Wang et al.）。** 「当时公开指令数据太少，模型几乎不会 follow 任意指令。他们用人写种子让模型扩任务再扩答，过滤掉低质和重复。相对当时的人写集，instruction following 从不可用变成可训。局限是教师偏差和没有硬验证。用在 post 的冷启动，进 mid 之前要加 verifier。」

**直接偏好优化（DPO）（Rafailov et al.）。** 「RLHF 要先训 RM 再 PPO，链路长。他们把 Bradley-Terry 写成对策略和参考策略的分类损失，离线就能拉偏好。同样偏好对上可以逼近 RLHF 的效果，少了采样。局限是不能探索离线对之外的回答，长度和标注噪声会直接进策略。有干净偏好、要稳，我用它；要新工具轨迹，我仍要在线采样。」

**FineWeb-Edu。** 「同样从网页出发，用教育价值分类器重筛，固定小模型看知识 / 推理。增益来自留下的 token，不是多训一遍。局限是分类器偏英语教科书味，会误杀代码和论坛。这是 pre / mid 的过滤立场：启发式过猛会扔好 token，和 AFM 2025 减弱规则、加重模型分是同一类决策。」

把这三篇换成你自己的论文时，数字必须是文里的。记不清就说「量级」，不要现场编一个百分点。

## 这岗听贡献的角度

Director 更想知道你改的是数据或监督，还是又堆了一个模块。我会先报这几样：固定算力、只动数据的对照；新的标签定义或验证器（verifier）；失败模式（collapse、长度、locale、污染）你怎么测。

模型结构是配角，除非结构是为了让某种数据变得可训（比如视觉连接器让 caption 对得上）。

## 追问

- **第二篇呢？** 准备一篇和第一篇不同段的：一篇过滤 / 合成，一篇偏好 / 强化学习（RL）。两篇都是 loss 变体，会被当成同一份工作讲两遍。
- **被问局限你答「没有」？** 减分。每篇至少准备一个：分布、验证、规模或负迁移。
- **文章还在投？** 按同样四句讲，标明未发表，不报审稿人意见。
