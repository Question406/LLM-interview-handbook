---
id: dt-agent-state-path
section: labs
order: 28
level: A
title: Agent 终局状态对了，中间少调一次只读工具，算不算过？
quick: "不算过。少调一次必经的只读查询，说明参数是猜的，最终状态碰巧对了也该判失败。做法是在题卡里用 `must_call` 列出必须拿到的证据，逐个核对参数是否来自前一步的工具返回，再确认写入落了库；模拟用户的对白不直接当金标。"
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

不算过。这类任务本来就是要教模型去查证，少调一次必经的只读工具，说明它在猜，这条轨迹应该从成功候选降成失败尝试。所以判一条轨迹要同时看两件事：证据是怎么拿到的，最终状态对不对。

举个例子。模型应该先调 `get_zipcode_by_city`，再拿返回的 zip 去查天气。它跳过了查询，凭记忆写了「Berkeley 是 94710」，最后天气也查对了。这条要是当正例，模型学到的就是「记得住就别查」，换一个冷门城市它还会接着猜。直接用知识回答有时更快，但这类训练任务的目的就是学会查证。BFCL V3 公开的要求也是这样，状态核验和响应核验都要做：该查的信息要实际查到，参数要来自工具返回，模型自己的世界知识不算数。

具体判的时候，我先在题卡里用 `must_call` 列出必须调用的只读工具，缺了就判失败。`must_call` 只管必要的证据有没有拿到，不规定探索顺序，两条路径都能合法拿到 zip，就都算过。

然后逐步看参数来源，每个参数都要能追溯到前面某次工具返回。只看整段结果，会放过中间猜对的那一步。标注员也不能为了凑出正确答案去改工具返回。最后是写操作，要确认目标事件真的落进了数据库。

## 追问

**多调了几次没必要的工具，算失败吗？**
不算。BFCL 允许多余动作，这里查的是有没有跳过必经的只读查询。重复的写操作另说，要单独检查幂等性。

**`must_call` 会不会把策略固定死？**
不会。它不规定探索顺序，只检查必要的证据有没有拿到。

**读邮件、查日历这类任务也这么判吗？**
一样。摘要看着没问题，可模型根本没读对应的那封邮件，就不能标成成功轨迹。

**用户那一侧能用 LLM 来模拟吗？**
可以拿来跑环境，模拟出来的对白不直接当金标。Tau-bench 用 LLM 模拟用户，BFCL 也指出模拟用户可能产生幻觉、不按指令行动。所以用户侧用研究集或人工脚本，环境侧用可重置的数据库。

相关：`dt-traj-quality`、`dt-grounding-data`、`dt-tool-turn-pref`
