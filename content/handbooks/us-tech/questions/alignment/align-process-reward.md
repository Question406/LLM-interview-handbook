---
id: align-process-reward
section: alignment
order: 9
level: A
title: 对齐：过程奖励 vs 结果奖励，步骤标注噪声
quick: "过程奖励能指出推理从哪一步开始出错，但最终成功仍应是主信号。我会先用最终答案或单测给 outcome 奖励，再加入能可靠检查的中间状态；步骤标签有噪声时，稠密奖励也会反复强化错误。"
tags:
  - OpenAI
  - Process Reward
  - RLHF
  - Alignment
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-23
sources:
  - title: Let's Verify Step by Step
    url: https://arxiv.org/abs/2305.20050
    type: primary
  - title: Training language models to follow instructions with human feedback
    url: https://arxiv.org/abs/2203.02155
    type: primary
  - title: Direct Preference Optimization
    url: https://arxiv.org/abs/2305.18290
    type: primary
---

过程奖励适合告诉模型「从哪一步开始错了」，最终成功仍要作为主信号。例如一百步推理最后算错一位，单个结果分会把整条轨迹判错，无法区分前面哪些步骤是对的。过程监督能提供更细的信号，但每步标签若不可靠，也会把错误放大。

## 两种奖励在管什么

结果奖励（ORM / outcome）给一条轨迹一个标量，最简单的是最终答案 0/1，可以来自答案对错、单测是否通过或人类偏好。它实现简单，容易和可验证任务对齐；但最终蒙对时，错误过程也会得分。这类信号稀疏时，强化学习（RL）的方差大，探索也更难。

过程奖励（PRM / process）分别评价中间断言、子结论、工具参数或安全约束，再和结果奖励合并：

$$
r = r^{\mathrm{out}} + \lambda\sum_k w_k s_k,
$$

这里 $\lambda$ 控制过程分的权重，$w_k s_k$ 是各步骤的加权得分。$\lambda$ 太大，模型可能靠漂亮步骤得高分，最后结论却错了。因此过程分用于 shaping 和诊断，最终是否成功还要单独检查。

OpenAI 的做法是：人看解题过程，标每一步是否正确，常以「第一步错误」为界后面都算错。用这些标签训 PRM，best-of-n 或搜索时用 PRM 而不是只看 ORM。他们发现过程监督比结果监督更数据高效，前提是标签质量高。换到开放域对话，没有逐步标准答案，这套不会自动成立。

能直接检查的中间状态，我会先用单测、类型检查、工具返回码或引用核对。这些规则过程分相对更抗 hack。开放 CoT 没有 oracle 时才考虑学习 PRM，并配合对抗样本和人工抽查。

## 步骤标注噪声从哪来

过程标签可能比 outcome 更嘈杂，原因主要在标注标准和观察条件：

- **第一步错误 vs 每步对错。** 只标 first error，后面步骤即使局部可救也当错，信用过惩。每步独立标，标注员会对「这步有没有用」分歧：跳步、换一种合法推导会被标错。
- **路径不唯一。** 同一道题有多条正确推理。强迫对齐到一条教师轨迹，会罚对的另一条路。噪声不是随机 flip，是系统性误杀等价策略。
- **不可验证的漂亮话。** 「让我们仔细想」这类句子没有真值，标成对就是在奖格式。PRM 会变成文风模型，和 奖励模型（RM） 刷分同类。
- **标注员看不到环境。** Agent 轨迹里工具参数对不对，人如果不跑工具就会标错。过程信号要尽量来自环境可观察事件，而不是人读 CoT 的感觉。

噪声会进 PRM，再被 RL 放大：策略专攻 PRM 喜欢的步骤模板。这比 outcome 噪声更阴，因为每一步都有一个可 hack 的钩子。缓解：多标注员一致率、只在高一致步骤上训练、保留 outcome 为主信号、$\lambda$ 从小做消融。相关性和 false positive 要在成功 / 失败轨迹上算过，再接入 RL。

搜索时 PRM 当启发式、outcome 当终局门禁，比把过程分直接加成奖励更安全。过程违规可以早停，避免把坏状态滚完：这是诊断和线上拦截，仍然不是最终任务定义。

数学、代码和游戏这类最终结果可验证的任务，我会先用 outcome / 验证器（verifier），再给可检查的中间状态加过程信号。开放聊天里只评「思维链好不好看」，容易奖励文风。标注贵时，也可以先把过程标签用于 verifier 训练和筛选。Let's Verify 的效果依赖高质量步骤标签，不能直接推广成任意 CoT 打分都有效。

相关：`align-reward-hack`。

## 追问

**过程 RM 和规则过程分怎么选？**
能规则就规则；开放中间步骤才上 RM，并配审计和对抗样本。
**能替代 outcome 吗？**
不能。主信号仍是最终成功，否则优化目标换了，模型会通过增加无用步骤获取奖励。
**步骤标错比最终答案标错更糟吗？**
常常是。每步一个钩子，RL 会拟合标注偏见；outcome 噪声至少还钉在任务成功上。
**first-error 标注为什么常用？**
实现便宜、和「从哪坏」的诊断一致；代价是惩罚可修复的后续步骤，等价路径更易误杀。
