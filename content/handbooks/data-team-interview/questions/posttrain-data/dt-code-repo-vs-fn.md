---
id: dt-code-repo-vs-fn
section: posttrain-data
order: 8
level: A
title: 函数级 HumanEval 数据，和仓库级 SWE 数据，后训练怎么分桶？
quick: "函数级和仓库级数据要单独分组。前者通常是短 prompt、单文件和单测；后者包含 issue、多文件定位、执行环境和回归测试。仓库任务需要保留检索与失败恢复过程，不能只训练最终补丁。SWE-Gym 提供可执行环境，成功轨迹仍要检查质量，见 `dt-swe-success-noise`。"
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
updatedAt: 2026-10-12
sources:
  - title: SWE-bench
    url: https://arxiv.org/abs/2310.06770
    type: primary
  - title: SWE-Gym
    url: https://arxiv.org/abs/2412.21139
    type: primary
  - title: The Llama 3 Herd of Models
    url: https://arxiv.org/abs/2407.21783
    type: primary
  - title: Apple Intelligence Foundation Language Models Tech Report 2025
    url: https://machinelearning.apple.com/research/apple-foundation-models-tech-report-2025
    type: primary
---

函数级和仓库级任务应分组配比并分别评测。两者混在一个 SFT 桶里，模型容易把独立写函数的做法用到需要定位、多文件修改和回归测试的仓库任务上。

不这么选的理由：后训练若只有「给定签名写函数」，产品里的编码 agent 会不会定位文件。把仓库轨迹压成 patch completion，是在教抄补丁，不是教定位。SWE-bench 把评测定在仓库。SWE-Gym 把 2438 个可执行 Python 任务拿来训 agent。成功轨迹仍可能脏，见 `dt-swe-success-noise`。

苹果：许可仓库或合成环境。用户日志不进基础模型。端侧补全走函数级桶，云上 agent 走仓库级配额。

## 两条配方

函数级：OSS-Instruct + 冻结单测。序列短，mask 简单。门禁用 LiveCodeBench 时间切，见 `dt-code-oss-instruct`。

仓库级：环境快照、issue 正文、允许的工具（读文件、改文件、跑测）。轨迹是多跳。正例看隐藏回归测，不是看 diff 像不像人。改测试文件、删断言的成功，扔掉，见 `dt-swe-success-noise`。

不要把仓库轨迹压成「把 patch 当 completion」。过程里的检索和失败恢复要留，见 `dt-tool-error-recover`。

## 配额

产品若是端侧补全，函数级权重大。若是云上 agent，仓库级和工具轨迹要单独配额，否则短函数题在条数上淹没，见 `dt-length-bucket-code`。负迁移：狂训 SWE 可能伤短补全，锚点两边都报。

## 追问

- **合成 issue 行不行？** 可以当种子，grader 仍是原仓库测试。用 LLM 写一个假测试当过关，是函数级泄漏的仓库版。
- **多语言仓库？** 环境按语言分。Java 轨迹不要和 Python 单测门混用。
- **SWE-bench test 能训吗？** 不能。Gym 的训练任务和 Verified 门禁要切开，和数学改写同一纪律。
