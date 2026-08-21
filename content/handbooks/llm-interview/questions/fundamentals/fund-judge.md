---
id: fund-judge
section: fundamentals
order: 17
level: S
title: LLM-as-Judge 有哪些常见 Bias？怎么缓解？
quick: >-
  常见 position bias、verbosity bias、style bias、self/family preference、prompt
  sensitivity。可做 swap consistency、random position、rubric 分维度、multiple
  judges、human calibration 与 adversarial examples。
tags:
  - Eval
  - LLM Judge
realInterview: false
status: published
format: markdown
provenance: legacy-handbook-v2
updatedAt: 2026-08-19
sources:
  - title: Judging LLM-as-a-Judge
    url: 'https://arxiv.org/abs/2306.05685'
    type: primary
---

LLM-as-Judge 看起来像中立裁判，其实带着位置、篇幅和「像自己」的偏好。用它排模型、筛数据、甚至当 RL reward，而不做对抗检验，等于让评委和选手穿同一件衣服。陷阱是把 judge win-rate 直接当成能力——Zheng et al. 的 MT-Bench / Chatbot Arena 工作已经把这些偏差写成必须处理的工程问题，而不是脚注。

## 位置、冗长、自我偏好

**Position bias：** pairwise 里 A/B 对调后结论翻转，说明比的是顺序不是质量；有的模型稳定偏爱先出现的，有的偏爱后出现的。**Verbosity bias：** 更长、更「完整」的答案被偏爱，即使事实更差或在灌水。**Self / family preference：** judge 偏爱同家族的语气、格式和推理套路；再叠加 style bias——标题、自信措辞、列表排版压过 correctness。Prompt 稍改，排名就会抖。这些偏差会进数据：被抬起来的长答案进入 SFT/DPO，下一轮更长、更像 judge，形成闭环。

## 最低成本的检验是 swap

**Swap test：** 同一对交换顺序各评一次，不一致记 flip 或丢弃，并报告 flip 率。再配合随机位置、隐藏模型身份、长度匹配或长度惩罚。协议应先抽 evidence 再打分，用分维度 rubric（正确、完整、安全、格式）而不是一个「哪个更好」。多 judge 聚合、与 human calibration set 对齐 agreement，比盲目换「更强 judge」更靠谱——更强模型也可能更会偏爱自己的文风。

Pointwise 可独立标量化、便于回归和阈值，但尺度漂、跨题不可比；pairwise 相对比较通常更稳，却必须做 swap。没有哪一种天然无偏。测 verbosity 的干净做法是构造内容等价、长度不同的 controlled pair，或给同一答案加冗余段，看分数是否单调变好。

## 同一 judge 不能直接当 RL reward

若同一 judge（或同家族）给 RL 打分，policy 会优化 judge 的口味：更长、更客气、更像某模型文风，而不是任务成功。这是 reward hacking 的快捷通道。没有独立 verifier、单元测试、人类抽检和持续 red-team（对抗冗长、奉承、格式游戏、位置翻转），就宣称「用 LLM 当 reward」，面试里应直接否决。换 judge 家族、监控 swap 稳定性、把 judge 分数当筛子而不是唯一标量，是最低配置。

上线协议可以压成三件事：每条 pairwise 必做 swap 并报 flip 率；每周用固定 human set 估 judge–human agreement，掉了就停用自动排名；RL 若吃 judge 分，必须另有任务成功或单测，且有人专门红队「写长一点就能赢」。缺任何一条，都不要把 LLM-as-Judge 写成金标。

## 追问

- **Pairwise 一定比 pointwise 稳吗？** 相对比较通常更容易，但有 position/order bias，必须做 swap。Pointwise 能量化、好做阈值，但尺度漂、跨题不可比。选哪种取决于你要排名还是要校准分数。
- **如何测 verbosity bias？** 构造内容等价、长度不同的 controlled pair，或给同一答案加冗余段，看分数是否随长度单调变好。长度匹配后差距消失，就说明原先在偏爱篇幅。
- **和 human 对不齐怎么办？** 先修 rubric 和 swap 协议，再换模型。Agreement 低时 judge 只能当筛子，不能当金标，更不能当 RL 的唯一 reward。
