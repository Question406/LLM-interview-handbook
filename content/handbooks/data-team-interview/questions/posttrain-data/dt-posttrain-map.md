---
id: dt-posttrain-map
section: posttrain-data
order: 1
level: S
title: 后训练数据：数学、代码、工具、agent，各自的门是什么？
quick: "先说明每类任务如何验证：数学用标准答案、解释器或 Lean；代码用固定测试；工具用 schema 和环境状态；agent 还要看轨迹是否可回放、多次运行是否稳定。后训练的数据单位是题目、轨迹和 grader，不只是新增网页。"
companies:
  - apple
tags:
  - Apple
  - Post-training
  - 备考地图
realInterview: false
status: published
format: markdown
updatedAt: 2026-10-12
sources:
  - title: Apple Intelligence Foundation Language Models Tech Report 2025
    url: https://machinelearning.apple.com/research/apple-foundation-models-tech-report-2025
    type: primary
  - title: DeepSeek-R1
    url: https://arxiv.org/abs/2501.12948
    type: primary
  - title: The Llama 3 Herd of Models
    url: https://arxiv.org/abs/2407.21783
    type: primary
---

回答后训练数据问题，先说明数据单位是 `(prompt, 轨迹, grader)`，以及怎样判断轨迹正确。数学、代码、工具和 agent 的检查不同，不能混用。Panel 的合成题讲整体流程，这一章分别解释各类数据的做法；面试时再按具体任务展开。

AFM 写了 监督微调（SFT） 和 基于人类反馈的强化学习（RLHF） 都用合成，能验证的先验证。用户日志默认不进基础模型。没有 grader 的开放生成，走偏好和人标，不要硬套这一章。

## 四条线和已有卡

| 域 | 正例门 | 这章 | 已经有的 |
| --- | --- | --- | --- |
| 数学 | 金标 / 解释器 / Lean | `dt-math-passk-band`、`dt-math-tir-data`、`dt-math-lean-prover`、`dt-math-rewrite-leak` | `dt-synth-reasoning`、`dt-rlvr-data`、`dt-prm-steps`、`dt-math-verifier-code`、`dt-s1k` |
| 代码 | 冻结测试；改测试的轨迹隔离 | `dt-code-oss-instruct`、`dt-code-hidden-tests`、`dt-code-repo-vs-fn` | `dt-code-exec-synth`、`dt-code-bench-bleed`、`dt-swe-success-noise`、`dt-rlef-split` |
| 工具调用 | 字段和类型规范（schema） 合法 + 环境状态 | `dt-tool-apigen`、`dt-tool-parallel`、`dt-tool-error-recover`、`dt-tool-write-confirm` | `dt-synth-tool-mm`、`dt-traj-quality`、`dt-tool-irrelevance`、`dt-tool-alias`、`dt-tool-inject`、`dt-tool-turn-pref` |
| Agent | 跨次 $\mathrm{pass}^{k}$、可回放；强化学习（RL） 看环境 | SFT：`dt-agent-fireact`、`dt-agent-swegym`、`dt-agent-user-sim`。RL：`dt-agent-rl-map` 到 `dt-tinker-agent-rl` | `dt-tau-passk`、`dt-webarena-traj`、`dt-gui-traj`、`dt-agent-state-path`、`dt-when-to-search` |
| 配在一起 | 分组统计、分 mask | `dt-posttrain-mix` | `dt-packed-sft-code`、`dt-neg-transfer` |

## 追问

- **和 mid-training 数学 / 代码怎么分？** mid 用书、仓库和网页题补充知识覆盖；后训练教模型如何解题、调用工具，以及何时停止。阶段见 `dt-pre-mid-post`。
- **用户工具日志能当轨迹吗？** 苹果默认不能进基础模型。环境里合成 + 许可研究集，见 `dt-privacy-feedback`。
