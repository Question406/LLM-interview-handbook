---
id: pt-rlvr-reasoning-eval
section: posttrain
order: 38
level: S
title: 为什么 Pass@K 可能错误判断 RLVR 只是压缩多样性？如何评测推理本身正确而非只看最终答案？
quick: >-
  Pass@K 只问 K 个候选里有没有正确最终答案，把覆盖率、选择器和轨迹质量揉在一起，所以 pass@1 升、pass@K 不动既可能是重加权，也可能是
  decoding 变尖。要联合报 Pass@1、Pass@K、正确轨迹率、过程验证器（verifier）分数和独立 trace audit，并固定
  sampling 温度和 K。
tags:
  - RLVR
  - Evaluation
  - Reasoning
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-21T00:00:00.000Z
sources:
  - title: RLVR Implicitly Incentivizes Correct Reasoning
    url: 'https://arxiv.org/abs/2506.14245'
    type: primary
  - title: Does RL Really Incentivize Reasoning Beyond the Base Model?
    url: 'https://arxiv.org/abs/2504.13837'
    type: primary
---

Pass@K 会误判，是因为它只问「$K$ 条独立样本里有没有出现过正确最终答案」，把三件事揉在了一起：生成器的覆盖率、有没有用上选择器、轨迹本身合不合理。所以看到 RL 后 `pass@1` 升、`pass@k` 不动，不能直接断言「只是压缩多样性」；`pass@k` 上涨也不能直接说「推理变强」。两种都可能，单个指标区分不了，要把指标拆开、单独评过程，并锁死评测协议。这和 `pt-rlvr-discovery-vs-reweighting`、`pt-best-of-n-decomposition` 要拆的是同一类问题。

RLVR 用可执行或形式化奖励优化最终答案，评测却常常只报 `pass@1` / `pass@k`。同一题、同一 sampling 协议下，我会拆成这几列：

| 指标 | 实际在问 |
| --- | --- |
| `pass@1` | 默认 decoding 下答案是否常对 |
| `pass@k` | 大 sampling 覆盖里有没有正确答案 |
| 正确轨迹率 | 最终对的样本中，关键中间断言是否也成立 |
| 验证器（verifier） 分 | 过程检查器是否接受这条 trace |
| 独立 audit | 人 / 另一套 oracle 是否同意 |

`pass@1` 升、`pass@k` 持平，可能是把稀有的正确模式重加权了，也可能是 `temperature` / `top_p` 变尖、长度截断更狠，把长尾的正确解采没了。`pass@k` 升、`pass@1` 不动，常常是覆盖变宽但缺一个可靠的选择器，或者只是把 $K$ 和温度调大了。`pt-best-of-n-decomposition` 里 coverage 和候选选择器（selector）之间的 gap，在这里变成了评测协议问题。`pass@k` 的估计量也要写清：是「采恰好 $K$ 条看有没有对的」，还是用更大的 $n$ 算 unbiased estimate，两种数字不能混在一条曲线上。majority vote、verifier rerank、Best-of-N 都是 selector，必须单独成列，别塞进同一个 `pass@k`。

再说怎么评推理本身。数学、代码、形式证明这类能检查的任务，每条 trace 至少标三件事：最终是否正确、关键中间断言是否正确、有没有无效跳步或和答案矛盾的步骤。过程标签别和训练奖励分数（reward）共用一套 checker，同一个漏洞会被训练和评测一起吃掉，看起来「过程也更好了」。独立 audit 的抽样按「最终对 / 最终错 / 高 reward」分层，否则只会看到已经过了训练 checker 的漂亮子集。正确轨迹率建议报两个分母：所有样本里过程也对的比例，这个才和 `pass@1` 可比；「最终已对」的子集里过程也对的比例，专门抓答案对、推理不成立的情况。

没法完全形式化的任务，用独立 judge 加人工抽检，rubric 固定：有没有引用不存在的引理、有没有先有答案再补理由、工具输出有没有被如实转述。报告 trace-level 指标时写清 oracle 是谁、有没有看过最终答案、能不能用工具、一次读多少 token。`pt-cot-monitorability-regression` 关心监控器能不能抓风险，这题关心能力评测会不会把碰巧答对当成推理进步。两边都怕 unfaithful chain of thought（CoT，即分步推理过程），只是标签不同，一个漏的是风险，一个虚高的是能力。

然后是协议。很多所谓「推理改善」其实是协议换了。至少固定 `temperature`、`top_p`、最大生成长度、$K$、有没有 majority vote / verifier rerank，以及总 token 预算。比较 RL 前后时，base 和 RL policy 用同一套 decoding，一边 greedy、一边大 $K$ sampling，结论作废。长度上限尤其容易作弊：RL 后模型写得更长，同一个 `max_tokens` 下 base 被截断、RL 写完了，看上去像推理进步。还要报计算 normalization 的数字：同样 token 预算下的 `pass@1`、同样实际耗时下的成功率，否则多 sampling 带来的碰巧命中会被写成能力。`pt-r1zero` 说明可验证 RL 能放大成功行为，这里要证明放大的是正确推理，排除「更会碰答案」和「更会写过 checker 的格式」这两种可能。

举两个例子。一道竞赛题，base 在较大 $K$ 时偶尔写出正确解、`pass@1` 很低；RL 后 greedy 常对、`pass@k` 几乎不动。这可能是 reweighting，也可能是多样性塌缩。加两项检查就能分开：看成功轨迹是否已经被 base 的大 $K$ sampling 轨迹（rollout）覆盖（见 `pt-rlvr-discovery-vs-reweighting`）；再抽最终正确的样本做过程 audit，如果大量「答案对、关键不等式跳步」，就说明 `pass@*` 在夸大推理质量。另一个反方向的例子：`pass@k` 涨了，正确轨迹率却在降，模型学会了多写几种能碰对最终数字的捷径，覆盖变宽、推理变差。只报 `pass@k` 的话，这会被读成「RL 发现了更多解法」。覆盖、选择、过程正确三列数字缺一列，就没法定性。

## 追问

**majority vote 够不够？**
不够。投票只聚合最终答案，错的主流解会压过稀有正解，也不检查中间步骤。票数高只说明多数样本同意同一个答案，推理成不成立它不管。

**过程 verifier 和训练奖励能共用吗？**
不能当唯一的评测。共用会把钻奖励规则空子的行为洗成「过程分也涨了」。至少换检查器、换规则粒度，或者加人工抽检。

**Pass@K 怎么报才不误导？**
同时报 `pass@1`、若干 $K$ 的曲线、正确轨迹率和协议（温度、长度、预算），并声明有没有 selector，估计量是「恰好 $K$ 条」还是更大 $n$ 的 unbiased estimate。

**和 discovery / reweighting 那题怎么分工？**
这题先保证测的是推理，排除碰巧答对；`pt-rlvr-discovery-vs-reweighting` 再问新路径是不是 base 在大 $K$ 下本来就会。两题共用同一套锁死的协议，否则互相不可比。
