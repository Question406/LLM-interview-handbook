---
id: dt-tau-passk
section: labs
order: 35
level: A
title: τ-bench：过一次库状态，为什么还不够当正例？
quick: "因为一次通过可能是运气。τ-bench 看同题多次运行是否都遵守政策、正确更新数据库：gpt-4o 零售 $\\mathrm{pass}^{1}$ 约 61%，到 $\\mathrm{pass}^{8}$ 只剩约 25%。用 $\\mathrm{pass}^{k}$ 当进 SFT 和发版的门禁，训练仍可用单次状态奖励；轨迹还要查必经只读调用，用户模拟和 grader 标签需独立复核。"
companies:
  - apple
tags:
  - Sierra
  - Agent
  - Tool Use
  - Apple
realInterview: false
status: published
format: markdown
updatedAt: 2026-10-12
sources:
  - title: "τ-bench: A Benchmark for Tool-Agent-User Interaction in Real-World Domains"
    url: https://arxiv.org/abs/2406.12045
    type: primary
  - title: "BFCL V3: Multi-Turn Function Calling"
    url: https://gorilla.cs.berkeley.edu/blogs/13_bfcl_v3_multi_turn.html
    type: primary
  - title: Apple Intelligence Foundation Language Models Tech Report 2025
    url: https://machinelearning.apple.com/research/apple-foundation-models-tech-report-2025
    type: primary
---

因为一次通过不代表模型稳定地遵守了政策，可能只是这次碰巧对了。τ-bench 的做法是同一道题跑多次，看是否每次都遵守政策、正确更新数据库。同题多次运行都稳定通过的轨迹，才适合当 SFT 正例。

## 为什么一次不够

τ-bench 的数字说明了差距有多大：零售域 114 题、航司域 50 题，gpt-4o 函数调用在零售上 $\mathrm{pass}^{1}$ 大约 61%，航司大约 35%；零售跑到 $\mathrm{pass}^{8}$ 就掉到大约 25%。一次通过的轨迹里，有一大半换个随机种子就会失败，把它整段当金标，就是在教不稳定的行为。

另外两个噪声来源也要考虑。论文用语言模型扮演用户，BFCL 也指出模拟用户会幻觉、会跟错指令。题目本身也可能写错：后续公开审计改过「期望动作写错、题面做不到」的题。

## 怎么做

1. 政策进题卡：把退货窗口、改签限制等政策写进题卡，能程序化检查的做成 grader，避免模型只背政策摘要，换一条细则就失败。
2. 查过程：最终数据库状态正确之外，还要检查必要的只读查询，见 `dt-agent-state-path`。
3. 跨次检查：$\mathrm{pass}^{k}$ 用来检查跨次稳定性，决定轨迹能否进 SFT、模型能否发版；训练时仍可给单次状态奖励。
4. 用户侧单独处理：用研究集或人工脚本，不直接把模型模拟的对白当 chosen。
5. 先怀疑标签：轨迹和期望动作冲突时，先复核 grader 和标注是否写错。
6. 补复合请求：论文的失败分析里，多请求和政策推理是两大坑。题集里要有一题两项操作的请求，要求两项都正确写入数据库；一题只考一个目标，测不出这类失败。

## 追问

- **$\mathrm{pass}^{k}$ 是奖励还是门禁？** 门禁。训练仍可用单次状态奖励，进 SFT 和发版才看跨次稳定。
- **和 BFCL 怎么分工？** BFCL 偏 API 形态和中间的只读调用，这张卡更关注业务政策和多次运行是否一致。
