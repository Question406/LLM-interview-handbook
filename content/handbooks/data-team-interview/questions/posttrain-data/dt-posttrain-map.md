---
id: dt-posttrain-map
section: posttrain-data
order: 1
level: S
title: post-training 数据：数学、代码、工具、agent，各自的 acceptance criteria 是什么？
quick: >-
  post-training 的数据单位是题目、trajectories 和 grader，各类任务的 acceptance criteria 就是
  grader 如何判断正确性：数学看标准答案、解释器或 Lean，代码看冻结的测试，工具看 schema 和环境状态，agent 还要看
  trajectories 能否 replay、多跑几次是否稳定。四类检查各管一个域，要分开建；post-training
  要准备的是题目、trajectories 和 grader，多加网页解决不了。
companies:
  - apple
tags:
  - Apple
  - Post-training
  - 备考地图
  - 口述改写 2026-10-28
realInterview: false
status: published
format: markdown
updatedAt: '2026-10-28'
sources:
  - title: Apple Intelligence Foundation Language Models Tech Report 2025
    url: >-
      https://machinelearning.apple.com/research/apple-foundation-models-tech-report-2025
    type: primary
  - title: DeepSeek-R1
    url: 'https://arxiv.org/abs/2501.12948'
    type: primary
  - title: The Llama 3 Herd of Models
    url: 'https://arxiv.org/abs/2407.21783'
    type: primary
---

## 可以这样回答

按 grader 分，是因为能验证的数据要先验证再用。比如一道数学题，teacher 给的解答再漂亮，gold labels 对不上就不进 training set；一条 tool-use trajectories，JSON 再规整，环境状态不对也一样。AFM 2025 报告也写了，SFT 和 RLHF 都用 synthetic data，能验证的先验证。

## 技术备查

这张卡当目录用：先按 grader 把 post-training 数据分成几个域，再顺着下表找每个域的卡。post-training 数据的单位是 `(prompt, 轨迹, grader)`，各域的「门」就是 grader 怎么判断一条 trajectories 算正确：数学看 gold labels、解释器或 Lean，代码看冻结的测试，工具看 schema 和环境状态，agent 还要看 trajectories 能不能 replay、多跑几次是否稳定。这四类检查各管一个域，要分开建。

按 grader 分，是因为能验证的数据要先验证再用。比如一道数学题，teacher 给的解答再漂亮，gold labels 对不上就不进 training set；一条 tool-use trajectories，JSON 再规整，环境状态不对也一样。AFM 2025 报告也写了，SFT 和 RLHF 都用 synthetic data，能验证的先验证。

面试时先说清是哪个 domain 和 acceptance criteria 是什么，再按具体任务展开。下表列出每个域的 positive-example criteria，以及本章和已有卡片的对应关系。

## 四条线和已有卡

| 域 | positive-example criteria | 这章 | 已经有的 |
| --- | --- | --- | --- |
| 数学 | gold labels / 解释器 / Lean | `dt-math-passk-band`、`dt-math-tir-data`、`dt-math-lean-prover`、`dt-math-rewrite-leak` | `dt-synth-reasoning`、`dt-rlvr-data`、`dt-prm-steps`、`dt-math-verifier-code`、`dt-s1k` |
| 代码 | 冻结测试；改测试的 trajectories 隔离 | `dt-code-oss-instruct`、`dt-code-hidden-tests`、`dt-code-repo-vs-fn` | `dt-code-exec-synth`、`dt-code-bench-bleed`、`dt-swe-success-noise`、`dt-rlef-split` |
| tool calls | 字段和类型规范（schema） 合法 + 环境状态 | `dt-tool-apigen`、`dt-tool-parallel`、`dt-tool-error-recover`、`dt-tool-write-confirm` | `dt-synth-tool-mm`、`dt-traj-quality`、`dt-tool-irrelevance`、`dt-tool-alias`、`dt-tool-inject`、`dt-tool-turn-pref` |
| Agent | 跨次 $\mathrm{pass}^{k}$、可 replay；RL 看环境 | SFT：`dt-agent-fireact`、`dt-agent-swegym`、`dt-agent-user-sim`。RL：`dt-agent-rl-map` 到 `dt-tinker-agent-rl` | `dt-tau-passk`、`dt-webarena-traj`、`dt-gui-traj`、`dt-agent-state-path`、`dt-when-to-search` |
| 配在一起 | 分组统计、分 mask | `dt-posttrain-mix` | `dt-packed-sft-code`、`dt-neg-transfer` |

## 追问

**没有 grader 的开放生成怎么办？**
不在这一章的范围里，走 preference data 和人工标注。

**这一章和 Panel 的合成题是什么关系？**
Panel 的合成题讲整体流程，这一章按域分别讲各类数据怎么做。

**和 mid-training 的数学 / 代码数据怎么分？**
mid-training 用书、仓库和网页题补知识覆盖；post-training 教模型怎么解题、怎么调用工具、什么时候停。阶段见 `dt-pre-mid-post`。

**用户工具日志能当 trajectories 吗？**
默认不用。trajectories 来自环境里的 synthetic data 加许可的研究集，用户数据的授权和隐私问题见 `dt-privacy-feedback`。
