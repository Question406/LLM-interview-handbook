---
id: dt-tau-passk
section: labs
order: 35
level: A
title: τ-bench：过一次库状态，为什么还不够当正例？
quick: "τ-bench 不只看一次成功，还看同题多次运行是否稳定遵守政策、正确更新数据库。用 $\\mathrm{pass}^{k}$ 做跨次检查，训练可使用单次状态奖励。进入 SFT 的轨迹也要查必经只读调用；用户模拟和 grader 标签需独立复核。"
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

先把退货窗口、改签限制等政策写进题卡，能程序化检查的做成 grader，避免模型只背政策摘要、换一条细则就失败。最终数据库状态正确，还要检查必要的只读查询，见 `dt-agent-state-path`。同题多次运行稳定通过，才适合作为 SFT 成功轨迹。用户侧使用研究集或人工脚本，不直接把模型模拟的对白当 chosen。$\mathrm{pass}^{k}$ 用于检查跨次稳定性；训练仍可给单次状态奖励。若轨迹与期望动作冲突，也要先复核 grader 和标注是否写错。

不能只因一次通过，就把整段对话当金标。gpt-4o 函数调用零售 $\mathrm{pass}^{1}$ 大约 61%，再跑到 $\mathrm{pass}^{8}$ 掉到大约 25%。论文用 LM 造用户，BFCL 也点过模拟用户会幻觉、会跟错指令。

接到苹果：日历 / 邮件助手同样有政策（谁能改、改完要不要确认）。用户原话默认不进全球 FM，见 `dt-privacy-feedback`。能进训练的是许可脚本和合成复现。复合请求要有「两项操作都正确写入数据库」的题，论文失败分析里多请求和政策推理是两大坑。和 BFCL 分工：BFCL 偏 API 形态和中间只读，这题更关注业务政策和多次运行是否一致。

公开锚点：τ-bench 零售 114 题、航司 50 题；gpt-4o 函数调用零售 $\mathrm{pass}^{1}$ 大约 61%，航司大约 35%，零售 $\mathrm{pass}^{8}$ 掉到大约 25%。后续公开审计还改过「期望动作写错、题面做不到」的题。

## 追问

- **$\mathrm{pass}^{k}$ 算奖励还是门禁？** 门禁。训练仍可用单次状态奖励；发版和进 SFT 看跨次稳定。
- **复合请求呢？** 论文失败分析里，多请求和政策推理是两大坑。一题一目标不够，要有「两件事都写进库」的题。
- **和 BFCL 怎么分工？** BFCL 偏 API 形态和中间只读。这张卡偏政策和跨次一致。
