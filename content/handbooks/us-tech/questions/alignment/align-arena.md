---
id: align-arena
section: alignment
order: 16
level: A
title: 对齐：Chatbot Arena / 在线 ELO 的偏差
quick: "Arena 用用户自选问题上的成对投票估计 Bradley-Terry / ELO 强度，适合观察开放对话偏好。分数还受长度、文风、用户与对手分布、匿名和位置影响，发版应结合场次、置信区间与私有能力、安全切片，不能只看小幅 ELO 领先。"
tags:
  - LMSYS
  - Arena
  - ELO
  - Evaluation
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-23
sources:
  - title: Judging LLM-as-a-Judge with MT-Bench and Chatbot Arena
    url: https://arxiv.org/abs/2306.05685
    type: primary
  - title: Chatbot Arena — An Open Platform for Evaluating LLMs by Human Preference
    url: https://arxiv.org/abs/2403.04132
    type: primary
  - title: Length-Controlled AlpacaEval
    url: https://arxiv.org/abs/2404.04475
    type: primary
---

Arena 可以观察用户在开放对话里更愿意使用哪个模型，但分数要连同采样方式一起看。用户自行带题、选择投票，得到的是这群用户在这些 prompt 上的偏好，不能直接覆盖全部能力。

LMSYS 把匿名两模型回答的投票做成动态榜单。MT-Bench 论文讨论人偏好与 LLM judge 的一致性，后续 Arena 论文介绍平台、ELO 和置信区间。这道题据公开资料整理，并非现场逐字记录，重点是如何解释榜分。

用户题目偏聊天、代码和文风，英语多，投票者本身也是关心模型的子群；难题还可能更多给当时头名，新旧模型面对的分布并不一样。热门模型场次多，冷门模型区间宽，不能只按点估计硬排。平局、跳过和用户只评熟悉的题，也会影响估计。

Bradley-Terry 近似假设偏好可传递，再估强度、报 ELO 和区间。但 A 在写作胜、B 在代码胜、C 在安全拒答胜，偏好可能成环，总分会隐藏任务差异。匿名与位置随机化也很重要，露出名字会引入粉丝和声誉，固定位置会引入先后偏差，相关 judge 偏差见 `align-llm-judge`。

## 怎样区分能力与文风

更长、更像助手、Markdown 列表或客套都可能增加投票，即使任务能力没变。对着 Arena 调提示，会把公开榜当成 RM，见 `align-reward-hack`、`align-length-bias`。同一用户反复投相似题也会放大个人文风权重，需要按用户和 prompt 近邻去重。

榜单还是非平稳的：用户、对手池、默认温度、新模型都在改变，旧分与新分未必同尺度。新模型早期场次少、点估计会跳；差 5 分且区间重叠时应视作并列。Glicko / 贝叶斯区间比只报裸 ELO 更能表达不确定性，style / length control 可以减少相应偏差，仍消不掉自选 prompt 与用户子群偏差。

我会同时报模型版本、对战场次、区间、平均长度和是否 style-controlled，再分写作、代码、拒绝切片。可以用横轴真实任务成功率、纵轴 Arena ELO 来看：只涨 ELO 先查长度排版，只涨任务成功率却降 ELO，也可能是回答变短、少了套话。总分领先但拒绝切片崩溃，仍不能通过验收。

发版则使用私有能力切片、安全、污染报告、长度匹配人偏好，再参考 Arena 方向，见 `design-eval-platform`。Arena 适合发现开放对话变差、文风异常和竞品观感差异，不能替代 GSM、代码单测、安全红队，也不能单独确定 KL、$\beta$ 或证明对齐进步。单独新高新低只触发调查。

公开题、内部套话、jailbreak 模板也可能被用户带进 Arena。拿这些投票做训练会泄露测试分布，见 `align-eval-contam`，因此不把公开活榜做训练闭环。内部可以借鉴盲测、换位和固定题库的协议，轮换独立盲测集，不能直接复制公开流量当回归门槛。

## 追问

**ELO 与 BT 差在哪？**
都估成对强度。ELO 受对局顺序、更新步长影响，静态 BT 一次拟合全部对，非平稳时都会漂。

**小幅领先能写全面领先吗？**
不能。先看区间与任务切片，写作赢、安全输应分别说明。

**匿名失效怎么办？**
分数混入声誉影响，需重新盲测，调温度多跑一场不能补救。

**和离线集、MT-Bench 怎么一起看？**
离线集可分层复现但会过时，Arena 活跃但难重现同一场；MT-Bench 是固定题。方向矛盾时先查长度、文风与泄漏，见 `design-offline-eval`。

## 相关题

- [[xai-lmarena]]：在线 Elo 转 BT 全局 MLE 与 Grok 博文分数。
- [[align-llm-judge]]：位置、长度和自偏好偏差。
- [[align-length-bias]]：偏好管道中的长度影响。
- [[anthropic-pref-bt]]：BT 如何处理平局和噪声。
