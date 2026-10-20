---
id: dt-when-to-search
section: labs
order: 34
level: A
title: Llama 3：什么题该调搜索，什么题不该？数据怎么切桶？
quick: "训练题分为必须搜索、禁止搜索和可搜可直接答三类。时事需要检索证据；邮件、日历里的私人信息应使用相应工具；稳定常识也要保留不搜索的示范。只教「有搜索就搜」会增加延迟和隐私风险。用户查询不能默认进入全球基础模型训练。"
companies:
  - apple
tags:
  - Meta
  - Search
  - Tool Use
  - Apple
realInterview: false
status: published
format: markdown
updatedAt: 2026-10-12
sources:
  - title: The Llama 3 Herd of Models
    url: https://arxiv.org/abs/2407.21783
    type: primary
  - title: "WebGPT: Browser-assisted question-answering with human feedback"
    url: https://arxiv.org/abs/2112.09332
    type: primary
  - title: Apple Intelligence Foundation Language Models Tech Report 2025
    url: https://machinelearning.apple.com/research/apple-foundation-models-tech-report-2025
    type: primary
---

我会把数据分成三类。必须搜的题包括训练截止日期后的比分和今日股价，正确轨迹要包含搜索调用，答案要有检索片段支持，见 `dt-webgpt-cite`。禁止开放搜索的题包括用户邮件里的约定、图片中的文字，应读取对应来源，无法读取时说明限制，见 `dt-grounding-data`。可搜可答：稳定常识，两套都留一点，锚住不检索也能答，见 `dt-neg-transfer`。必须搜却直接答，当幻觉，即使碰巧对，见 `dt-agent-state-path`。不该搜却搜了，是隐私和延迟问题：端上把邮件关键词丢给开放搜索，通道错了。零样本工具另造：目录里没见过的函数，只给签名，和 `dt-tool-alias` 一起练。

不这么选的理由：搜索 监督微调（SFT） 全是时事题，或把「该不该搜」交给系统提示。全是「有搜索就搜」，模型会把常识题也拖去检索。

接到苹果：日历 / 邮件是闭集工具，开放搜索是另一条。两套 mix 分开，配额写在 dataset card。用户查询默认不进全球 FM。能执行验证的题优先解释器，查常量走 Wolfram 一类；数据里要有「选错工具再改」的被放弃的尝试。多步计划要进 SFT，plan 文本不进奖励，奖励看调用和状态。他们公开说工具基准上没看到拒绝采样的增益所以没做；我会改成工具步用环境核验，RS 留给最终对用户的那句。

公开锚点：Llama 3 §4.3.5 为截止之后的事件和要点检索训了 Brave Search，还能零样本看陌生工具定义；多跳就先计划再调；合成先冷启动单步，再标对话，再标多步和数据分析。

## 追问

- **Wolfram 和 Python 谁先？** 能执行验证的题优先解释器；查常量走 Wolfram。数据里要有「选错工具再改」的被放弃的尝试。
- **为什么工具不做 RS？** 他们公开说基准没涨。我会改成：工具步用环境核验，RS 留给最终对用户的那句。
- **多步计划要不要进 SFT？** 要，但 plan 文本不进奖励。奖励看调用和状态。
