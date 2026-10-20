---
id: fund-judge
section: fundamentals
order: 17
level: S
title: LLM-as-Judge 有哪些常见 Bias？怎么缓解？
quick: "常见偏差包括偏爱某个展示位置、冗长答案、特定文风，以及自己或同家族模型的输出；评分也可能对提示词敏感。可以交换答案顺序检查一致性、随机安排位置、按维度评分、使用多个评委，并用人工校准和对抗样例检验。"
tags:
  - Eval
  - LLM Judge
realInterview: false
status: published
format: markdown
provenance: legacy-handbook-v2
updatedAt: 2026-08-21
sources:
  - title: Judging LLM-as-a-Judge
    url: 'https://arxiv.org/abs/2306.05685'
    type: primary
---

常见误区是：把 judge win-rate 当成能力。LLM-as-Judge 带着位置、篇幅和「像自己」的偏好；用它排模型、筛数据、甚至当 强化学习（RL） 奖励分数（reward） 却不做对抗检验，会把评委自身的偏好当成模型能力。Zheng et al. 的 MT-Bench / Chatbot Arena 工作已经把这些偏差写成必须处理的工程问题。

## 位置、冗长、自我偏好

Position bias：pairwise 里 A/B 对调后结论翻转，说明比的是顺序不是质量；有的模型稳定偏爱先出现的，有的偏爱后出现的。Verbosity bias：更长、更「完整」的答案被偏爱，即使事实更差或在灌水。Self / family preference：judge 偏爱同家族的语气、格式和推理套路；再叠加 style bias，标题、自信措辞、列表排版压过 correctness。Prompt 稍改，排名就会抖。这些偏差会进数据：被抬起来的长答案进入 SFT/DPO，下一轮更长、更像 judge，形成闭环。

## 最低成本的检验是 swap

Swap test：同一对交换顺序各评一次，不一致记 flip 或丢弃，并报告 flip 率。再配合随机位置、隐藏模型身份、长度匹配或长度惩罚。协议应先抽 evidence 再打分，用分维度 rubric（正确、完整、安全、格式），不要只问「哪个更好」。多 judge 聚合、与 human calibration set 对齐 agreement，比盲目换「更强 judge」更靠谱；更强模型也可能更偏爱自己的文风。

Pointwise 可独立标量化、便于回归和阈值，但尺度漂、跨题不可比；pairwise 相对比较通常更稳，却必须做 swap。没有哪一种天然无偏。测 verbosity 的干净做法是构造内容等价、长度不同的 controlled pair，或给同一答案加冗余段，看分数是否单调变好。

## 同一 judge 不能直接当 RL reward

若同一 judge（或同家族）给 RL 打分，policy 会优化 judge 的口味：更长、更客气、更像某模型文风，而不是任务成功。这是 钻奖励规则的空子 的快捷通道。没有独立 验证器（verifier）、单元测试、人类抽检和持续 red-team（对抗冗长、奉承、格式游戏、位置翻转），就宣称「用 LLM 当 reward」，面试里应直接否决。换 judge 家族、监控 swap 稳定性、把评委分数用于筛选，而不是作为唯一奖励，是最低配置。

上线协议我会压成三件事：每条 pairwise 必做 swap 并报 flip 率；每周用固定 human set 估 judge-human agreement，掉了就停用自动排名；RL 若吃 judge 分，必须另有任务成功或单测，且有人专门红队「写长一点就能赢」。缺任何一条，都不要把 LLM-as-Judge 写成金标。

## 追问

- **Pairwise 一定比 pointwise 稳吗？** 相对比较通常更容易，但有 position/order bias，必须做 swap。Pointwise 能量化、好做阈值，但尺度漂、跨题不可比。选哪种取决于你要排名还是要校准分数。
- **如何测 verbosity bias？** 构造内容等价、长度不同的 controlled pair，或给同一答案加冗余段，看分数是否随长度单调变好。长度匹配后差距消失，就说明原先在偏爱篇幅。
- **和 human 对不齐怎么办？** 先修 rubric 和 swap 协议，再换模型。Agreement 低时 judge 只能当筛子，不能当金标，更不能当 RL 的唯一 reward。
