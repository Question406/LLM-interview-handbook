---
id: anthropic-agent-eval
section: anthropic
order: 29
level: S
title: Anthropic：OSWorld / WebArena 类公开基准怎么讲？污染和成功定义卡在哪？
quick: >-
  Agent 基准先按任务终态判功能正确，再固定分数汇总、步数预算和输入模态。WebArena 查最终状态，OSWorld 部分题有 [0, 1]
  完成度，要保留原始分。公开题面、检查器和轨迹都可能泄漏，发版还需私有任务与单列安全指标。
tags:
  - Anthropic
  - Agents
  - Evaluation
  - Computer use
  - 口述改写 2026-10-28
realInterview: false
status: published
format: markdown
updatedAt: '2026-10-28'
sources:
  - title: 'WebArena: A Realistic Web Environment for Building Autonomous Agents'
    url: 'https://arxiv.org/abs/2307.13854'
    type: primary
  - title: >-
      OSWorld: Benchmarking Multimodal Agents for Open-Ended Tasks in Real
      Computer Environments
    url: 'https://arxiv.org/abs/2404.07972'
    type: primary
  - title: Developing a computer use model (Anthropic)
    url: 'https://www.anthropic.com/research/developing-computer-use'
    type: primary
---

## 可以这样回答

WebArena / OSWorld 应先看任务有没有完成，再解释成功率怎么算、用了多少步，以及训练是否见过题。比如文件早已在磁盘上，agent 随便点一圈也拿分，终态分虽然高，轨迹并没有证明操作能力。需要把功能检查与轨迹抽查结合。

WebArena（Zhou 等，约 812 题）运行在可自托管的电商、论坛、开发协作和 CMS 站点。它用 functional correctness 检查数据库、页面内容和最终 URL，合法路径可以不止一条。原论文最佳 GPT-4 配置约 14%，人类约 78%，差距反映了长程规划与恢复等困难。

## 技术备查

WebArena / OSWorld 应先看任务有没有完成，再解释成功率怎么算、用了多少步，以及训练是否见过题。比如文件早已在磁盘上，agent 随便点一圈也拿分，终态分虽然高，轨迹并没有证明操作能力。需要把功能检查与轨迹抽查结合。

## 功能正确与动作路径分开

WebArena（Zhou 等，约 812 题）运行在可自托管的电商、论坛、开发协作和 CMS 站点。它用 functional correctness 检查数据库、页面内容和最终 URL，合法路径可以不止一条。原论文最佳 GPT-4 配置约 14%，人类约 78%，差距反映了长程规划与恢复等困难。

OSWorld（Xie 等，约 369 题）转到真实桌面，主评 Ubuntu，也讨论 Windows / macOS，涉及文件、办公套件、浏览器和跨应用。检查器读文件系统、应用输出，有时查网络副作用。部分任务给 $[0,1]$ 完成度，排行榜把原始分相加除以题数，再四舍五入，不能把 0.5 等部分完成分先阈值化成 0/1。早期 agent 约一成二、人类约七成二，人类中位耗时也更长。

这些基准检查任务终态，敏感动作前是否确认需要另一列安全指标，见 `anthropic-computer-use`。越权点击和执行注入指令应单列，否则一个完成任务但违规的轨迹会被总分掩盖。

## 控制泄漏后再解释分数

公开任务、站点镜像和检查器都可能被预训练扫到。下面几种泄漏需要分别查：

| 漏什么 | 为什么涨分 | 怎么查 |
| --- | --- | --- |
| GitHub 上的任务 JSON / README | 模型背指令和站点结构 | 训练切分、检索重叠 |
| 评测脚本 | 直接优化检查器而不是任务 | 换等价检查器看分是否崩 |
| 人类示范视频和轨迹 | 变成逐步克隆 | 打乱 UI 主题 / 分辨率 |
| 排行榜本身 | 在测试集上调 prompt | 留私有持出、定期换题 |

UI 版本也会改变结果：Ubuntu 22 的 Save 在 24 中换位置，记住轨迹的策略可能掉点。公开分包含能力和污染的影响，需要配合冻结私有集、任务轮换，必要时用直播站验证。`anthropic-eval-honesty` 中的证据检查，在这里对应抽查任务究竟是怎样做完的。

报分前固定检查器版本，并把 WebArena 不可完成题中的正确认输与乱试分开。声明步数 / 时间预算，预算加倍会改变成功率；声明纯 DOM / 无障碍树、截图或两者的输入方式。Claude computer use 是截图加动作，与 WebArena 早期文本 agent 的 ACI 不同。OSWorld 保留原始 $[0,1]$ 分，还要按办公 / 浏览器分域。

失败可分定位、操作知识、注入和超时，Anthropic 研究文把早期主要失败归为 grounding 与操作知识。LLM 看截图能辅助分析，不能取代功能检查；测试集上穷举 system prompt 或关确认框，也会改变对比含义。训练奖励要来自训练切分或私有任务，直接拿公开测试检查器做 RL 会泄漏，见 `anthropic-computer-rl`。

## 追问

**动作匹配能当成功指标吗？**
不适合。合法绕路会被误判，克隆演示又可能被高估；动作匹配可用于定位单元测试。

**LLM 裁判能做什么？**
可以辅助失败聚类和轨迹分析，但它有 length bias，可能被看起来忙的长轨迹误导。

**和 needle、Arena 怎么分工？**
`anthropic-needle` 测窗口检索，对话 Arena 测观感，agent 基准测任务副作用，分别解释。

**内部最该补什么？**
带注入的截图、分辨率扰动和敏感动作前的确认检查，公开基准很少覆盖这些条件。
