---
id: frontier-coding-guide-2026-10-28
section: overview
order: 0
level: S
title: 五家公司 Coding 新题：Meta、xAI、OpenAI、Humans&、Thinking Machines
quick: >-
  查重后新增九道可运行练习：Meta 三道、OpenAI 两道、xAI 一道、Humans& 一道，以及 Thinking Machines
  官方技术文章衍生的两道机制练习。各卡明确来源类别与接口约定。
companies:
  - meta
  - xai
  - openai
  - humansand
  - thinking-machines
tags:
  - Frontier Coding 2026-10-28
  - 练习导航
realInterview: false
status: published
format: markdown
updatedAt: '2026-10-28'
sources:
  - title: Meta 候选人自述：ML Research Scientist loop
    url: >-
      https://www.reddit.com/r/leetcode/comments/1r37w7q/meta_ml_research_scientist_interview_experience/
    type: interview
  - title: Meta 候选人自述：2D convolution
    url: >-
      https://www.reddit.com/r/leetcode/comments/1reuwrd/meta_ai_coding_interview/
    type: interview
  - title: Humans& 第一手记录：DrustZ 找工记（3）
    url: 'https://www.uscardforum.com/t/topic/535363'
    type: interview
  - title: Thinking Machines Lab coding round 公开讨论，2026-08
    url: 'https://www.1point3acres.com/home/thread/1185730'
    type: interview
  - title: Thinking Machines coding rounds 公开讨论，2026-10
    url: 'https://www.1point3acres.com/interview/discussion/1191996'
    type: interview
  - title: Thinking Machines Lab：batch invariance 官方文章
    url: >-
      https://thinkingmachines.ai/blog/defeating-nondeterminism-in-llm-inference/
    type: primary
  - title: Thinking Machines Lab：LoRA 官方文章
    url: 'https://thinkingmachines.ai/blog/lora/'
    type: primary
  - title: OpenAI indexed sequence：二手候选人记录
    url: >-
      https://www.reddit.com/r/OfferEngineering/comments/1wzedra/openai_senior_software_engineer_interview_it_felt/
    type: interview
  - title: OpenAI tree message counting：公开候选人记录
    url: 'https://www.screna.ai/experience/aa1b5634-5b22-42a3-9077-5787f791e718'
    type: interview
  - title: xAI offline autocomplete：二手题型目录
    url: 'https://aceoffer.app/interviews/xai_autocomplete_input_box'
    type: interview
---

## 回答思路

> **先选方向：** ML implementation 与常规 SWE coding 分开练。  
> **再看来源：** 候选人自述、平台二手整理、官方机制练习分别标注。  
> **完成标准：** 先读完整题面，再写实现、解释选择并运行 assertions。

## 全部题目入口

后续已建立[五家公司 Coding 独立题本](http://127.0.0.1:3000/?book=frontier-coding&section=guide&question=frontier-coding-full-map)，汇总 **117 张可运行 Coding Cards**，含第二批新增 **20 张**。下方九张为第一批增量清单；全部题与本轮新增请从独立题本浏览。

## 新增九张 Coding Cards

截至 2026-10-28，本批查重后补充九道独立练习，统一标签为 **Frontier Coding 2026-10-28**。所有新卡都有输入输出、示例、回答思路、完整 Python 实现与测试。

| 公司 | 题目 | 来源类别 |
| --- | --- | --- |
| meta | [Meta ML Coding：从零实现 batched 2D convolution](http://127.0.0.1:3000/?book=us-tech&section=meta&question=meta-conv2d-from-scratch) | 候选人题型报告；具体接口由手册整理 |
| meta | [Meta：Tree diameter 改成按 nodes 计数](http://127.0.0.1:3000/?book=us-tech&section=meta&question=meta-tree-diameter-node-count) | 候选人题型报告；具体接口由手册整理 |
| meta | [Meta：Longest Valid Parentheses 与 sentinel index](http://127.0.0.1:3000/?book=us-tech&section=meta&question=meta-longest-valid-parentheses) | 候选人题型报告；具体接口由手册整理 |
| openai | [OpenAI：Indexed sequence、插入与便宜的 checkpoints](http://127.0.0.1:3000/?book=us-tech&section=openai&question=openai-indexed-sequence-checkpoints) | 候选人题型报告；具体接口由手册整理 |
| openai | [OpenAI：只用 async messages 给整棵树计数](http://127.0.0.1:3000/?book=us-tech&section=openai&question=openai-async-tree-count-idempotency) | 候选人题型报告；具体接口由手册整理 |
| xai | [xAI：Offline autocomplete 的 prefix top-K index](http://127.0.0.1:3000/?book=us-tech&section=xai&question=xai-offline-autocomplete-trie) | 候选人题型报告；具体接口由手册整理 |
| humansand | [Humans&：Top-p live coding 与现场 debug](http://127.0.0.1:3000/?book=us-startup&section=humansand&question=humansand-top-p-live-debug) | 候选人题型报告；具体接口由手册整理 |
| thinking-machines | [Thinking Machines 机制练习：Batch-invariant RMSNorm](http://127.0.0.1:3000/?book=us-startup&section=thinking-machines&question=tml-batch-invariant-rmsnorm-reference) | 官方研究文章衍生练习 |
| thinking-machines | [Thinking Machines 机制练习：LoRA Linear、初始化与 gradients](http://127.0.0.1:3000/?book=us-startup&section=thinking-machines&question=tml-lora-linear-forward-gradients) | 官方研究文章衍生练习 |

## 先练哪些

针对 ML / Research Engineer，先做 convolution、Humans& top-p debug、RMSNorm 和 LoRA；再做 async tree count 与 persistent indexed sequence，补上状态与工程实现。Tree diameter、parentheses 和 autocomplete 可用于练计数单位、stack invariant 与数据结构选择。

Meta 报告里的 ML algorithm coding 与 AI-enabled repository debugging 是不同形式。两份自述分别给出了 convolution 和标准算法方向；已有 [[meta-ai-coding]] 讨论工具使用与项目调试。

## 已有题目，继续复用

本次也找到以下题型的更多公开目录，它们已有独立卡片，保留原入口：

- xAI：[[xai-kv-txn]]、[[xai-lru-cache]]、[[p3a-xai-flatten-unflatten-nested-structure]]、[[p3a-xai-twitter-spaces-active-hours]]、[[p3a-xai-speculative-edits]]、[[p3a-xai-input-field-review]]。
- OpenAI：[[p3a-openai-gpu-credits]]、[[p3a-openai-time-based-kv-store]]、[[p3a-openai-in-memory-database-sql]]、[[p3a-openai-numpy-1nn-wx-b]]、[[p3a-openai-sharded-matmul-backprop-debugging]]。

## Thinking Machines Lab 的查找结果

2026-08 与 2026-10 的一亩三分地帖子提到 coding screen 或询问题目，公开正文没有给出可重建的具体算法题。两张新增卡来自该 Lab 的官方技术文章，类别为“公开机制练习”，题卡的 realInterview 标记为 false。

搜索结果还出现菲律宾 Thinking Machines 的 intern / engineering-consultant 面经，公司的职位、地点与招聘主体不同；本批采用 thinkingmachines.ai 的官方材料。某些培训站给出的“likely questions”单独作为备考建议，不累计成候选人题目数量。

## 实现与验证

在含 NumPy、PyTorch 的 Python 环境运行 scripts/check-frontier-coding-new.py，会直接抽取九张 Markdown 中展示的实现与 tests 执行。新题 source links 在各卡底部保留；source facts 与手册补充的接口、constraints、tests 在题面分开说明。
