---
id: swe-run-contract
section: swe-agent
order: 1
level: S
title: 怎样定义一个可复现的 issue-to-patch run contract？
quick: 固定 repo base commit、依赖/镜像 digest、issue、模型与 sampling、工具版本、时间/费用预算、评测命令；产出 patch、完整 trace 和机器可读 verdict。缺任一项，结果都难以复现或比较。
tags:
  - SWE Agent
  - Reproducibility
  - Evaluation
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-17
sources:
  - title: SWE-bench Multimodal
    url: https://arxiv.org/abs/2505.23419
    type: primary
---

run contract 是 Agent 实验的输入输出协议。输入包含 issue 文本与附件、repo base SHA、patch/test 版本、容器/依赖 digest、模型 snapshot、system prompt、tool schema、sampling seed、时间/调用/token 预算与网络/权限策略。

输出不能只有一个 patch：还应有逐步 trace、所有命令和结果、文件 diff、测试日志、退出原因、资源消耗和 evaluator verdict。这样另一个人能在相同环境 replay，也能定位问题来自模型、工具、依赖还是评测。

持续 benchmark 还要声明 freshness cutoff 与任务版本。否则仓库更新、依赖漂移或模型已见过 issue，都会让 resolve rate 失去可比性。
