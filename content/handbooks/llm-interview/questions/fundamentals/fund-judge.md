---
id: fund-judge
section: fundamentals
order: 17
level: S
title: LLM-as-Judge 有哪些常见 Bias？怎么缓解？
quick: >-
  常见的有 position bias、冗长偏差、偏爱特定文风或自己 / 同家族模型的输出，评分还会对 prompt 敏感。缓解从最便宜的 swap test
  做起：交换顺序看结论是否翻转，再加随机位置、按维度打分、多评委，并用人工 calibration 集和对抗样例检验。同一个 judge 不能直接当 RL
  的唯一奖励。
tags:
  - Eval
  - LLM Judge
realInterview: false
status: published
format: markdown
provenance: legacy-handbook-v2
updatedAt: 2026-08-21T00:00:00.000Z
sources:
  - title: Judging LLM-as-a-Judge
    url: 'https://arxiv.org/abs/2306.05685'
    type: primary
---
LLM-as-Judge 主要有三类偏差：位置、篇幅，以及偏爱「像自己」的输出，缓解的第一步是每次 pairwise 都交换顺序再评一遍。不处理这些偏差，拿 judge 的 win-rate 去排模型、筛数据，甚至当 RL 的奖励分数（reward），就是把评委自己的偏好当成了模型能力。Zheng et al. 的 MT-Bench / Chatbot Arena 工作已经把这些偏差写成了必须处理的工程问题。

举个例子，两个回答 A 和 B，A 放前面时 judge 说 A 好，把 B 换到前面它又说 B 好，这说明它比的是顺序；再给 B 加一段内容重复的总结，分数涨了，说明它在奖励篇幅。

## 位置、冗长、自我偏好

Position bias 是 pairwise 里 A / B 对调后结论翻转，有的模型稳定偏爱先出现的，有的偏爱后出现的。Verbosity bias 是更长、看起来更「完整」的答案被偏爱，哪怕事实更差、在灌水。Self / family preference 是 judge 偏爱同家族的语气、格式和推理套路；再叠上 style bias，标题、自信的措辞、列表排版会压过正确性。Prompt 稍微改一下，排名就会抖。

这些偏差还会进数据：被抬高的长答案进了 SFT / DPO，下一轮模型更长、更像 judge，形成 feedback loop。

## 最低成本的检验是 swap

Swap test 就是同一对答案交换顺序各评一次，结论不一致就记一次 flip 或者丢弃，并报告 flip 率。在此基础上再加随机位置、隐藏模型身份、长度匹配或长度惩罚。评分协议要先抽证据再打分，用分维度的 rubric（正确、完整、安全、格式），别只问「哪个更好」。多个 judge 聚合、在 human calibration set 上对齐 agreement，比盲目换一个「更强的 judge」靠谱，更强的模型也可能更偏爱自己的文风。

Pointwise 能独立给出标量分，方便做回归和定阈值，但尺度会漂，跨题不可比；pairwise 做相对比较通常更稳，但必须做 swap。哪一种都不是天然无偏的。测 verbosity bias 的干净做法，是构造内容等价、长度不同的 controlled pair，或者给同一个答案加冗余段落，看分数是不是随长度单调变好。

## 同一个 judge 不能直接当 RL reward

如果让同一个 judge（或同家族模型）给 RL 打分，policy 会去优化 judge 的口味：更长、更客气、更像某个模型的文风，任务本身未必做成了。这是钻奖励规则空子的快捷通道。没有独立的验证器（verifier）、单元测试、人工抽检，也没有持续的 red-team（专门对抗冗长、奉承、格式游戏、位置翻转），就宣称「用 LLM 当 reward」，面试里应该直接否掉。最低配置是换 judge 家族、监控 swap 稳定性，把评委分数用来筛选，别让它当唯一奖励。

上线协议我会压成三件事。每条 pairwise 都做 swap 并报 flip 率；每周用固定的 human set 估一次 judge 和人的 agreement，掉了就停用自动排名；RL 如果吃 judge 分，必须另有任务成功信号或单测，并有人专门红队「写长一点就能赢」这类漏洞。缺了任何一条，都别把 LLM-as-Judge 当金标。

## 追问

**Pairwise 一定比 pointwise 稳吗？**
相对比较通常更容易，但有 position / order bias，必须做 swap。Pointwise 能量化、好定阈值，但尺度漂、跨题不可比。选哪种看你要排名还是要 calibration 过的分数。

**怎么测 verbosity bias？**
构造内容等价、长度不同的 controlled pair，或者给同一答案加冗余段落，看分数是否随长度单调变好。长度匹配以后差距消失，就说明原先是在偏爱篇幅。

**和人工标注对不齐怎么办？**
先修 rubric 和 swap 协议，再考虑换模型。Agreement 低的时候，judge 只能当筛子，当不了金标，更不能当 RL 的唯一 reward。
