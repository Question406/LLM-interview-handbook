---
id: pt-rlvr-discovery-vs-reweighting
section: posttrain
order: 39
level: S
title: 如何实验区分 RLVR 学到了新推理路径，还是只把 base model 原有正确路径重加权？
quick: 先在 base model 上用大 K 测正确路径覆盖，再比较 RL 后路径是否已被 base rollout 包含；联合看 Pass@1 / Pass@K、路径相似度和跨分布泛化。只见 Pass@1 涨不能证明发现了新算法。
tags:
  - RLVR
  - Exploration
  - Evaluation
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-21
sources:
  - title: Does RL Really Incentivize Reasoning Beyond the Base Model?
    url: https://arxiv.org/abs/2504.13837
    type: primary
  - title: DeepSeek-R1
    url: https://arxiv.org/abs/2501.12948
    type: primary
---

RLVR 之后 `pass@1` 大涨，不等于模型发明了 base 不会的算法。一种机制是 discovery：出现了 base 在合理采样预算下几乎采不到的新成功路径。另一种是 reweighting：base 的长尾里本来就有正确轨迹，RL 只是把它们的概率从「偶尔」抬到「默认」。`pt-r1zero` 讲 search-selection-amplification 的正反馈；本题要你设计实验，避免把 amplification 误称为创造。这块容易直接答成只看 `pass@1`，或只看平均 CoT 变长。

## 先画 base 的可达成功集

对每道题，用与训练一致的 prompt、`temperature`、token budget 和 verifier，在 base policy 上采很大的 $K$，得到它本来能触及的正确答案集合，以及过程模式集合（关键引理、代码骨架、工具调用序）。再在同一协议下采 RL policy 的成功轨迹，问两条 containment：

- **answer-level**：RL 的正确答案是否已在 base 的成功答案集里。
- **trace-level**：RL 的成功过程是否落在 base 成功 trace 的近邻（编辑距离、程序等价、关键步骤集合）。

若大量新成功只是原集合中更常被采样，主结论是 reweighting。`pass@1` 升、`pass@k` 持平，是这条故事的常见表象，但不能单独定案，还要排除解码变尖把长尾采没了。评测协议见 `pt-rlvr-reasoning-eval`。过程近邻要预先定义：关键等式集合、函数调用序列、证明所用引理，而不是整段文本的 embedding 相似，后者会把换了一种套话判成新算法。

## 控制变量与跨分布

必须锁 prompt、温度、长度、$K$、verifier。否则「新路径」可能只是换了采样。比较时把 base 的计算预算给足：用过小的 $K$ 会把 base 不会的假象造出来。更稳的做法是画 base 的 $K$-coverage 曲线，直到边际覆盖接近平坦，再谈 RL 是否越出该平台。

还要在与训练 reward 不同的分布上评估：新题型、更难组合、不同形式化。真实 discovery 更可能带来结构性泛化；纯 reweighting 常在原任务 `pass@1` 好看、换分布后回到 base 的覆盖上限。注意：泛化也不是充分条件，数据泄漏或更强的格式先验也能造成「看起来会迁移」。反向检查同样有用：若 OOD 升了但 containment 仍高，可能是 base 本来就会、只是默认解码不够敢。

路径相似度要用过程特征，不要只比最终数字。两个证明答案相同、引理集合不同，才值得称为新路径。代码题可用「通过的是哪些测例 + 核心循环结构」做等价，避免把变量重命名当成 discovery。

## 重加权仍然有产品价值

这个实验不是为了否定 reweighting。把稀有正确策略变成 `pass@1` 可用能力，本身就是推理产品要的东西；`pt-r1zero` 的 search-selection-amplification 很大一部分就是在做这件事。需要禁止的是话术：把 support 内的概率重排说成「从零创造新 reasoning」。对科研声称，应同时报 base 大 $K$ 覆盖、RL containment、以及 OOD。对工程，reweighting 够用就够用，不必强行讲 discovery。

若 containment 很高且 OOD 不动，下一步通常是改善 seed / 探索 / 环境，而不是再堆同分布 RL 步数。探索不足时，温度、熵奖励、课程难度或 `pt-self-generated-curriculum` 比再跑同样的 RLVR 更相关。白板结论允许是混合的：一部分题是 reweighting，一小部分题出现了越出 base 覆盖的过程，按题切片报，不要用一个形容词概括整个 run。

报告模板：base $K$-coverage 是否已平台、RL 成功的 answer / trace containment、OOD 是否越出原覆盖。三句齐才能说 discovery；只见 `pass@1` 只够说「默认更好用」。

## 追问

- **多大的 $K$ 才算「base 不会」？** 没有魔法数。应画 $K$-coverage 曲线，看 RL 成功是否仍落在曲线已饱和的集合外。曲线还在涨就下结论，是把计算不足写成了 discovery。
- **答案对、过程不同算 discovery 吗？** 算候选。要用过程等价判定（引理集、调用序、核心循环），并排除只是换了叙述顺序或变量名。embedding 相似不能当证据。
- **和 Pass@K 误判有何关系？** `pt-rlvr-reasoning-eval` 防止把覆盖 / 选择 / 轨迹质量混为一谈；本题在协议正确后再问新路径来源。两题应共用温度、长度和 verifier。
- **没有过程 verifier 还能做吗？** 能做 answer-level containment 和 OOD，但会低估「同答案、新算法」。结论要写弱，并明确这是下界而不是点估计。
