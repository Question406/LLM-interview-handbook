---
id: align-weak-strong
section: alignment
order: 26
level: S
title: 对齐：weak-to-strong——监督者弱于被监督模型
quick: "Weak-to-strong 问的是：强模型能否从弱监督者的标签里引出已有能力，表现超过老师。直接拟合弱标签也会学走老师的错误，所以要用辅助目标、置信度筛选等方法减轻影响，并用独立强金标衡量还剩多少差距。"
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

Weak-to-strong 研究强学生能不能从弱老师的标签里学出超过老师的表现。OpenAI 2023 年的实验用 GPT-2 级监督者标数据，训练 GPT-4 级学生，模拟未来模型强于人类标注员时的监督问题。关键是引出学生预训练中已有的能力，同时少学老师的系统性错误。

## 为什么强学生也会学错

设弱监督者 $w$ 在 $x$ 上给出 $\tilde y$ 或偏好，强模型 $\pi$ 做 监督微调（SFT） / 分类。若 $\tilde y$ 系统错（过时知识、谄媚、不会的题乱猜），$\pi$ 有足够容量去**模仿错误**，而不是「自动纠正老师」。这和过拟合训练集还不一样：分布内老师就错，学生学到的是老师的决策面。

OpenAI 报告的现象是：有一些任务上，强模型用弱标签仍能明显超过弱老师（他们称为 weak-to-strong generalization），但通常**到不了**用强标签能达到的上限。中间有 gap。这说明额外容量有时能恢复被弱标签压住的预训练能力，但它是经验现象，没有保证模型会自动纠正标签。

方法上他们讨论过：在弱标签之外加辅助损失、用学生自己的置信度、不让学生把老师的错误当硬目标。实现时就要降低把 $\tilde y$ 当硬 one-hot 目标的风险。软标签、保留拒绝选项、只在老师高置信切片上监督，都是同一类补丁。

```python
def weak_sft_mask(weak_conf, thresh):
    # 只在弱监督者自己有把握的切片上给硬标签；其余当无监督 / 辅助目标
    return weak_conf >= thresh
```

上面伪代码里的阈值本身会被刷：老师对谄媚特别自信，你就在谄媚切片上训得最狠，见 `align-sycophancy`。所以还要对着**强金标 held-out**（研究里才有）看 gap；生产里没有强金标时，这个实验做不全，要承认。

## 怎么验证，以及其他监督方式能补什么

RLHF 的 RM 是弱监督者的蒸馏：人比未来模型弱，RM 更弱。RM over-optimization 是「强策略钻弱判官」，见 `align-overopt-rm`。weak-to-strong 是「强学生能不能从弱老师那里长出真能力」。前者关注利用监督者的漏洞，后者关注从弱监督中泛化。两者都涉及能力差距，但评测的问题不同。

CAI 假设原则比逐条标签更容易由人维护；它不解决「原则也覆盖不了超人类领域」。辩论假设弱裁判看交叉质询比看最终答案更容易；它把 weak-to-strong 从拟合标签变成拟合**过程可检查性**。RFT / 基于可验证奖励的强化学习（RLVR） 走另一条：能验证就不靠弱老师的品味，见 `align-rft`。

失败模式：学生学会预测老师会怎么标，而不是世界状态（迎合弱 judge）；用 LLM-as-judge 当弱老师再 强化学习（RL），把 gap 藏进 Arena 分，见 `align-llm-judge`。因此要说清缺少哪一种金标，实验能支持到什么范围。

验证时我会比较弱老师的准确率、强学生接受弱标签训练后的准确率，以及强标签训练的上限。naive SFT 可能贴近老师，成功的弱到强泛化则表现为学生超过老师、但仍未达到强标签上限。一个解释是预训练已有更强表征，弱标签有时把能力引了出来；这个假说要用 held-out 强金标检验。没有强标签上限时，线上 RM 分不足以证明泛化成功。

和安全税叠：弱监督者过度拒绝，学生会把拒答学成默认，见 `align-over-refuse`、`align-safety-tax`。helpful 切片和 harmless 切片要分开看 gap。

生产中可以用可验证奖励和原则监督补足弱标签，但没有强金标时，仍要承认泛化差距无法完整测量。

相关：`align-debate`、`align-cai`。

## 追问

**这是蒸馏吗？**
蒸馏通常是强教师弱学生。这里教师更弱，问的是学生会不会被较弱教师的错误限制。
**没有强金标怎么知道泛化了？**
实验室用人为的能力差当代理。生产只能看下游任务和人抽查，承认代理失效风险。
**和过程监督的关系？**
若人只能检查步骤不能检查终局，过程标签仍是弱监督，噪声见 `align-process-reward`。
**面试怎么收？**
说清问题（监督者盖不住），说清 naive SFT 的失败，说清论文是部分泛化而不是已经解决问题。
**弱标签加 RL 是不是更糟？**
常常是。RL 会放大老师的偏见，变成迎合弱 judge。能验证就走 RLVR，见 `align-rft`。
