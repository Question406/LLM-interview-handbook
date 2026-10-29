---
id: dt-code-repo-vs-fn
section: posttrain-data
order: 8
level: A
title: 函数级 HumanEval 数据，和仓库级 SWE 数据，post-training 怎么分桶？
quick: >-
  分成两个桶，分别 data mix、分别评测。函数级是短 prompt、单文件、单测；仓库级要读 issue、定位多个文件、在执行环境里跑
  regression tests，混在一起训，模型会把写独立函数的做法搬到仓库任务上。仓库 trajectories
  要保留检索和失败恢复的过程，只训最终补丁，模型学不会定位；SWE-Gym 这类可执行环境里的成功 trajectories 也要再筛，见
  `dt-swe-success-noise`。
companies:
  - apple
tags:
  - Apple
  - Coding
  - Agent
  - SWE
realInterview: false
status: published
format: markdown
updatedAt: 2026-10-12T00:00:00.000Z
sources:
  - title: SWE-bench
    url: 'https://arxiv.org/abs/2310.06770'
    type: primary
  - title: SWE-Gym
    url: 'https://arxiv.org/abs/2412.21139'
    type: primary
  - title: The Llama 3 Herd of Models
    url: 'https://arxiv.org/abs/2407.21783'
    type: primary
  - title: Apple Intelligence Foundation Language Models Tech Report 2025
    url: >-
      https://machinelearning.apple.com/research/apple-foundation-models-tech-report-2025
    type: primary
---

函数级和仓库级数据分成两个桶，分别 data mix、分别评测。混在一个 SFT 桶里，模型容易把「给定签名写函数」的做法用到要定位文件、多文件修改和跑 regression tests 的仓库任务上。

举个例子，一个 issue 说某个配置项不生效。模型要先读 issue，找到读这个配置的是哪几个文件，改完跑测试，失败了再调整。post-training 如果只有「给定签名写函数」，编码 agent 就学不会定位文件。公开基准也是这么划分的，SWE-bench 的评测单位就是仓库，SWE-Gym 用 2438 个可执行的 Python 任务来训 agent。

函数级桶简单一些：用 OSS-Instruct 生成题目，配冻结的单测，序列短，loss mask 也简单。上线前用 LiveCodeBench 按时间切分做 evaluation gate，避免见过的题混进评测（见 `dt-code-oss-instruct`）。

仓库级桶的环境来自许可仓库或合成环境，要准备环境快照、issue 正文，以及允许的工具：读文件、改文件、跑测试。trajectories 是多跳的，检索和失败后恢复的步骤都要保留（见 `dt-tool-error-recover`）。一条 trajectories 算不算正例，看它能不能通过隐藏的 regression tests，diff 像不像人写的不算数。通过了也要查是不是靠改测试文件、删 assertion 过的，这类「成功」直接扔掉（见 `dt-swe-success-noise`）。

配额跟着目标能力走。主要目标是短补全，函数级权重就大；要做仓库级 agent，仓库级和 tool-use trajectories 要单独给配额，否则短函数题在条数上会把它们淹没（见 `dt-length-bucket-code`）。另一个方向也有 negative transfer，狂训 SWE 可能伤到短补全，所以两边的评测都要报。

## 追问

**仓库 trajectories 只留最终 patch 行不行？**
不行。把仓库 trajectories 压成「把 patch 当 completion」来训，模型学到的是抄补丁，学不会定位。

**合成 issue 行不行？**
可以当 seed，但 grader 还是要用原仓库的测试。让 LLM 顺手写一个假测试当过关标准，就是函数级 leakage 在仓库级的翻版。

**multilingual 仓库怎么办？**
环境按语言分开。Java 的 trajectories 不要和 Python 的单测 evaluation gate 混用。

**SWE-bench 的 test 能拿来训吗？**
不能。SWE-Gym 的训练任务和 Verified evaluation gate 要切开，这和数学题改写防 leakage 是同一条纪律。
