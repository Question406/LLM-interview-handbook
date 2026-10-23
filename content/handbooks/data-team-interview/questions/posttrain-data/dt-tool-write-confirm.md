---
id: dt-tool-write-confirm
section: posttrain-data
order: 12
level: A
title: 会改状态的工具，数据里要不要先确认再写？
quick: "要，但按副作用分。工具目录标记 read / write，读取按任务自动执行；含糊的写操作先澄清、确认，已有明确且唯一的授权可以按协议直接执行。训练要覆盖用户拒绝后停止；评分同时检查确认轮和实际状态，只看写入结果会漏掉未经确认的误操作。"
companies:
  - apple
tags:
  - Apple
  - Tool Use
  - Safety
  - Agent
realInterview: false
status: published
format: markdown
updatedAt: 2026-10-12
sources:
  - title: Apple Intelligence Foundation Language Models Tech Report 2025
    url: https://machinelearning.apple.com/research/apple-foundation-models-tech-report-2025
    type: primary
  - title: "τ-bench: A Benchmark for Tool-Agent-User Interaction"
    url: https://arxiv.org/abs/2406.12045
    type: primary
  - title: Datasets used for Apple Intelligence
    url: https://www.apple.com/legal/ai-regulations/training-data/
    type: primary
---

要，但只针对会改状态的写操作。读取可以按任务自动调用；删除邮件、转账、修改日历这类写操作，要根据用户是否给了明确授权和产品策略，决定是否先复述、确认。示范还要覆盖用户拒绝后不执行。

用两句话就能看出差别。用户说「把今天下午三点的会删掉」，而且符合条件的只有一场，这是明确的祈使，可以直接删。用户说「清掉一些会」，删哪些都说不准，必须先问。如果数据里总是直接执行 `cancel_order`，模型就学不到这两种情况的区别。

只检查最终状态也不够，会漏掉没确认就写、结果碰巧对的误操作。这和 `dt-agent-state-path` 讲的「终局对就算过」是同一类问题，方向相反：那边担心漏掉只读步骤，这边担心多写。τ-bench 的零售和航空域里，写库就是核心操作，政策常常要求先确认。

## 数据怎么造

工具目录给每个工具带上副作用标记，`read` 或 `write`。标注协议规定，write 之前必须有一轮用户看得到的确认，除非用户已经给出上面那种明确且唯一的指令。

正例是确认轮 + 写入 + 状态正确。没确认就写的轨迹是负例，即使最终状态碰巧对。

写操作的示范放在可回滚的环境里造。判分时把 write 工具的确认做成硬性的策略 grader，没看到确认轮就给零分，这比人事后看 diff 便宜。

## 追问

**让 LLM judge 判断有没有确认行吗？**
不要。它会给出「好像确认过了」这种结论，确认轮要由环境里的策略 grader 硬性检查。

**和安全拒答放一张卡吗？**
不放。安全拒答处理的是不该做的请求，确认处理的是该做但要用户点头的请求，两者配比分开，见 `dt-safety-refuse`。

**只读工具也要确认吗？**
不要。否则 agent 会事事请示，τ-bench 的政策下也会让用户烦。在 schema 里把读写类型标清楚即可。

**用户拒绝之后模型该说什么？**
承认已取消，写入不发生。训练里要有这类停止轨迹，避免模型把拒绝当成「换个办法继续执行」。

相关：`dt-agent-state-path`、`dt-safety-refuse`
