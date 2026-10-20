---
id: dt-tool-write-confirm
section: posttrain-data
order: 12
level: A
title: 会改状态的工具，数据里要不要先确认再写？
quick: "工具目录标记 read / write。读取按任务自动执行，含糊或需确认的写操作先澄清、确认；已有明确且唯一的授权可按协议直接执行。训练覆盖用户拒绝后停止，评分检查确认与实际状态，不能只看写入结果。"
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

读取可按任务自动调用；删除邮件、转账和修改日历等写操作，需要根据明确授权和产品策略决定是否先复述、确认。示范也要覆盖用户拒绝后不执行。只检查最终状态，可能漏掉未经确认的误操作。

不这么选的理由：数据如果总是直接执行 `cancel_order`，模型就学不到何时需要确认。这和「终局对就算过」反着来，见 `dt-agent-state-path`。那边说的是漏只读；这边说的是多写。τ-bench 的零售 / 航空域，写库是核心，政策常要求确认。

苹果：用户日志不进基础模型。写操作示范在可回滚环境里造。产品还有隐私和误操作成本，这一刀比 BFCL 的 irrelevance 更贴端侧。

## 标签怎么切

工具目录带副作用标记：`read` / `write`。标注协议：write 之前必须有一轮用户可见的确认，除非用户已经给了明确祈使（「把今天下午三点的会删掉」且只有一场）。模棱两可（「清掉一些会」）必须问。

正例：确认轮 + 写 + 状态对。负例：没确认就写，即使最终状态碰巧对。

用户拒绝：写不发生，回复承认取消。训练要覆盖这种停止轨迹，避免模型把拒绝当作改用另一种方法继续执行。

## 合成

环境里把 write 工具的确认做成硬策略 grader：没看到确认轮就零分。比人事后看 diff 便宜。不要用 LLM judge 说「好像确认了」。

## 追问

- **和安全拒答一张卡吗？** 安全是不该做的请求。确认是该做但要人点头。配比分开，见 `dt-safety-refuse`。
- **只读工具也确认？** 不要。会把 agent 变成事事请示，τ-bench 政策也会烦。在 schema 中明确标记读写类型。
- **端侧 Siri 动作？** 公开口径是隐私敏感留本地。数据示范仍是：写操作可见、可撤销。不要编内部意图分类名。
