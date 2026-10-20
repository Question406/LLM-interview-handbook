---
id: dt-agent-state-path
section: labs
order: 28
level: A
title: Agent 终局状态对了，中间少调一次只读工具，算不算过？
quick: "最终状态碰巧正确，不代表整段轨迹可作正例。题卡用 `must_call` 指定必须获取的证据，核对参数是否来自前一步工具返回。跳过只读查询、靠记忆猜参数的轨迹应判失败；同时检查写入结果，用户模拟也要使用可靠脚本或研究集。"
companies:
  - apple
tags:
  - BFCL
  - Agent
  - Tool Use
  - Apple
realInterview: false
status: published
format: markdown
updatedAt: 2026-10-12
sources:
  - title: "BFCL V3: Multi-Turn Function Calling"
    url: https://gorilla.cs.berkeley.edu/blogs/13_bfcl_v3_multi_turn.html
    type: primary
  - title: The Llama 3 Herd of Models
    url: https://arxiv.org/abs/2407.21783
    type: primary
  - title: Apple Intelligence Foundation Language Models Tech Report 2025
    url: https://machinelearning.apple.com/research/apple-foundation-models-tech-report-2025
    type: primary
---

轨迹是否正确，需要同时检查证据获取过程和最终状态。题卡可以用 `must_call` 列出必须调用的只读工具；缺少必经调用，就把这条成功候选降为失败尝试。写操作还要确认目标事件是否真的在数据库里，见 `dt-traj-quality`。

例如调用 `get_zipcode_by_city` 后，下一步天气查询中的 zip 必须能追溯到上一步工具返回。若模型没有查询，而是凭记忆猜「Berkeley 是 94710」，即使最后碰巧正确，也不能作为学习工具证据的正例，见 `dt-grounding-data`。标注要按每一步检查，不只看整段结果，见 `dt-tool-turn-pref`；标注员也不能修改工具返回来凑正确答案。

`must_call` 只要求获取必要证据，不固定探索顺序。两条路径都能合法获取 zip，就都可以通过。产品中直接用知识回答有时更快，但这类训练任务的目的就是学会查证，换成冷门城市时才能避免猜测。

## 在苹果工具任务中的对应问题

邮件和日历工具也有只读查询。摘要看起来正确，但模型没有读取对应邮件，就不能标成成功轨迹。Tau-bench 使用 LLM 模拟用户；BFCL 也指出，模拟用户可能产生幻觉或不按指令行动，所以不能直接把模拟对白当作金标。用户侧使用研究集或人工脚本，环境侧用可重置数据库，用户原话默认不进入全球 FM。

BFCL V3 的公开要求包括状态核验和响应核验：该查的信息需要实际查到，参数应来自工具返回，而非模型的世界知识。

## 追问

- 冗余调用算失败吗？BFCL 允许多余动作。这里重点检查有没有跳过必经的只读查询；重复写操作还要检查幂等性。
- 用预训练知识答对邮编呢？产品上可能更快，但训练证据获取能力时仍要按任务要求调用工具。
- `must_call` 会固定策略吗？不会固定探索顺序，只检查必要证据是否获取。
