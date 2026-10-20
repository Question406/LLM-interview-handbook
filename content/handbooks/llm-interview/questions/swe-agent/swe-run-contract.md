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
updatedAt: 2026-08-21
sources:
  - title: SWE-bench Multimodal
    url: https://arxiv.org/abs/2505.23419
    type: primary
---

没有 run contract，resolve rate 不可比。两个人「都跑了同一 issue」，可能用了不同 base commit、不同依赖、不同超时、不同是否允许联网。面试官要听的是输入输出约定：固定什么、产出什么、缺少哪些信息时无法可靠比较成绩。先定义这份约定，再选择模型：数字对不上时，先查环境漂移，再查模型。

## 输入必须明确固定下来

一份 attempt 的输入至少包括：issue 文本与附件 hash、repo base SHA、评测 test commit、容器 / 依赖 lock digest、网络与权限策略、模型 snapshot、系统提示的 hash、工具字段和类型规范（schema）的版本、sampling 参数与 seed、时间 / 调用次数 / token / 费用预算。持续 benchmark 还要声明 freshness cutoff 与任务版本号。仓库更新、依赖漂移或模型已见过该 issue，都会让数字失去对照。缺 seed 或镜像 digest，就不要声称可复现。把这些字段写成一份 YAML，和 artifact 一起存；口头「我们用的官方镜像」不够。评测命令本身也要版本化，避免 evaluator 静默升级。

## 输出不能只有 patch

输出应能让第二个人在相同环境 replay，并判断失败来自模型、工具、依赖还是评测器。最低集合：统一 diff、逐步 trace（每次 tool 的请求 / 响应）、测试日志、机器可读 verdict（`resolved` / `failed` / `timeout` / `policy_denied` / `env_error`）、退出原因、资源消耗。verdict 必须由冻结的 evaluator 产生，而不是模型自称「已修复」。artifact 与 trace 要版本化存放，并和任务 ID、attempt ID 绑定。没有 trace 的成功不可审计：无法证明没改测试、没检索 gold PR。预算耗尽要单独计，不要并进「模型不会修」。

## 评测上能刷的缺口

常见缺口：不冻依赖导致「环境碰巧能编过」；允许评测时上网把 gold PR 检索回来；预算不封顶，用无限 retry 堆成功率；只交最终 patch、不交 trace；把环境崩溃算模型失败或反过来全甩给环境。报告应同时给出成功定义、预算耗尽率、不可复现率和多次重跑方差。合同的价值是：别人按同一 YAML 能重跑出同一 verdict，误差来自模型随机性而不是环境漂移。最小可发表物是任务版本 + 镜像 digest + 模型 snapshot + patch + evaluator verdict + 完整 trace。把这份清单当成实验的 schema：缺字段的运行结果不得进入对比表。现场被问「为什么你们分数和官方不一致」时，先核对运行约定中的字段，再谈模型。

把 run contract 存成与 patch 同目录的机器可读文件，CI 拒绝缺 digest / 缺 verdict / 缺 trace 的提交。对比实验只能在合同字段完全一致时进行。口头对齐环境和可复现不是一回事。

## 追问

- **seed 能保证 LLM 可复现吗？** 不能完全。必须冻模型版本与 decoding，并多次重跑报方差；seed 只是必要项。
- **live 仓库能进同一数字吗？** 不能。frozen 与 live 分列，见 `swe-contamination-resistance`。
- **timeout 算失败还是无效？** 算预算内失败，单独列；不要和 oracle fail 混成一个 error rate。
- **prompt 改了要不要换任务版本？** 要。prompt / tool schema 是输入合同的一部分，静默修改会使历史分数不可比。
