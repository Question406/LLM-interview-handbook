---
id: drustz-d209f295ada1098caa
section: openai
order: 128
level: A
title: Debug and Improve a GRPO RL Training Loop for Language Models (PyTorch)
quick: >-
  original-structured-preparation-guide · Debug and Improve a GRPO RL Training
  Loop for Language Models (PyTorch)
companies:
  - openai
tags:
  - DrustZ
  - original-structured-preparation-guide
  - OpenAI · 题库与复习指南
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
      https://www.1point3acres.com/interview/problems/906a162e-db6b-4431-8c41-1c53c758d2b9
    type: secondary
---
> DrustZ 整理的复习指南。公司与轮次信息沿用作者的来源记录。

# 调试与改进 GRPO 训练循环

> 旧内容只是宽泛的 RL 基础资料。原始 PyTorch starter code 未公开，下面是与 GRPO 标题对应的检查框架和核心公式。

## 核心流程

对每个 prompt sampling一组 `G` 个 completion，得到 reward `r_i`。在组内standardization advantage：

```text
A_i = (r_i - mean(r_group)) / (std(r_group) + eps)
```



保存 rollout 时的 `old_logprob`，训练时计算：

```text
ratio = exp(new_logprob - old_logprob)
clipped = clip(ratio, 1-epsilon, 1+epsilon)
policy_loss = -min(ratio*A, clipped*A)
```



再加入相对 frozen reference policy 的 KL penalty。loss 只对 completion token 计算，并用 attention/completion mask 排除 prompt 与 padding。

## 最常见的 bug

- advantage 没按 prompt group normalization；
- `old_logprob`、reward 或 advantage 没有 detach；
- reference model 仍在更新或 dropout 没关闭；
- token shift 错一位；
- prompt token 也进入 policy loss；
- 先按 token 平均、再按 sequence 平均的分母不一致；
- `exp(logprob difference)` 在低精度溢出；
- reward 全相同时除以 0；
- rollout policy 与更新后的 policy 数据混用过久。

## 调试方法

先用一个 prompt、两个很短 completion 和手写 reward，打印每个 token 的 mask、logprob、ratio、advantage 与 loss。验证 ratio 在新旧模型相同时为 1；正 advantage 应提高对应 completion 概率，负 advantage 应降低。

## 复杂度

主要成本是每个 prompt 生成 `G` 条序列以及 policy/reference forward，约与 `batch × G × sequence_length × model_cost` 成正比。显存还需保存 token、旧 logprob 和训练 activation；可用 gradient checkpointing 与分批生成权衡。

### 来源与内容类型

- Content kind: `original-structured-preparation-guide`
- [原始来源](https://www.1point3acres.com/interview/problems/906a162e-db6b-4431-8c41-1c53c758d2b9)

---

来源：[DrustZ / Mingrui Zhang · 1acre3points_crawl/data/questions.json](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/1acre3points_crawl/data/questions.json)。作者整理资料；许可和第三方来源范围见阅读指南。
