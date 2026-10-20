---
id: openai-mm-eval
section: openai
order: 33
level: A
title: OpenAI：多模态评测坑，图文泄漏、OCR 当语义、MMMU 一类怎么拆
quick: >-
  先跑盲文：不给图只给题干，分还很高就是泄漏或语言先验。MMMU 学院科题目，文本选项经常自带答案。MMStar 把必须看图的题筛出来。OCR
  抄板上的字和「读懂图」不是同一能力，要分切片。分辨率、裁切、是否把选项印在图上，全部锁进协议。
tags:
  - OpenAI
  - Multimodal
  - Evaluation
  - MMMU
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-23
sources:
  - title: MMMU — A Massive Multi-discipline Multimodal Understanding Benchmark
    url: https://arxiv.org/abs/2311.16502
    type: primary
  - title: Are We on the Right Way for Evaluating Large Vision-Language Models? (MMStar)
    url: https://arxiv.org/abs/2403.20330
    type: primary
  - title: GPT-4V System Card
    url: https://openai.com/index/gpt-4v-system-card/
    type: primary
  - title: openai/simple-evals
    url: https://github.com/openai/simple-evals
    type: primary
---

## 题怎么来的

GPT-4V / GPT-4o 发数字时，对外是 MMMU、文档、图表一类；对内仍要防刷榜，纪律见 `openai-eval-harness`。多模态多了两种污染：题干自己能答，以及训练见过这张图。MMStar（Chen et al.）把 Gemini 在不给图时 MMMU 仍远超随机写进论文。这题不是背榜名，是你会不会拆泄漏、OCR、真正的视觉推理。原生 token 预算见 `openai-mm-gpt`。

## 盲文基线：先把图关掉

我会把每条样本跑三遍：

1. 图+文 $S_v$。常规协议。
2. 只文 $S_{wv}$。图换成空白或删掉 image part，题干和选项不动。
3. 只视觉塔对应的纯 LM $S_t$（若你有基座）。用来看多模态训练是不是在背题。

MMStar 定义 multimodal gain $MG=S_v-S_{wv}$，leakage $ML=\max(0,S_{wv}-S_t)$。$S_{wv}$ 比随机高一大截，这张榜就不能当「看图能力」。MMMU 上公开数字：强 LM 不看图也能到四十出头，因为学院选择题的选项和题干已经泄漏了学科常识。面试先报盲文，再报带图；只报一个 MMMU 总分，评委会当没测视觉。

泄漏来源要分开讲：

- **题面自包含。** 「图中是哪种已灭绝的鸟？」选项里只有一种是鸟。不看图也能猜。
- **选项印在图上。** 模型 OCR 出 A/B/C 旁边的文字，再当阅读理解。这是 OCR，不是空间推理。
- **训练见过题。** 网页、教材、MMMU 原图进了预训练。n-gram 扫文本不够，图还要哈希 / 近邻。Canary 同 `openai-eval-harness`。
- **开发见过图。** 对着公开测试图调分辨率、裁切、输入提示（prompt）。「换了 high-detail 涨 3 点」可能是刷协议，不是模型变强。

Holdout 必须是从未用来选 checkpoint 的图。公开 MMMU 只能沟通，不能当唯一升模型信号。

## OCR 切片和语义切片不要合成一个分

「看图」至少三摊，平均会互相掩盖：

- **OCR / 抄写。** 白板公式、UI 字符串、发票数字。应用层可用外接 OCR 当对照。模型高分若全来自抄写，换一张没有字的示意图会塌。
- **图表 / 布局。** 轴、图例、哪根柱子更高。要看相对位置，纯 OCR 不够，但题干里的「如图所示，2019 年最大」若把数字又写一遍，又变回文本题。
- **学科推理（MMMU 声称的）。** 电路图、病理切片、乐谱。必须看图才能选。MMMU-Pro 后来加了「去文本可答题」和 vision-only 设定，方向就是把泄漏挖走。

协议锁死：分辨率（low vs high，见 `openai-mm-gpt`）、是否把选项画进图、解码温度、是否允许工具。GPT-4V 系统卡自己也按类别谈局限；内部 harness 要按类切片，不要一个 macro。判分：选择题对选项顺序敏感；开放描述不要用被测模型当法官，法官隔版本，同 `openai-eval-harness`。

常见误区是：用带图的思维链（CoT）prompt 和别人的盲文比；把 OCR 榜当 MMMU；不跑 $S_{wv}$。指令遵循仍要单独测，见 `openai-if-eval`：「用 JSON 列出图中物体」失败可能是格式，不是没看见。

## 追问

- **盲文很高一定是作弊吗？** 不一定。有的题就是语言知识。要人审一小部分「必须看图」的金标，不能只看平均。
- **提高分辨率算新模型还是新协议？** 新协议。数字要并排报 low / high，不要把 high 的新高写进同一条曲线。
- **视频评测多了什么？** 抽帧率和时间戳。描述对、事件安错分钟，不算过。抽样必须固定。
- **和 Arena？** 人比看图回答会把文笔和礼貌混进视觉分。私有看图 holdout 仍要留，见 `openai-eval-harness`。
