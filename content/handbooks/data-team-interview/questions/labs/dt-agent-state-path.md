---
id: dt-agent-state-path
section: labs
order: 28
level: A
title: Agent 终局状态对了，中间少调一次只读工具，算不算过？
quick: "不算过。这类任务要教模型查证，跳过只读查询、凭记忆猜参数的轨迹，最终状态碰巧正确也应判失败。做法是在题卡里用 `must_call` 列出必须获取的证据，核对每个参数是否来自前一步工具返回，同时检查写入结果；用户侧用可靠脚本，模拟对白不直接当金标。"
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

不算过。判一条轨迹要同时看两件事：证据是怎么拿到的，最终状态对不对。少调一次必经的只读工具，说明模型在猜，这条轨迹应该从成功候选降为失败尝试。

## 为什么结果对了也不行

例如调用 `get_zipcode_by_city` 后，下一步天气查询中的 zip 必须能追溯到上一步的工具返回。如果模型没有查询，凭记忆猜「Berkeley 是 94710」，即使最后碰巧正确，也不能作为学习工具证据的正例。直接用知识回答有时更快，但这类训练任务的目的就是学会查证；把这种轨迹当正例，换成冷门城市时模型就会继续猜。

BFCL V3 的公开要求也是这样：既做状态核验，也做响应核验。该查的信息需要实际查到，参数应来自工具返回，模型的世界知识不算数。

## 怎么判

1. 在题卡里用 `must_call` 列出必须调用的只读工具。缺少必经调用，这条轨迹就判失败。`must_call` 只要求获取必要证据，不固定探索顺序；两条路径都能合法获取 zip，就都可以通过。
2. 逐步检查参数来源：每个参数要能追溯到前面的工具返回，只看整段结果会放过中间猜对的那一步。标注员也不能修改工具返回来凑正确答案。
3. 写操作还要确认目标事件真的落进了数据库。

## 实践中的变化

读邮件、查日历这类工具同样有只读查询。摘要看起来正确，但模型没有读取对应邮件，就不能标成成功轨迹。

用户侧也要小心。Tau-bench 用 LLM 模拟用户；BFCL 也指出，模拟用户可能产生幻觉或不按指令行动，所以模拟对白不能直接当金标。用户侧用研究集或人工脚本，环境侧用可重置的数据库。

## 追问

- **冗余调用算失败吗？** 不算。BFCL 允许多余动作，这里重点检查有没有跳过必经的只读查询。重复的写操作则要另外检查幂等性。
- **`must_call` 会把策略固定死吗？** 不会。它不规定探索顺序，只检查必要证据有没有拿到。

相关：`dt-traj-quality`、`dt-grounding-data`、`dt-tool-turn-pref`。
