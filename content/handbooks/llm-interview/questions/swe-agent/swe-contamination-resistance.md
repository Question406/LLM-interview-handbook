---
id: swe-contamination-resistance
section: swe-agent
order: 3
level: A
title: 为什么静态 SWE 集很容易发生训练污染，如何构建并报告一个 contamination-resistant 的持续 benchmark？
quick: GitHub issue、PR 和测试通常公开，模型可能记住答案。采用时间截断、近期/未见仓库、冻结提交与隐藏测试，明确训练 cutoff；把 frozen leaderboard 与持续 live eval 分开报告。
tags:
  - SWE Agent
  - Contamination
  - Benchmark
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-21
sources:
  - title: SWE-bench Multimodal
    url: https://arxiv.org/abs/2505.23419
    type: primary
---

面试里说「我们跑了 SWE-bench」不等于有评测能力。GitHub issue、最终 PR、CI 测试、甚至讨论里的正确改法，都可能已经进过预训练或 SFT。模型吐出和 gold patch 很像的 diff，可能是在背答案，而不是在仓库里诊断。污染抵抗首先是合同问题：你冻了什么、cutoff 怎么声明、live 和 frozen 怎么分报。不要用「公开集很高」暗示线上修 bug 能力。

## 污染通道

公开任务至少有四条泄漏路径：issue 原文与标题；gold PR 的文件级 diff；`FAIL_TO_PASS` 测试名和断言；第三方 blog、复现教程、合成蒸馏把同一批任务反复写入。Agent harness 若把测试文件、隐藏断言或「应改哪些文件」塞进 prompt，等于当场开卷。时间截断只挡「cutoff 之后创建的 issue」，挡不住 cutoff 前已公开、后来才被收进 bench 的仓库。检索增强同样危险：评测时允许上网，模型可以把 gold PR 搜回来再「生成」。污染是训练、评测、harness 三侧的事，不是只洗语料。

每次 attempt 至少记录：task 版本、issue 创建时间、base SHA、test commit、harness digest、模型 cutoff、是否联网、生成 patch 与 gold 的检索相似度。没有这些字段，污染审计无法事后补。

## 合同要冻什么

每个任务版本钉死并写入报告：issue `created_at`、repo base SHA、评测用 test commit、容器与依赖 digest、harness 与 oracle 版本。模型侧声明训练 cutoff，并记录评测当日是否允许网络检索、是否允许读测试目录。持续 live 集只收 cutoff 之后、未见组织或未见仓库的 issue；hidden test 不进公开镜像，失败 case 不得回流 SFT。审计用字符串、AST、embedding、patch hunk 检索：命中标高风险，未命中不能证明干净。去重粒度至少到 hunk 与测试名，文件级 hash 会漏 fork 和 cherry-pick。Live 采集管道要与训练数据管道物理隔离，否则「持续评测」会在几周内变成第二套训练集。

## 怎么报告、哪里会被刷

必须拆开三列，禁止加总成一个 headline：frozen leaderboard resolve rate、cutoff 之后 live rate、污染审计命中率（patch 近重复 / 测试名命中）。Live 更低通常更接近真实泛化，不要解释成模型退化，也不要用「我们后来又训了 live」把两列重新对齐。评测上能刷的是：只报公开集；把 live 任务事后并进训练；评测开检索找 gold PR；harness 泄漏测试；用同一 issue 的镜像仓库充新题。面试官要听的是：你有 frozen 与 live 两套数字，审计方法写在报告里，并且失败日志有隔离通道。持续 bench 的价值是趋势，单次百分点没有意义。发布清单至少附：任务版本、cutoff、是否允许检索、审计方法、frozen / live 两列。缺任何一项，数字只能当内部调试，不能当对外能力声明。

## 追问

- **去重到什么粒度？** 文件级 hash 不够；要看 patch hunk 与测试名。同一 issue 换仓库 fork 仍算污染。
- **私有 hidden eval 就安全？** 人员、日志、失败 case 回流训练都会二次污染，需要独立 ACL 与禁止训练使用条款。
- **和语料泄漏检测怎么分？** 那题偏 n-gram / 检索重合；本题偏 SWE 任务合同：冻结提交、时间窗、分报和 harness 是否开卷。
