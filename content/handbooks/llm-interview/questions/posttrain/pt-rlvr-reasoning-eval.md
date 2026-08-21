---
id: pt-rlvr-reasoning-eval
section: posttrain
order: 38
level: S
title: 为什么 Pass@K 可能错误判断 RLVR 只是压缩多样性？如何评测推理本身正确而非只看最终答案？
quick: Pass@K 只问候选里是否出现正确最终答案，混淆覆盖率、选择器和轨迹质量。应联合报告 Pass@1、Pass@K、正确轨迹率、过程 verifier 分数与独立 trace audit，并固定采样温度和 K。
tags:
  - RLVR
  - Evaluation
  - Reasoning
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-19
sources:
  - title: RLVR Implicitly Incentivizes Correct Reasoning
    url: https://arxiv.org/abs/2506.14245
    type: primary
  - title: Does RL Really Incentivize Reasoning Beyond the Base Model?
    url: https://arxiv.org/abs/2504.13837
    type: primary
---

RLVR 用可执行或形式化奖励优化最终答案，评测却常只报 `pass@1` / `pass@k`。`pass@k` 问的是「$K$ 条独立样本里是否出现过正确最终答案」，它把生成器覆盖率、选择器是否用上、轨迹本身是否合理三件事揉在一起。面试陷阱是：看到 RL 后 `pass@1` 升、`pass@k` 不动，就断言「只是压缩多样性」；或把 `pass@k` 上涨说成「推理变强」。两者都可能，单指标无法区分。这和 `pt-rlvr-discovery-vs-reweighting`、`pt-best-of-n-decomposition` 要拆的是同一类问题。

## 指标各在量什么

同一题、同一采样协议下，把结果拆开：

| 指标 | 实际在问 |
| --- | --- |
| `pass@1` | 默认解码下答案是否常对 |
| `pass@k` | 大采样覆盖里有没有正确答案 |
| 正确轨迹率 | 最终对的样本中，关键中间断言是否也成立 |
| verifier 分 | 过程检查器是否接受这条 trace |
| 独立 audit | 人 / 另一套 oracle 是否同意 |

`pass@1` 升而 `pass@k` 持平，既可以是把稀有正确模式重加权，也可以是 `temperature` / `top_p` 变尖、长度截断更狠，把长尾正确解采没了。`pass@k` 升而 `pass@1` 不动，常常是覆盖变宽但缺少可靠选择器，或只是把 $K$ 和温度调大了。`pt-best-of-n-decomposition` 里的 coverage vs selector gap，在这里变成评测协议问题。

`pass@k` 本身还要写清估计量：是「采恰好 $K$ 条看有没有对的」，还是用更大 $n$ 再算无偏估计。两种数字不能混着画曲线。majority vote、verifier rerank、Best-of-N 都是 selector，必须单独成列，不能塞进同一个 `pass@k`。

## 怎么评「推理本身」

对能检查的任务（数学、代码、形式证明），每条 trace 至少标三件事：最终正确性、关键中间断言正确性、是否存在无效跳步或与答案矛盾的步骤。过程标签不要和训练 reward 共用同一套 checker——同一漏洞会被训练和评测同时吃掉，看起来「过程也更好了」。独立 audit 的抽样要按「最终对 / 最终错 / 高 reward」分层，否则只会看到已经过训练 checker 的漂亮子集。

对不可完全形式化的任务，用独立 judge 加人工抽检，并固定 rubric：是否引用不存在的引理、是否事后编造理由（先有答案再补步骤）、工具输出是否被诚实转述。报告 trace-level 指标时写清：oracle 是谁、是否看过最终答案、是否允许工具、一次看多少 token。`pt-cot-monitorability-regression` 关心监控器能不能抓风险；本题关心能力评测会不会把「碰巧答对」当成推理进步。两者都怕 unfaithful CoT，但标签不同：一个是风险漏检，一个是能力虚高。

正确轨迹率建议同时报两个分母：所有样本中过程也对的比例，以及「最终已对」子集中过程也对的比例。后者专门抓「答案对、推理假」；前者才和 `pass@1` 可比。

## 必须锁死的协议

所谓「推理改善」经常是协议换了。至少固定 `temperature`、`top_p`、最大生成长度、$K$、是否 majority vote / verifier rerank，以及总 token 预算。比较 RL 前后时，base 与 RL policy 用同一套解码；一边 greedy、一边大 $K$ 采样，结论作废。长度上限尤其容易作弊：RL 后模型写得更长，同一 `max_tokens` 下 base 被截断、RL 写完，看起来像推理进步。

还要报计算归一化数字：同样 token 预算下的 `pass@1`、同样墙钟下的成功率。否则多采样带来的碰巧命中会被写成能力。`pt-r1zero` 说明可验证 RL 能放大成功行为；本题要求证明放大的是正确推理，而不是更会碰答案或更会写过 checker 的格式。

## 白板小例子

一道竞赛题，base 在较大 $K$ 时偶尔写出正确解但 `pass@1` 很低；RL 后 greedy 常对、`pass@k` 几乎不动。这可能是 reweighting，也可能是多样性塌缩。补两刀就能分开：看成功轨迹是否已被 base 的大 $K$ rollout 覆盖（见 `pt-rlvr-discovery-vs-reweighting`）；再抽最终正确的样本做过程 audit——若大量「答案对、关键不等式跳步」，`pass@*` 在夸大推理质量。

另一类反例：`pass@k` 涨了，但正确轨迹率下降。模型学会多写几种能碰对最终数字的捷径，覆盖变宽、推理变差。这时若只报 `pass@k`，会被解读成「RL 发现了更多解法」。白板结论应写成：覆盖、选择、过程正确，三列数字缺一就无法定性。

面试收尾时把三列数字写在同一张表：覆盖（`pass@k`）、默认命中（`pass@1`）、过程正确（正确轨迹率）。缺一列就拒绝下结论。

## 追问

- **为什么不能只用 majority vote？** 投票只聚合最终答案，错的主流解会压过稀有正解；它也不检查中间步骤。票数高只说明「多数样本同意一个答案」，不说明推理成立。
- **过程 verifier 和训练奖励能共用吗？** 不能当唯一评测。共用会把 reward hacking 洗成「过程分也涨了」。至少换检查器、换规则粒度，或加人抽检。
- **Pass@K 该怎么报才不误导？** 同时报 `pass@1`、若干 $K$ 的曲线、正确轨迹率和协议（温度、长度、预算），并声明有没有 selector。估计量是「恰好 $K$ 条」还是更大 $n$ 的无偏估计，也要写清。
- **和 discovery / reweighting 题怎么分工？** 本题先保证「测的是推理」而不是碰巧碰对答案；`pt-rlvr-discovery-vs-reweighting` 再问新路径是不是 base 在大 $K$ 下本来就会。两题共用同一套锁死协议，否则互相不可比。
