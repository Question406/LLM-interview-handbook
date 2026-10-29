---
id: pt-rlvr-discovery-vs-reweighting
section: posttrain
order: 39
level: S
title: 如何实验区分 RLVR 学到了新推理路径，还是只把 base model 原有正确路径重加权？
quick: >-
  先在 base model 上用和训练一致的协议、足够大的 K 画出它本来能到达的正确路径，再看 RL 后的成功答案和过程是否已被 base
  sampling 轨迹（rollout）包含，同时看跨分布泛化。只见 Pass@1 涨，只能说默认 decoding 更好用，证明不了发现了新算法。
tags:
  - RLVR
  - Exploration
  - Evaluation
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-21T00:00:00.000Z
sources:
  - title: Does RL Really Incentivize Reasoning Beyond the Base Model?
    url: 'https://arxiv.org/abs/2504.13837'
    type: primary
  - title: DeepSeek-R1
    url: 'https://arxiv.org/abs/2501.12948'
    type: primary
---

实验思路是先把 base 本来能到达的成功集合画出来，再看 RL 后的成功轨迹有没有越出去。base 在足够大的 $K$ 下就能采到、只是概率低的，算 reweighting；base 采到平台也采不到的新成功路径，才算 discovery 的候选。只看 `pass@1`，或者只看 chain of thought（CoT）平均变长，两者区分不了。

这么做是因为两种机制都会让 `pass@1` 大涨。比如一道题，base 在大 $K$ 下偶尔写出正确解，RLVR 之后 greedy 也常对了：可能是 RL 出现了 base 在合理 sampling 预算下几乎采不到的新路径，也可能只是把长尾里本来就有的正确轨迹从「偶尔」抬到了「默认」。`pt-r1zero` 讲的 search-selection-amplification 就是后一种正反馈，这题要设计实验，免得把 amplification 误称为创造。

第一步，用和训练一致的 prompt、`temperature`、token 预算和验证器（verifier），在 base policy 上采很大的 $K$，得到它本来能触及的正确答案集合，以及过程模式集合，比如关键引理、代码骨架、工具调用顺序。$K$ 要给足，太小会凭空造出「base 不会」的假象；更稳的是画 base 的 $K$-coverage 曲线，直到边际覆盖接近平坦，再谈 RL 有没有越出这个平台。

第二步，同一协议下采 RL policy 的成功轨迹，查两种包含关系。answer-level 看 RL 的正确答案是否已在 base 的成功答案集里；trace-level 看 RL 的成功过程是否落在 base 成功 trace 的近邻里，近邻可以用编辑距离、程序等价或关键步骤集合判断。近邻要预先定义成过程特征，比如关键等式集合、函数调用序列、证明用到的引理，整段文本的 embedding 相似度会把换了一种套话判成新算法。两个证明答案相同、引理集合不同，才值得叫新路径；代码题可以用「通过的是哪些测例加核心循环结构」判等价，免得把变量重命名当成 discovery。大量新成功只是原集合里被采得更勤，主结论就是 reweighting。`pass@1` 升、`pass@k` 持平是这种情况的常见表象，但单靠它定不了案，还要排除 decoding 变尖、把长尾采没了，评测协议见 `pt-rlvr-reasoning-eval`。整个过程要锁死 prompt、温度、长度、$K$ 和 verifier，否则「新路径」可能只是换了 sampling。

第三步，在和训练奖励分数（reward）不同的分布上评估：新题型、更难的组合、不同的形式化。真正的 discovery 更可能带来结构性泛化，纯 reweighting 常常是原任务 `pass@1` 好看、换了分布又回到 base 的覆盖上限。泛化也不是充分条件，数据泄漏或更强的格式先验也能造出「看起来会迁移」。反过来查也有用：out-of-distribution 数据（OOD，即与训练数据明显不同的数据）上涨了但 containment 仍然高，可能是 base 本来就会、只是默认 decoding 不够敢。

结论可以是混合的：一部分题是 reweighting，一小部分题出现了越出 base 覆盖的过程，按题切片报，别用一个形容词概括整个 run。另外，reweighting 本身有产品价值，把稀有的正确策略变成 `pass@1` 可用的能力，正是推理产品要的东西。要避免的是话术，把 support 内的概率重排说成「从零创造新 reasoning」。做科研声称时，base 大 $K$ 覆盖、RL containment 和 OOD 三样都要报；做工程时 reweighting 够用就够用，不必硬讲 discovery。containment 很高、OOD 不动时，下一步通常是改善 seed、探索或环境，温度、entropy bonus、课程难度或 `pt-self-generated-curriculum` 比再堆同分布的 RLVR 步数更相关。

## 追问

**多大的 $K$ 才算「base 不会」？**
没有魔法数。画 $K$-coverage 曲线，看 RL 的成功是不是落在曲线已饱和的集合之外。曲线还在涨就下结论，是把计算不足写成了 discovery。

**答案对、过程不同，算 discovery 吗？**
算候选。要用过程等价来判（引理集、调用序、核心循环），排除只是换了叙述顺序或变量名。embedding 相似不能当证据。

**和 Pass@K 误判那题怎么分工？**
`pt-rlvr-reasoning-eval` 防止把覆盖、选择和轨迹质量混在一起；这题在协议正确之后再问新路径从哪来。两题要共用温度、长度和 verifier。

**没有过程 verifier 还能做吗？**
能做 answer-level containment 和 OOD，但会低估「同答案、新算法」的情况。结论要写弱，并说明这是下界，算不上 point estimate。
