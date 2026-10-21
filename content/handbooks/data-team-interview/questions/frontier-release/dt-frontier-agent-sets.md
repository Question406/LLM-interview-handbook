---
id: dt-frontier-agent-sets
section: frontier-release
order: 4
level: S
title: BrowseComp、OSWorld、τ² 怎么造，各卡 agent 的哪一段？
quick: "这些基准测的是 agent 的不同环节：BrowseComp 用 1266 道人写事实题测持续搜索；OSWorld 原集用 369 个真实桌面任务检查最终状态；τ-bench 看 agent 能否在与模拟用户对话后正确更新数据库，并在多次运行中保持稳定；MCP Atlas 测多步工具流程。所以要分开报，合成一个「工具分数」会掩盖它们各自卡住的环节。"
companies:
  - openai
  - anthropic
  - google
tags:
  - Evaluation
  - Agent
  - Tool use
  - BrowseComp
  - OSWorld
realInterview: false
status: published
format: markdown
updatedAt: 2026-10-12
sources:
  - title: BrowseComp
    url: https://arxiv.org/abs/2504.12516
    type: primary
  - title: OSWorld
    url: https://arxiv.org/abs/2404.07972
    type: primary
  - title: "τ-bench: A Benchmark for Tool-Agent-User Interaction in Real-World Domains"
    url: https://arxiv.org/abs/2406.12045
    type: primary
  - title: Gemini 3.1 Pro Model Card
    url: https://deepmind.google/models/model-cards/gemini-3-1-pro/
    type: primary
  - title: GPT-5.6
    url: https://openai.com/index/gpt-5-6/
    type: primary
  - title: Claude Opus 4.5 System Card
    url: https://www.anthropic.com/claude-opus-4-5-system-card
    type: primary
  - title: Introducing GPT-5
    url: https://openai.com/index/introducing-gpt-5/
    type: primary
---

评价 agent 的工具能力，先要区分它在完成什么任务：根据多条线索查出事实（BrowseComp），用键鼠完成桌面操作（OSWorld），在与用户对话后正确更新业务数据库（τ-bench），或按 MCP 完成多步工具流程（MCP Atlas）。这些任务需要的能力不同，不能合成一个分数就下结论。每套题的覆盖范围也不同，解释分数时要先知道它没测什么。

## BrowseComp

这项评测看 agent 能否持续搜索，并根据结果调整查询。它是 OpenAI 的 1266 道题，由人写，不靠模型造题。它不评价长文质量，也没有覆盖用户意图含糊时如何澄清。论文把它比作编程竞赛：能反映一部分能力，但只是实际产品表现的代理指标。

出题指令沿用 SimpleQA：答案要单一、简短、不会随时间改变、有据可查。和 SimpleQA 的差别在难度门槛。训练员要确认当时的 GPT-4o（开浏览和不开浏览）、o1 以及早期 deep research 都解不出；自己做五次简单搜索，答案不在结果首页；并且难到另一个人十分钟内解不出。还有抽查：第二个人十分钟内能解出超过 40% 的，退回改题。

出题人先选定一个事实，例如某个人、事件或论文，再加上几条需要大量搜索才能核对的条件，问「谁满足这些条件」。出题时已经知道答案，解题者则要把线索逐一查出来。论文里的例子是：某年 EMNLP、第一作者本科在达特茅斯、第四作者本科在宾大，问论文标题。核对只要搜到那篇论文；正着找却要翻几千篇论文的作者背景。论文也写了缺点：无法证明没有第二个合法答案，所以要求出题人熟悉领域，发现别的合法答案时再加约束。

判分时，由模型检查回答与参考答案在语义上是否等价，使用的提示词与 HLE 相同。数据集带有用于追踪训练污染的 canary 字符串。

Gemini 3.1 模型卡（2026-02）的设定是 Search + Python + Browse：Gemini 3.1 Pro 85.9%，Opus 4.6 84.0%，Sonnet 4.6 74.7%，GPT-5.2 65.8%，Gemini 3 Pro 59.2%。GPT-5.6 博文（2026-07）写 Sol 在 BrowseComp 上 92.2%。两份材料相隔五个月，而且 5.6 的博文没有把思考档和工具列全，不要把 92.2 和 65.8 当成「同一协议下 GPT 涨了 26 个点」。

训练侧对应的是「必须搜 / 可以不搜」的分组统计，见 `dt-when-to-search`。带引用的最终答案和浏览过程是不同的监督信号，制作监督微调（SFT）样本时要区分，见 `dt-webgpt-cite`。

## OSWorld

OSWorld（Xie 等）检查 agent 能否从指定的初始状态出发，通过屏幕和键鼠操作达到目标状态。操作路径可以不同，只要最终状态符合检查脚本就算通过。

