---
id: dt-when-to-search
section: labs
order: 34
level: A
title: Llama 3：什么题该调搜索，什么题不该？数据怎么切桶？
quick: >-
  按三类切桶：必须搜（时事、截止日后的信息）、禁止开放搜索（邮件、日历、图片里的私人信息，用对应工具读）、可搜可答（稳定常识，两种示范都留一点）。只教「有搜索就搜」，模型会把常识题也拖去检索，增加延迟和隐私风险。读私人数据的工具和开放搜索分成两套
  mix，配额分开记。
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
updatedAt: 2026-10-12T00:00:00.000Z
sources:
  - title: The Llama 3 Herd of Models
    url: 'https://arxiv.org/abs/2407.21783'
    type: primary
  - title: 'WebGPT: Browser-assisted question-answering with human feedback'
    url: 'https://arxiv.org/abs/2112.09332'
    type: primary
  - title: Apple Intelligence Foundation Language Models Tech Report 2025
    url: >-
      https://machinelearning.apple.com/research/apple-foundation-models-tech-report-2025
    type: primary
---

我会把题分成三个桶：必须搜、禁止开放搜索、可搜可答。搜索 SFT 的数据要是全是时事题，或者把「该不该搜」完全交给系统提示，模型就会学成「有搜索就搜」，连常识题也拖去检索。

两个方向的错都有代价。必须搜却直接答，算 hallucination，碰巧答对也一样，见 `dt-agent-state-path`。不该搜却搜了，是隐私和延迟问题，比如把用户邮件里的关键词丢给开放搜索，私人信息就流到了外部。

必须搜的是训练截止日期之后的比分、今日股价这类，正确 trajectories 要包含搜索调用，答案要有检索片段支持，见 `dt-webgpt-cite`。禁止开放搜索的是用户邮件里的约定、图片里的文字，应该读对应的来源，读不到就说明限制，见 `dt-grounding-data`。可搜可答的是稳定常识，搜和不搜两套示范都留一点，锚住「不检索也能答」，见 `dt-neg-transfer`。读邮件、日历这类私人数据的是闭集工具，开放搜索是另一条路径，两套 mix 分开，配额写进 dataset card。另外单独造零样本工具题，用目录里没见过的函数、只给签名，和 `dt-tool-alias` 一起练。

## 追问

**Llama 3 公开是怎么做的？**
Llama 3 §4.3.5 为训练截止之后的事件和要点检索训练了 Brave Search，模型还能零样本读懂陌生的工具定义，多跳问题先计划再调用。synthetic data 的顺序是先冷启动单步调用，再标对话，再标多步和数据分析。

**除了搜索还有别的工具，选工具怎么教？**
能执行验证的题优先用解释器，查常量走 Wolfram 一类；数据里要有「选错工具再改」的被放弃的尝试。

**多步计划要不要进训练？**
要进 SFT，但 plan 文本不进奖励，奖励看调用和状态。

**工具步为什么不做 rejection sampling？**
Llama 3 公开说在工具基准上没看到 rejection sampling（RS）的增益，所以没做。我会改成工具步用环境核验，RS 留给最终对用户说的那句话。
