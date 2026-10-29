---
id: p3a-openai-crossword-puzzle-solver
section: openai
order: 640
level: A
title: "OpenAI：分布式填字求解：约束传播与搜索切分"
quick: "先按词长和交叉字母缩小候选，选候选最少的槽位搜索并传播约束，前沿足够大才拆到 worker。比如一个槽只剩三个词，就按三个分支分工；返回前独立验解，超时只表示未找到，不能说无解。"
companies:
  - openai
tags:
  - 场景参考答案
  - 1Point3Acres
  - Frontier-2026-10
  - Design
  - OpenAI
realInterview: true
status: published
format: markdown
updatedAt: 2026-10-18
sources:
  - title: "1Point3Acres · OpenAI · crossword-puzzle-solver"
    url: https://www.1point3acres.com/interview/problems/company/openai/crossword-puzzle-solver
    type: secondary
---

我会先用约束传播缩小候选，再把足够大的搜索前沿分给多台机器。比如某个 5 字母横槽只剩 3 个候选，就按这 3 个词拆分支；worker 各自继续搜索，协调者独立验解后提交第一个合法结果，并取消其他分支。

题目按 50×50 棋盘、大约 100 个槽位、百万词词典设计，返回任意合法解，允许无解，也要支持限时和取消。开始时先确认同一个词能不能重复使用。词典按「词长 + 某位置的字母」建索引，给每个槽位求候选；每次选候选最少的槽位做 DFS，填入一个词后把交叉字母约束传给相邻槽，候选变空就回溯。

协调者创建 `search_job`，字段为 `search_job(board, dictionary_version, budget)`，先本地传播约束，前沿足够大再切分为 `branch(assignments, remaining_candidates, seed, state)`。分支 id 确定且可重放，保存的前沿状态要足够让别的机器恢复。如果前沿很小，传输搜索状态可能比本地求解更慢。

worker 失联时重跑同一分支，结果按 branch id 去重；完整赋值上报后，协调者再核验全部交叉约束，提交 winner。取消信号带 job epoch，旧任务即使还在运行也不能继续发布结果。分布式能加速搜索，最坏情况仍是指数复杂度。评测看节点展开数、约束收缩率、worker 空闲比例、状态传输字节数和首解时延，先确认剪枝有效，再扩机器。

## 追问

**一定能在限时内解出来吗？**
不能保证。无解要穷尽搜索空间才能确认，预算耗尽只能返回「超时未找到」。

**为什么选候选最少的槽位？**
它的分支因子小，矛盾也暴露得早，能更早回溯并剪掉无效子树。

> 来源：一亩三分地 OpenAI 题卡摘要（2026-10-18 用 Chrome 读取），是网站对候选人报告的二手整理。规模数字、SLO 和故障情景是手册补的练习约定。
