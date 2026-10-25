---
id: pt-reasoning-seed-data-quality
section: posttrain
order: 42
level: S
title: 为什么少量高质量 expert CoT 有时能激活 reasoning，而大量普通 CoT 不行？
quick: "seed 的价值在于把策略送进能探索、能被 verifier 区分对错的区域，和 token 总量关系不大。挑 seed 先看题目难度、答案和步骤是否正确、关键决策密度、格式一致性以及 teacher-student gap，再用固定 token 的小规模 ablation 验证。"
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

少量 expert CoT 能起作用，是因为它把策略送进了一个能被后续 RL 或搜索区分好坏的区域；大量普通 CoT 常常在教「写很长、套模板、中间步可以错」。决定效果的是题够不够难、步骤能不能验证、关键转折密不密、格式稳不稳，条数是次要的。

普通 CoT 的毛病通常有三类：冗余模板，比如写了「让我们一步步思考」却没有任何决策；错误的中间步；对目标模型过难或过易的题。大量混进去以后，监督微调（SFT）先学会的是表面风格，变长、变礼貌、会分段。后面的强化学习（RL）如果奖励终局正确，这些风格会被当成相关特征一起放大；过程奖励有洞的话，错误中间步会被写成「看起来像证明」。

高质量 expert trace 提供的是可验证的关键转折、稳定的解析格式，以及足够难、能让验证器（verifier）给出有意义对错差的题。走 `pt-r1zero` 那条路线时，seed 甚至可以很少，但必须让模型先产出能被解析、能拿到非零奖励分数（reward）的样本。如果是纯 SFT、不接 RL，seed 质量更是直接决定了有没有把正确算法写进监督。

挑 seed 时我会分开查几件事：难度是否落在当前学生的可学区间；终局答案是否可验证正确；每一步是否有效、有没有跳步；关键决策占总 token 的比例；语言和工具调用格式是否一致；还有教师模型（teacher）是不是远超学生能模仿的范围。「像不像 CoT」说明不了这些。

最有说服力的实验是固定总 token，只换 seed 的质量和难度，测三件事：冷启动后的可解析成功率、后续 RL 的学习曲线、分布外数据（OOD，即与训练数据明显不同的数据）泛化。比如做四组等 token 的对照：高质量难题、高质量易题、普通长 CoT、错但漂亮。先看冷启动的格式率，再接同一套 RL。如果只有高质量难题那组能让后续 reward 出现稳定方差，就说明 seed 的价值在于进入可区分的区域，跟字数无关。「错但漂亮」这组要专门放，它常比随机噪声更伤，因为它长得像正例。再加一组「对但没有关键转折」，用来证明密度本身有贡献，光答案对还不够。质量组用更少条数赢了数量组，结论才站得住；没有固定 token 和这些对照，数量组的输赢说明不了机制，可能只是换了计算量。

teacher-student gap 要单独看：把同一批 expert 轨迹按学生在该前缀上的困惑度分组统计。gap 过高的轨迹在 SFT 里像噪声，进了 RL 也给不出有用的中间状态，这时应该降难度、加脚手架，或者先做格式冷启动，再注入决策。

也别把「少量」神化。知识缺口类任务里，seed 仍要覆盖事实和工具用法，通用推理格式再漂亮也补不上没见过的 API；verifier 有漏洞的任务里，再干净的 CoT 也会把模型带向错误奖励。seed 只负责把策略送进可探索的区域，区域外的能力还得靠 RL、工具或更多针对性数据。`pt-cold-start-to-multistage-rl` 讲了为什么生产上仍要 cold start，它对 cold start 的要求就是可读、可解析、能拿到非零 reward，一次训成最终推理器不归它管。LIMA 式的「少即是多」也不能当普遍规律。把「几条神数据激活推理」和「必须百万条 CoT」讲成普遍科学，是对称的两种面试错误。

## 追问

**为什么数量组会输？**
它主要在拟合风格和错误中间步，后续 reward 很难把策略拉回正确算法。RL 需要的是能区分对错的差值，「看起来在思考」的边际提升帮不上忙。

**和 long-to-short 的数据过滤有什么关系？**
同一个原则：错的长推理过程不能进监督，见 `pt-long-to-short-reasoning`。seed 阶段引入的错误，可能在压缩和 RL 里继续保留甚至放大。

**没有 verifier 怎么挑 seed？**
用更强的独立 judge 加人工抽检，并单独标步骤错误，光看最终答案不够。judge 要固定版本，免得和后续 self-judge 回路搅在一起。

**冷启动之后还要不要混普通 CoT？**
格式和指令数据可以混，但别用低密度的长思考去稀释已经对齐的推理区域。冷启动的目标是可解析、能拿到 reward，把普通 CoT 堆满对它没有帮助。
