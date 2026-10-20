---
id: pt-reasoning-seed-data-quality
section: posttrain
order: 42
level: S
title: 为什么少量高质量 expert CoT 有时能激活 reasoning，而大量普通 CoT 不行？
quick: "Seed data 的价值在于把策略送进能探索、能被 验证器（verifier） 区分的轨迹区域，不在 token 总量。优先看题目难度、答案与步骤正确性、关键决策密度、格式一致性和与目标任务的匹配，再做小规模 ablation。"
tags:
  - Seed Data
  - Chain of Thought
  - SFT
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-21
sources:
  - title: The Challenge of Teaching Reasoning to LLMs Without RL or Distillation
    url: https://arxiv.org/abs/2507.09850
    type: primary
---

Reasoning seed 的作用不是「多喂一些思考文本」，而是把政策从「不会进入可验证成功区」推进到「能被后续 RL / 搜索区分好坏」的区域。少量 expert 思维链（CoT，即分步推理过程） 若题目够难、步骤可验证、关键转折密、格式稳定，就能完成这次位移；大量普通 CoT 常在教「写很长、套模板、中间步可以错」。这块容易把 LIMA 式「少即是多」当成普遍规律，或反过来迷信数据吨数。`pt-cold-start-to-multistage-rl` 解释为何生产仍要 cold start；本题解释 cold start 该看哪些质量轴。

## 普通 CoT 在教什么表面统计

普通轨迹常有三类问题：冗余模板（「让我们一步步思考」但无决策）、错误中间步、对目标模型过难或过易的题。大规模混入后，监督微调（SFT） 先拟合表面风格：变长、变礼貌、变会分段。后续 强化学习（RL） 若奖励终局正确，这些风格会被当成相关特征一起放大；若过程奖励有洞，错误中间步会被写成「看起来像证明」。

高质量 expert trace 提供的是可验证的关键转折、稳定的解析格式，以及足够难、能让 验证器（verifier） 给出有意义对错差的题。对 `pt-r1zero` 路线，seed 甚至可以很少，但必须让模型先产出能被解析、能拿到非零 奖励分数（reward） 的样本。对纯 SFT、无 RL 的设定，seed 质量更决定你有没有把正确算法写进监督。

## 选择清单与固定 token 预算的消融

数据选择应分开检查，而不是只看「像不像 CoT」：

| 轴 | 问什么 |
| --- | --- |
| 难度 | 对当前学生是否处于可学区间 |
| 终局 | 答案是否可验证正确 |
| 步骤 | 每步是否有效、有无跳步 |
| 密度 | 关键决策 / 总 token |
| 格式 | 语言、工具调用是否一致 |
| gap | 教师模型（teacher） 是否远超学生能模仿的范围 |

最有效的实验是固定总 token，替换不同质量 / 难度的 seed，测三件事：冷启动后可解析成功率、后续 RL 学习曲线、分布外数据（OOD，即与训练数据明显不同的数据） 泛化。质量组用更少条数胜过数量组，结论才站得住；否则只是换了计算。也要测「错但漂亮」的对照：它常比随机噪声更伤，因为它像正例。再加一组「对但无关键转折」的对照，用来证明密度本身有贡献，而不是「只要答案对就行」。

Teacher-student gap 要单独画：把同一批 expert 轨迹按对学生的可模仿性分组统计（学生在该前缀上的困惑度）。过高 gap 的轨迹在 SFT 里像噪声，进 RL 也给不出中间状态。这时应降难度、加脚手架，或先格式冷启动再注入决策。

## 不要神化「少量」

对知识缺口任务，seed 仍需覆盖事实与工具使用，再漂亮的通用推理格式也补不上未知 API。对 verifier 有漏洞的任务，再干净的 CoT 也会把模型带向错误奖励。对学生远弱于 teacher 的情况，expert 轨迹可能不可学，需要先降难度或先训格式。

Seed 只负责把政策送进可探索区域；区域外的能力仍要靠 RL、工具或更多针对性数据。`pt-cold-start-to-multistage-rl` 里 cold start 的职责正是「可读、可解析、能拿到非零 reward」，不是一次训成最终推理器。把「几条神数据激活推理」讲成普遍科学，和把「必须百万条 CoT」讲成普遍科学，是对称的面试错误。

白板设计：四组等 token，高质量难、高质量易、普通长、错但漂亮，先看冷启动格式率，再接同一套 RL。若只有高质量难能让后续 reward 出现稳定方差，就说明 seed 的价值在于进入可区分区域，而不在字数。面试时先写质量轴，再写等 token 四组对照，最后才谈「少即是多」。没有固定 token 和「错但漂亮」对照，数量组输赢说明不了机制。

## 追问

- **为什么数量组会输？** 它主要拟合风格和错误中间步，后续 reward 难以把政策拉回正确算法。RL 需要的是可区分的对错差，不是「看起来在思考」的边际。
- **和 long-to-short 的数据过滤有何关系？** 同一原则：错很长的推理过程不能进监督。见 `pt-long-to-short-reasoning`。seed 阶段引入的错误，可能被压缩和 RL 继续保留或放大。
- **没有 verifier 怎么挑 seed？** 用更强独立 judge 加人工抽检，并单独标步骤错误；不要只看最终答案。judge 要固定版本，避免和后续 self-judge 回路搅在一起。
- **冷启动之后还要不要混普通 CoT？** 可以混格式 / 指令数据，但不要用低密度长思考稀释已经对齐的推理区域。`pt-cold-start-to-multistage-rl` 的冷启动目标是可解析、能拿到 reward，不是把普通 CoT 堆满。
