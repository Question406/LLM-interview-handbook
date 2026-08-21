---
id: xiaohongshu-dapo-vs-grpo
section: posttrain
order: 147
level: S
title: 小红书 Hi lab：DAPO 相对 GRPO 优化了什么？
quick: >-
  DAPO 针对 GRPO 的熵崩、过长响应和 clip 不对称等问题，引入 clip-higher、动态采样、token 级损失解耦等工程改动。面试应讲清改的是哪类失败，而不是背缩写。
tags:
  - Xiaohongshu
  - DAPO
  - GRPO
realInterview: true
status: published
format: markdown
updatedAt: 2026-08-19
sources:
  - title: 小红书Hi lab 日常实习 一面
    url: https://www.nowcoder.com/feed/main/detail/8f02e3837274408d9c94c312e8ee578d
    type: candidate-first-hand
  - title: DAPO
    url: https://arxiv.org/abs/2503.14476
    type: primary-paper
---

## 真题记录

- 公司：小红书
- 团队 / 岗位：Hi lab 日常实习
- 届别 / 流程：日常实习；一面
- 面试时间：原帖未披露
- 来源类型与可信度：牛客候选人原帖，B
- 原始措辞：**“DAPO 相对于GRPO 的优化”**

小红书 Hi lab 一面这题，最容易把 DAPO 答成「更好的 GRPO」或和「去 KL」混成一件事。面试要听的是：GRPO 省 critic 之后，长链 RL 仍会在 clip、采样和长度上翻车；DAPO 改的是这些工程失败，不是换了一个新的优势公式。条目以论文为准，现场讲「针对哪种 GRPO 病」。

## GRPO 实务上会踩哪些坑

组相对优势 $A_i=(r_i-\bar r)/\sigma_r$ 能去掉 value model，但常见失败是：响应越训越长、熵掉、clip 上界过紧把稀有正向 token 卡死、组内全对 / 全错浪费样本。这些不是「没 critic」造成的，而是 clip 对称、序列等权损失和硬截断奖励叠在一起。先点名病，再对药，比背四个缩写更像练过。相关卡：`pt-grpo`、`pt-dapo`。

## DAPO 四类改动分别治什么

- **Clip-Higher**：非对称 clip，放宽正优势上界，让低概率但高 $A$ 的 token 有上升空间，缓解探索刚出现就被 $\varepsilon$ 裁掉。
- **Dynamic Sampling**：丢掉 accuracy 为 0 或 1 的 group，保证 batch 里有有效优势；这是当前策略依赖的动态过滤，不是永久删题。
- **Token-level PG**：损失更靠近每 token 等权，避免「一条回复一个权重」让长序列单 token 梯度被摊薄。
- **Overlong shaping**：硬截断把奖励从 1 打到 0 会造成不连续噪声；用更平滑的超长惩罚减轻长度 hack。

和「去 KL」不是同一卖点：DAPO 讨论过 KL 相关设计，但核心是采样与 clip 工程。落地必须复现消融，不要把所有变体都叫 DAPO。

## 落地时不要口号化

改 clip 上界会让更新更猛，必须盯熵、长度和 holdout。动态采样长期只留当前可解题，会变成隐性 curriculum，要周期性探测全错桶。token 级损失不是永远优于序列级，取决于你要序列等权还是 token 等权。面试收口：GRPO 提供组相对基线；DAPO 修 clip、有效样本、长度加权和截断噪声。相关卡：`xiaohongshu-grpo-drop-kl`、`gaode-dapo-no-kl`。

## 追问

- **Clip-Higher 和熵崩有什么关系？** 稀有好 token 的正向提升若很快被上界裁掉，策略更容易锁进已有高概率模式。
- **Dynamic Sampling 会不会偏科？** 会。只保留当前可解 prompt 可能丢掉超难题，要用覆盖配额和再探测。
- **去掉 KL 算不算 DAPO？** 不算。那是另一条取舍，见去 KL 卡；不要把后续工作的开关都贴到 DAPO 上。
- **如何证明改动有效？** 按失败模式消融：无效 group 比例、平均长度、熵、clip fraction，而不是只报一个平均 reward。
