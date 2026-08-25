---
id: align-process-reward
section: alignment
order: 9
level: A
title: 对齐：过程奖励 vs 结果奖励，步骤标注噪声
quick: >-
  结果奖励只看最终对错，信用分配稀、长推理难学。过程奖励给中间步骤打分，密但标噪大：哪一步先错、等价正确路径会被误杀。能规则核验的中间态优先；开放 CoT 上 PRM 必须审计，且不能替代 outcome。
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

OpenAI 的 Let's Verify Step by Step 把过程监督推到数学题：人标每一步对错，训 PRM，推理时按步骤分搜。对齐 / reasoning 岗会问：为什么不直接用最终答案 0/1。答错成「过程分一定更强」会翻车——步骤标签噪声可以比稀疏 outcome 更毒。奖励被刷的风险见 `align-reward-hack`。

## 两种奖励在管什么

**结果奖励 (ORM / outcome)。** 一条轨迹一个标量：答案对、单测过、人偏好赢。实现简单，和可验证任务天然对齐。问题是信用分配：一百步推理最后错一位，前面九十九步可能是对的，outcome 全盘否定；最后蒙对，前面胡写也会得分。稀疏时 RL 方差大，探索难。

**过程奖励 (PRM / process)。** 对中间断言、子结论、工具参数、安全约束分别打分。密，能告诉模型「哪一步开始坏」。数学上可写成

$$
r = r^{\mathrm{out}} + \lambda\sum_k w_k s_k,
$$

$\lambda$ 过大就会刷中间分：步骤写得很漂亮、结论错。过程监督是 shaping 和诊断，**不能替代** 最终成功。面试这句话要先说。

OpenAI 的做法是：人看解题过程，标每一步是否正确，常以「第一步错误」为界后面都算错。用这些标签训 PRM，best-of-n 或搜索时用 PRM 而不是只看 ORM。他们发现过程监督比结果监督更数据高效，前提是标签质量高。换到开放域对话，没有逐步标准答案，这套不会自动成立。

能规则就规则：单测、类型检查、工具返回码、是否引用了检索到的文档。规则过程分比可学习 PRM 抗 hack。开放 CoT、没有 oracle 时才上 PRM，并且要对抗样本和人抽查。

## 步骤标注噪声从哪来

过程标签比 outcome 噪。常见几种：

- **第一步错误 vs 每步对错。** 只标 first error，后面步骤即使局部可救也当错，信用过惩。每步独立标，标注员会对「这步有没有用」分歧：跳步、换一种合法推导会被标错。
- **路径不唯一。** 同一道题有多条正确推理。强迫对齐到一条教师轨迹，会罚对的另一条路。噪声不是随机 flip，是系统性误杀等价策略。
- **不可验证的漂亮话。** 「让我们仔细想」这类句子没有真值，标成对就是在奖格式。PRM 会变成文风模型，和 RM 刷分同类。
- **标注员看不到环境。** Agent 轨迹里工具参数对不对，人如果不跑工具就会标错。过程信号要尽量来自环境可观察事件，而不是人读 CoT 的感觉。

噪声会进 PRM，再被 RL 放大：策略专攻 PRM 喜欢的步骤模板。这比 outcome 噪声更阴，因为每一步都有一个可 hack 的钩子。缓解：多标注员一致率、只在高一致步骤上训练、保留 outcome 为主信号、$\lambda$ 从小做消融。相关性和 false positive 要在成功 / 失败轨迹上算过，再接入 RL。

搜索时 PRM 当启发式、outcome 当终局门禁，比把过程分直接加成奖励更安全。过程违规可以早停，避免把坏状态滚完——这是诊断和线上拦截，仍然不是最终任务定义。

## 面试怎么选

可验证最终答案（数学、代码、游戏）先上 outcome / verifier。中间有可检查状态再加过程。开放聊天的「思维链好不好看」不要当过程奖励。数据贵时，过程标签用在 verifier 训练和筛选，而不是一上来稠密 RL。Let's Verify 的启示是：高质量步骤标签很强；启示不是「任何 CoT 打分都叫过程监督」。

## 追问

- **过程 RM 和规则过程分怎么选？** 能规则就规则；开放中间步骤才上 RM，并配审计和对抗样本。
- **能替代 outcome 吗？** 不能。主信号仍是最终成功，否则优化目标换了，模型会刷步骤。
- **步骤标错比最终答案标错更糟吗？** 常常是。每步一个钩子，RL 会拟合标注偏见；outcome 噪声至少还钉在任务成功上。
- **first-error 标注为什么常用？** 实现便宜、和「从哪坏」的诊断一致；代价是惩罚可修复的后续步骤，等价路径更易误杀。
