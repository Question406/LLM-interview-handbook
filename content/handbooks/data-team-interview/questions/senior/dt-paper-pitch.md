---
id: dt-paper-pitch
section: senior
order: 5
level: A
title: Director / VP：论文一分钟怎么讲，才像 data team 的贡献？
quick: "一分钟按顺序讲：论文要解决的问题、和原方法的差别、一个可靠的结果、局限，最后说明它适合数据流程的哪一段。从 related work 讲起，或者只说「提出了一个框架」，听的人抓不到贡献。没有自己的论文，可以介绍真正读过的工作，但要说明是别人的。"
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

一分钟按这个顺序讲：先讲问题，再讲方法和原方法的差别，然后给一个实验结果或失败模式，说明局限，最后说它对数据工作有什么用。没有发表经历，就选一篇真正读过、和数据岗位相关的论文，并说明是在介绍别人的工作。

## 这个岗位听的是什么

岗位 guideline 要求能在一分钟内讲清 NeurIPS / ICML / ICLR / CVPR / ACL 一类文章的核心贡献。从 related work 讲起，或者把贡献说成「我们提出了一个新型框架」「多了一个模块」，在这个岗位都会减分。

Director 更想知道你改的是数据或监督，还是又堆了一个模块。所以我会优先讲这几样：固定算力、只动数据的对照；新的标签定义或验证器（verifier）；失败模式（collapse、长度、locale、污染）你怎么测。模型结构是配角，除非结构是为了让某种数据变得可训，比如视觉连接器让 caption 对得上。

## 一分钟怎么分配

先说当时缺少哪种监督或过滤。再说相对原方法增加了什么检查、减少了什么假设。然后给论文中的数字，或者固定模型只改数据的对照，并说明局限。最后指出它适合 pre / mid / post 或持续迭代的哪一步，见 `dt-pre-mid-post`。

控制在 50 到 60 秒。VP 打断时，在一个完整的句子处停下，方法细节留给追问。

## 三篇示范（别人的工作）

**Self-Instruct（Wang et al.）。** 「当时公开的指令数据太少，模型几乎不会遵循任意指令。他们用人写的种子让模型扩写任务、再生成回答，并过滤掉低质和重复的样本。和当时的人写数据集相比，instruction following 从不可用变成了可训。局限是有教师偏差，也没有硬验证。我会把它用在 post 的冷启动，进 mid 之前要加 verifier。」

**直接偏好优化（DPO）（Rafailov et al.）。** 「RLHF 要先训 RM 再跑 PPO，链路长。他们把 Bradley-Terry 写成策略相对参考策略的分类损失，离线就能学偏好。在同样的偏好对上可以逼近 RLHF 的效果，还省掉了采样。局限是无法探索离线偏好对之外的回答，长度偏差和标注噪声会直接进入策略。偏好数据干净、要求稳定时我用它；要学新的工具轨迹，我仍然要在线采样。」

**FineWeb-Edu。** 「同样从网页出发，用教育价值分类器重新筛选，再用固定的小模型看知识和推理的变化。增益来自筛选后留下的那批 token，训练量并没有加。局限是分类器偏向英语教科书的风格，会误杀代码和论坛。这是 pre / mid 阶段的过滤立场：启发式过猛会扔掉好 token，和 AFM 2025 减弱规则、加重模型打分是同一类决策。」

换成你自己的论文时，数字必须是论文里的。记不清就说量级，不要现场编一个百分点。

## 追问

- **还有第二篇吗？** 准备一篇和第一篇处在不同阶段的：一篇讲过滤或合成，一篇讲偏好或强化学习（RL）。如果两篇都是 loss 变体，会被当成同一份工作讲了两遍。
- **被问局限时答「没有」？** 会减分。每篇至少准备一个局限：分布、验证、规模或负迁移。
- **文章还在投稿？** 按同样的四句讲，标明未发表，不提审稿人意见。