环境是真电脑（Ubuntu、Windows、macOS 都能接），动作是键鼠操作，不需要为每个 App 定制 API。基准有 369 题，覆盖网页和桌面软件、文件操作和跨应用流程。每题都有初始状态配置和自定义的执行检查脚本，作者写了 134 个不同的检查函数。人的完成率超过 72.36%；论文当时最好的模型只有 12.24%，跨应用流程最高 6.57%。失败集中在看图点坐标和不会基本 GUI 操作。

只看终态也有漏洞：agent 可能修改检查器，或利用环境没有复位而留下的文件来获得通过。所以保存训练轨迹时，还要记录初始状态的哈希和检查器版本，见 `dt-gui-traj`。

版本不能混。Opus 4.5 system card 报 OSWorld 66.3%。GPT-5.6 博文报的是 OSWorld 2.0，Sol 62.6%，并写它用比 Opus 4.8 少 85% 的输出 token 超过了对方。2.0 和原集不是同一列，62.6 低于 66.3 并不构成退步。

## τ-bench 和 τ²

τ-bench（Yao 等）考查 agent 能否在多轮对话里理解约束、正确调用写入工具，并遵守业务政策。用户提出要求，并不意味着 agent 就可以违反政策。场景是零售、航空一类业务，环境包括策略文档、数据库、工具和一个模拟用户。成功看的是对话结束时数据库状态对不对，模型口头说「已改好」不算数。同一策略换几次用户仍要通过，所以他们看 $\mathrm{pass}^{k}$，见 `dt-tau-passk`。

2026 年的发版表写成 τ²，并把 Retail 和 Telecom 分开。Google 模型卡（2026-02）：

| 模型 | Retail | Telecom |
| --- | --- | --- |
| Gemini 3.1 Pro Thinking High | 90.8% | 99.3% |
| Opus 4.6 Thinking Max | 91.9% | 99.3% |
| Sonnet 4.6 Thinking Max | 91.7% | 97.9% |
| GPT-5.2 Thinking xhigh | 82.0% | 98.7% |
| Gemini 3 Pro | 85.3% | 98.0% |

Opus 4.5 system card 自家的数是 Retail 88.9%、Telecom 98.2%，那是 4.5。Telecom 的分数已接近 99%，新增数据有没有效果，在这个切片上已经很难看出来；Retail 仍能区分模型，再加上自己保留的政策评测集（holdout），先找仍然存在的失败，再决定需要什么数据。这时数据应帮助模型在多次运行中稳定执行，并用政策评分器（grader）检查行为是否合法；单独再标一轮回复是否礼貌，解决不了这些问题。

## MCP Atlas，以及还没展开造法的职业任务

MCP Atlas 测的是按 MCP 把多步工具流程走完。Opus 4.5 system card 报 62.3%。Gemini 3.1 卡报 Gemini 3.1 Pro 69.2%，对照列里 Opus 4.6 是 59.5%、GPT-5.2 是 60.6%。4.6 的 59.5 低于 4.5 自家卡的 62.3，应先怀疑 harness 和复现方，不要写成能力回退。公开材料里我没有核对到一份像 SWE-bench 那样写清条数和过滤规则的造法论文，面试时只讲它卡的能力，不编任务数。

另外三项只在发版里出现，造法我没有逐节核对，问到时要说清边界：

- GDPval-AA：Google 卡标成专家任务，报的是 Elo。Gemini 3.1 Pro 1317，GPT-5.2 1462，Sonnet 4.6 1633，Opus 4.6 1606。Elo 不能和准确率比。
- APEX-Agents：卡上写的是长程职业任务。Gemini 3.1 Pro 33.5%，Opus 4.6 29.8%，GPT-5.2 23.0%。
- Agents' Last Exam：只出现在 GPT-5.6 博文。OpenAI 写成 55 个领域的长程职业流程，Sol 53.6。博文没有给出题面过滤和判分脚本；除非你自己核对了单位，不要把 53.6 写成百分数。

GPT-5 博文还单独报了 HealthBench Hard 46.2%。那是健康对话的难子集，和上面的电脑操作不是同一条能力轴。

## 追问

- **BrowseComp 高，产品搜索就好了吗？** 不一定。除了它刻意避开的含糊问题和长答案，产品还要看该不该搜、引用是否支持句子、失败时会不会停。
- **OSWorld 中通过的轨迹都能用于 SFT 吗？** 还要核对当时的可访问性树和最终状态检查脚本。根据过期画面执行的操作、点在动画上的点击，即使任务最后通过了，也应单独作为负例或丢弃，见 `dt-gui-traj`。
