---
id: drustz-ca0d825886bbce963b
section: anthropic
order: 4
level: A
title: Performance Engineer Modeling
quick: locally-saved-research-summary · Performance Engineer Modeling
companies:
  - anthropic
tags:
  - DrustZ
  - locally-saved-research-summary
  - Anthropic · 题库与复习指南
realInterview: false
status: published
format: markdown
updatedAt: '2026-10-28'
sources:
  - title: DrustZ / Mingrui Zhang · pinned source
    url: >-
      https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/1acre3points_crawl/data/questions.json
    type: primary
  - title: 作者记录的原始来源
    url: >-
      https://www.1point3acres.com/interview/problems/company/anthropic/performance-engineer-modeling
    type: secondary
---
> DrustZ 整理的复习指南。公司与轮次信息沿用作者的来源记录。

## SWE/RE Virtual Onsite 结构（2026）：coding + system design + project deep dive + culture，新增 AI-assisted coding 轮

标准 VO 四轮：(1) Coding（题库题，如 Q6 tokenizer/Bootloader/dedupe 3-part 版）；(2) System Design（Prompt Playground / inference API / image processing）；(3) Project deep dive / technical presentation（讲自己项目，40 min HM 轮问 career development 和 impact 的经典 behavioral）；(4) Culture/values（AI safety alignment，最常见挂点）。RE onsite 为 coding + ML task + behavioral + culture fit（interview thread 1137418）。2026 新增：有 onsite coding 轮明确允许并要求'使用 AI 工具编写和审查代码'，提供 Claude Code CLI 访问（Telegram 镜像）。店面规则：不许用 AI 工具，但从网上正当搜到的代码可以抄。流程前置：OA→recruiter chat（有人 OA 完 2 小时就被联系）→HM chat 20 min team match→店面→VO。EM loop 另有：HR、HM、culture fit、leadership、coding、tech project discussion、performance modeling、design review（interview thread 1137727）。

### 解题与准备提示

AI-assisted 轮考察点是驾驭 agent 的工作流：任务拆解、给 Claude Code 写清晰 spec、review 生成代码、验证；平时用 Claude Code 做真实项目即最好的准备。

---

### 本地面经中的具体追问

现有本地笔记把该轮与 thread-1157758 对应，并记录了两个明确 follow-up：

1. 给定一个输入 activation（例如 m×k）、一个输出 activation（例如 m×n）和模型权重（k×n），判断它们能否同时放进 VRAM，并解释计算与通信成本。
2. 比较两张 GPU 上的 Pipeline Parallelism 与 Tensor Parallelism：端到端耗时、每卡内存占用以及两种方案的 trade-off。

准备时应能从矩阵乘 FLOPs、参数/activation 字节数、显存容量与互连带宽估算瓶颈，并说明 arithmetic intensity、流水线 bubble、tensor-parallel all-reduce 成本。以上来自用户本地 `questions_and_solutions.md` 的既有笔记，不代表未公开的逐字题面。

### 来源与内容类型

- Content kind: `locally-saved-research-summary`
- [原始来源](https://www.1point3acres.com/interview/problems/company/anthropic/performance-engineer-modeling)

---

来源：[DrustZ / Mingrui Zhang · 1acre3points_crawl/data/questions.json](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/1acre3points_crawl/data/questions.json)。作者整理资料；许可和第三方来源范围见阅读指南。
