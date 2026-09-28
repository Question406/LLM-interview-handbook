---
id: align-weak-strong
section: alignment
order: 26
level: S
title: 对齐：weak-to-strong——监督者弱于被监督模型
quick: >-
  人 / 小模型给的标签盖不住大模型已经会的能力。朴素 SFT 会把弱监督者的错和偏见也学走。OpenAI 的
  weak-to-strong 问的是：强模型能否从弱标签里泛化出更强行为。这是可扩展监督，不是蒸馏的反义词。
tags:
  - OpenAI
  - Alignment
  - Oversight
  - Generalization
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-23
sources:
  - title: Weak-to-Strong Generalization — Eliciting Strong Capabilities With Weak Supervision
    url: https://arxiv.org/abs/2312.09390
    type: primary
  - title: Weak-to-strong generalization (OpenAI)
    url: https://openai.com/index/weak-to-strong-generalization/
    type: primary
  - title: Constitutional AI — Harmlessness from AI Feedback
    url: https://arxiv.org/abs/2212.08073
    type: primary
---

OpenAI 2023 年那篇 weak-to-strong 是对齐岗的公开必读之一：用 GPT-2 级监督者标数据，训 GPT-4 级学生，看学生能不能超过老师。评委要听的是可扩展监督：未来模型强过所有人标注员时，朴素 RLHF 的标签从哪来。辩论 / 递归监督是另一条公开路线，见 `align-debate`；CAI 是工程上把人挪到原则层，见 `align-cai`。

## 朴素拟合弱标签会怎样

设弱监督者 $w$ 在 $x$ 上给出 $\tilde y$ 或偏好，强模型 $\pi$ 做 SFT / 分类。若 $\tilde y$ 系统错（过时知识、谄媚、不会的题乱猜），$\pi$ 有足够容量去**模仿错误**，而不是「自动纠正老师」。这和过拟合训练集还不一样：分布内老师就错，学生学到的是老师的决策面。

OpenAI 报告的现象是：有一些任务上，强模型用弱标签仍能明显超过弱老师（他们称为 weak-to-strong generalization），但通常**到不了**用强标签能达到的上限。中间有 gap。面试不要说「大模型会自己纠正标注」。要说：额外容量有时能恢复被弱标签压住的预训练能力；这是经验现象，不是定理。

方法上他们讨论过：在弱标签之外加辅助损失、用学生自己的置信度、不让学生把老师的错误当硬目标。工程直觉是 **不要把 $\tilde y$ 当 one-hot 真理**。软标签、保留拒绝选项、只在老师高置信切片上监督，都是同一类补丁。

```python
def weak_sft_mask(weak_conf, thresh):
    # 只在弱监督者自己有把握的切片上给硬标签；其余当无监督 / 辅助目标
    return weak_conf >= thresh
```

上面伪代码里的阈值本身会被刷：老师对谄媚特别自信，你就在谄媚切片上训得最狠，见 `align-sycophancy`。所以还要对着**强金标 held-out**（研究里才有）看 gap；生产里没有强金标时，这个实验做不全，要承认。

## 和 RM、CAI、辩论怎么摆

RLHF 的 RM 是弱监督者的蒸馏：人比未来模型弱，RM 更弱。RM over-optimization 是「强策略钻弱判官」，见 `align-overopt-rm`。weak-to-strong 是「强学生能不能从弱老师那里长出真能力」。一个是钻缝，一个是泛化。面试别合成一句「都是师生不匹配」。

CAI 假设原则比逐条标签更容易由人维护；它不解决「原则也覆盖不了超人类领域」。辩论假设弱裁判看交叉质询比看最终答案更容易；它把 weak-to-strong 从拟合标签变成拟合**过程可检查性**。RFT / RLVR 走另一条：能验证就不靠弱老师的品味，见 `align-rft`。

失败模式：学生学会预测老师会怎么标，而不是世界状态（迎合弱 judge）；用 LLM-as-judge 当弱老师再 RL，把 gap 藏进 Arena 分，见 `align-llm-judge`。研究叙事要落到「我们缺哪一种金标」，不要承诺已经解决超人类对齐。

我会画两根柱：弱老师准确率、强学生在弱标签上的准确率、强标签天花板。naive SFT 贴着第一根；weak-to-strong 介于第二和第三之间。评委追问「为什么能超过老师」时，答预训练里已经有更强表征，弱标签有时只是在引出而不是在注入能力——这是假说，要用 held-out 强金标证伪。没有这根天花板柱，就不要把线上 RM 分当证明。

和安全税叠：弱监督者过度拒绝，学生会把拒答学成默认，见 `align-over-refuse`、`align-safety-tax`。helpful 切片和 harmless 切片要分开看 gap。

OpenAI 岗可能把这篇当「人标注盖不住时你怎么办」的开口，不必背实验表。要能说：naive 拟合会模仿弱错误；有时能引出更强能力；gap 还在；生产用可验证奖励和原则补。

## 追问

- **这是蒸馏吗？** 蒸馏通常是强教师弱学生。这里教师更弱，问的是学生会不会被教师拖下水。
- **没有强金标怎么知道泛化了？** 实验室用人为的能力差当代理。生产只能看下游任务和人抽查，承认代理失效风险。
- **和过程监督的关系？** 若人只能检查步骤不能检查终局，过程标签仍是弱监督，噪声见 `align-process-reward`。
- **面试怎么收？** 说清问题（监督者盖不住），说清 naive SFT 的失败，说清论文是部分泛化而不是关闭问题。
- **弱标签加 RL 是不是更糟？** 常常是。RL 会放大老师的偏见，变成迎合弱 judge。能验证就走 RLVR，见 `align-rft`。
