---
id: dt-tau-passk
section: labs
order: 35
level: A
title: τ-bench：过一次库状态，为什么还不够当正例？
quick: >-
  假设同一道工具任务跑了五次，只成功一次。Pass@5 关心至少一次成功，因此可能很好看；pass^5
  关心五次都成功，就会很低。它们回答的是探索能力和执行可靠性两种问题。
companies:
  - apple
tags:
  - Sierra
  - Agent
  - Tool Use
  - Apple
  - 口述改写 2026-10-28
realInterview: false
status: published
format: markdown
updatedAt: '2026-10-28'
sources:
  - title: 'τ-bench: A Benchmark for Tool-Agent-User Interaction in Real-World Domains'
    url: 'https://arxiv.org/abs/2406.12045'
    type: primary
  - title: 'BFCL V3: Multi-Turn Function Calling'
    url: 'https://gorilla.cs.berkeley.edu/blogs/13_bfcl_v3_multi_turn.html'
    type: primary
  - title: Apple Intelligence Foundation Language Models Tech Report 2025
    url: >-
      https://machinelearning.apple.com/research/apple-foundation-models-tech-report-2025
    type: primary
---

## 回答思路

> **问题与场景：** 假设同一道工具任务跑了五次，只成功一次。
>
> **做法与原因：** 像退货或改签这样的任务，我会既检查最终数据库状态，也检查政策与授权。
>
> **检查与取舍：** 做训练数据时要保留每次尝试的证据，独立验证成功轨迹，不把“这个任务某次过了”当成其他尝试也正确。

## 可以这样回答

假设同一道工具任务跑了五次，只成功一次。Pass@5 关心至少一次成功，因此可能很好看；pass^5 关心五次都成功，就会很低。它们回答的是探索能力和执行可靠性两种问题。

像退货或改签这样的任务，我会既检查最终数据库状态，也检查政策与授权。一次结果正确，不代表执行路径合法，更不代表重复运行仍可靠。

做训练数据时要保留每次尝试的证据，独立验证成功轨迹，不把“这个任务某次过了”当成其他尝试也正确。具体 benchmark 规模与公式见后面的来源说明。

## 技术备查

因为一次通过可能只是这次碰巧对了，说明不了模型稳定地遵守了政策。τ-bench 的做法是同一道题跑多次，看是不是每次都遵守政策、正确更新数据库。同题多次运行都稳定通过的 trajectories，才适合当 SFT 正例。

差距有多大，τ-bench 的数字很直观：零售域 114 题、航司域 50 题，gpt-4o 函数调用在零售上 $\mathrm{pass}^{1}$ 大约 61%，航司大约 35%；零售跑到 $\mathrm{pass}^{8}$，就掉到大约 25%。也就是说，一次通过的 trajectories 里有一大半换个 random seed 就会失败，把它整段当 gold labels，就是在教不稳定的行为。

造数据时，先把退货窗口、改签限制这些政策写进题卡，能程序化检查的做成 grader，免得模型只背政策摘要，换一条细则就失败。最终数据库状态对了，还要查必要的只读查询，见 `dt-agent-state-path`。然后用 $\mathrm{pass}^{k}$ 检查跨次稳定性，决定 trajectories 能不能进 SFT、模型能不能发版。trajectories 和期望动作冲突时，先复核 grader 和标注是不是写错了，题目本身也可能有错，后续公开审计就改过「期望动作写错、题面做不到」的题。

## 追问

**$\mathrm{pass}^{k}$ 是奖励还是 evaluation gate？**
evaluation gate。训练仍可用单次状态奖励，进 SFT 和发版才看跨次稳定。

**模型扮演的用户靠得住吗？**
不太靠得住。论文用语言模型扮演用户，BFCL 也指出模拟用户会 hallucination、会跟错指令。所以用户侧用研究集或人工脚本，模型模拟的对白不直接当 chosen。

**题集里最容易缺什么题？**
复合请求。论文的失败分析里，多请求和政策推理是两大坑。题集里要有一题两项操作的请求，要求两项都正确写入数据库；一题只考一个目标，测不出这类失败。

**和 BFCL 怎么分工？**
BFCL 偏 API 形态和中间的只读调用，这张卡更关注业务政策和多次运行是否一致。
