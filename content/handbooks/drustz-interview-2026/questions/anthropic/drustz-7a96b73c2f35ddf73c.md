---
id: drustz-7a96b73c2f35ddf73c
section: anthropic
order: 67
level: A
title: Debug three RL training bugs and discuss GRPO trade-offs and variants
quick: >-
  original-structured-preparation-guide · Debug three RL training bugs and
  discuss GRPO trade-offs and variants
companies:
  - anthropic
tags:
  - DrustZ
  - original-structured-preparation-guide
  - Anthropic · 题库与复习指南
realInterview: false
status: published
format: markdown
updatedAt: '2026-10-28'
sources:
  - title: DrustZ / Mingrui Zhang · pinned source
    url: >-
      https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/1acre3points_crawl/data/questions.json
    type: primary
  - title: 作者记录的原始来源
    url: >-
      https://www.1point3acres.com/interview/problems/bb3d1390-8cc8-41a4-938b-95ae37967619
    type: secondary
---
> DrustZ 整理的复习指南。公司与轮次信息沿用作者的来源记录。

# GRPO 训练循环：用实验定位三处未知 Bug

## 证据边界

公开标题确认 starter 中有三处 bug，但源码没有公开，故不能预先编造“三处固定答案”。一份本地直接面经在**那一次代码**里发现：把 logits 直接交给要求非负权重的 `torch.multinomial`，以及 advantage standardization分母缺 epsilon；这两点只能作为候选检查项，不能断言当前 UUID 仍相同，第三处更无证据。注意 `Categorical(logits=...)` 本来就接受 logits，不应机械加 softmax。

## 可读任务、诊断接口与输入输出例

给定 policy、old/reference policy、prompt/completion、reward 与 mask 的训练 step，找出实际失败不变量并修复，随后解释 clipping、KL 和 GRPO/PPO 权衡。可先写：

```python
def inspect_step(batch, policy, old_policy, ref_policy) -> DebugReport: ...
```



最小 batch 只含一个 prompt、两条短 completion，手设一高一低 reward。修复后的报告应满足：group advantage 有限、均值近 0 且符号相反；prompt/pad mask 为 0；policy 与 old 完全相同且在同一 eval forward、更新前重算时，completion token ratio 接近 1。

## Debug 实验与关键公式

按数据流逐层断言 shape、finite、device 和 detach。先检查sampling API 所需的是 logits 还是 probabilities；再检查 advantage 是否在每个 prompt 的 G 条 rollout 内计算，并用 `std+eps` 处理同奖组；随后对齐 autoregressive shift，确认只 gather 目标 token、只在 completion mask 上聚合。核心是 `ratio=exp(new_logp-old_logp)`，不是简单差值。若 ratio 不为 1，做ablation：同 checkpoint 同训练器重算、关闭 dropout、改 fp32、在第一次 optimizer step 前比较，再与独立 rollout engine 的 old_logp 比较；多次 update、不同 kernel/精度都可能产生合理偏差，不能一概判 bug。

GRPO 省掉 critic 与 value loss，但每个 prompt 需多条 rollout，生成成本高，组内奖励相同会失去学习信号。clip 提升稳定性却会截断大更新；KL 可约束远离 reference，但系数过大会压弱奖励。还应讨论 outcome/process reward、组大小、off-policy correction 和按 token/sequence normalization。

## 复杂度与边界测试

设 prompt batch `B`、每组 `G` 条、长度 `L`，生成与 policy/reference forward 成本约 `O(BGL·model_cost)`；保存 token、mask、old logprob 和 activation 的空间也随 `BGL` 增长。测试 G=1、奖励全同、全 padding/空 completion、长度不一、极大 logprob 差导致 exp 溢出、bf16、dropout、reference 未冻结、old tensor 未 detach、零有效 token 分母和多 optimizer epoch。每个修复都应配会先失败后通过的回归测试。

### 来源与内容类型

- Content kind: `original-structured-preparation-guide`
- [原始来源](https://www.1point3acres.com/interview/problems/bb3d1390-8cc8-41a4-938b-95ae37967619)

---

来源：[DrustZ / Mingrui Zhang · 1acre3points_crawl/data/questions.json](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/1acre3points_crawl/data/questions.json)。作者整理资料；许可和第三方来源范围见阅读指南。
