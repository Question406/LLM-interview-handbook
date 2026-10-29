---
id: drustz-ea2850a02d5cd6a07a
section: mlsd
order: 186
level: A
title: >-
  20 · Exa 第二轮技术面：agentic search 的 retrieval / reranking / snippet / alignment ·
  5. 第三题 ⭐⭐：Model alignment —— 训一个 search agent
quick: >-
  作者文档章节 · 20 · Exa 第二轮技术面：agentic search 的 retrieval / reranking / snippet /
  alignment · 5. 第三题 ⭐⭐：Model alignment —— 训一个 search agent
companies: []
tags:
  - DrustZ
  - 作者文档章节
  - ML System Design · 全流程
realInterview: false
status: published
format: markdown
updatedAt: '2026-10-28'
sources:
  - title: DrustZ / Mingrui Zhang · pinned source
    url: >-
      https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/ml_sys_prep/20_case_exa_agentic_search.md
    type: primary
---
## 5. 第三题 ⭐⭐：Model alignment —— 训一个 search agent

> **题面可能长这样**："我们想训一个模型，更会用我们的搜索。怎么做？"
> 或反过来："搜索质量怎么影响 RL？"

**这题你有主场优势** —— 你在 Decagon 项目里手写过 Dr. GRPO（含 length/std normalization 的修正）和 DAPO 的 clip-higher，
而**他们博客里用的就是 Dr. GRPO**。见 §11.1。

### 5.1 阶段划分（照他们的方法论说）

```text
① SFT：轨迹格式 + 工具协议     ← 建立行为地板，不求最优
② RL（Dr. GRPO）：outcome reward ← 锐化决策边界（何时搜、搜什么、何时停）
③ （可选）on-policy distillation ← 抗遗忘 / 把多个 teacher 蒸成一个 student
```



### 5.2 reward 设计（这是最能出彩的地方）

| 层 | reward | 说明 |
|---|---|---|
| **outcome** | LLM grader 判最终答案对错 | ⚠️ 他们踩过的坑：**精确子串匹配会被 hack** —— 模型学会啰嗦地列一堆候选答案，总有一个命中。改用 grader |
| **cost** | 超上下文 **−0.25**；每次 search call 一个小负项 | 不加成本项，agent 会无限搜。你们量化过：好检索让 search call 少 62%，**这个收益必须进 reward 才能被学到** |
| **process**（我会加，他们没提） | 引用是否真的支撑了 claim | 只给 outcome reward，模型可以**猜对**或**靠记忆答对**而完全没用检索。这是 [06 §E4](?book=drustz-interview-2026&section=mlsd&question=drustz-354984fdc7bc9d31a9) 的老问题 |

**verifiable reward 的边界**（主动说这条，显示你不是无脑上 RL）：
> RL 只在 **verifier 可靠**时才该开。multi-hop QA 有唯一答案，verifier 干净，所以你们能训。
> 换成开放式研究任务（Websets 那种「找出所有满足 N 个条件的公司」），verifier 本身就是个难题，
> 这时我会先做 **rejection sampling + SFT**，而不是直接上 RL —— 因为 reward 噪声会被 RL 放大。

### 5.3 「搜索质量 → RL 样本效率」的因果链（背下来）

```text
检索质量↑
  → rollout 里「结果中直接含答案」的比例↑（你们：36.1% vs 32.6%）
  → 成功轨迹的密度↑
  → 有效梯度信号↑（GRPO 组内全错时优势全为 0，这一组白跑）  ← 这是机制的关键
  → 到同等性能所需 token↓（你们：−69%）、search call↓（−62%）
```



**⭐ 最值得说的一句（GRPO 特有，博客没写但是对的）**：
> GRPO 是**组内**normalization优势。如果一组 rollout **全部失败**，组内优势全是 0，这一组的算力完全浪费。
> 所以检索质量提升的收益在 GRPO 下是**超线性**的 —— 它不只是把平均 reward 抬高，
> 它是把「全组失败」的组从**零信号**变成**有信号**。这就是为什么少 20% token 就能到第 100 步。

（这段能讲出来，基本就证明你既读了他们的博客又真懂 GRPO。）

### 5.4 skill transfer 与评测污染

- 他们发现用 Exa 训的 agent 换到别的引擎也更强 → 说明学到的是**通用搜索技能**（怎么拆 query、何时停），不是"记住 Exa 的排序"。
  **验证方法**：交叉评测矩阵 —— {Exa训, SERP训} × {Exa测, SERP测}，四格都报。只报对角线会把 overfit 藏起来。
- **污染**：HotpotQA / 2Wiki 早就在预训练里了。所以他们用 **BrowseComp / FRAMES** 做 OOD，
  WebCode 更狠 —— **只用 2025-08-01 之后发布的库**。这是抗污染的正解，值得复述。

---

---

来源：[DrustZ / Mingrui Zhang · ml_sys_prep/20_case_exa_agentic_search.md](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/ml_sys_prep/20_case_exa_agentic_search.md)。作者整理资料；许可和第三方来源范围见阅读指南。
