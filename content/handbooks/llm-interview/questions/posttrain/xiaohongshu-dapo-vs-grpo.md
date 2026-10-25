---
id: xiaohongshu-dapo-vs-grpo
section: posttrain
order: 147
level: S
title: 小红书 Hi lab：DAPO 相对 GRPO 优化了什么？
quick: "DAPO 修的是 GRPO 在长推理 RL 里的几类工程失败：Clip-Higher 放宽正优势上界防熵崩，动态采样丢掉全对全错组，token 级损失避免长序列梯度被摊薄，超长惩罚做平滑减轻截断噪声。答题时按它治哪种病来讲，别背缩写。"
tags:
  - Xiaohongshu
  - DAPO
  - GRPO
realInterview: true
status: published
format: markdown
updatedAt: 2026-08-21
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

DAPO 修的是 GRPO 在长推理强化学习（RL）里的几类工程失败：clip 太紧、有效样本太少、长序列梯度被摊薄、超长截断带来噪声。它没有换一个新的优势公式。GRPO 省掉价值评估模型（critic）以后，很长的推理过程照样会在 clip、采样和长度上翻车，DAPO 就是冲着这些去的。所以别把它答成「更好的 GRPO」，也别和「去 KL」混成一件事，具体条目以论文为准，每一条都对上一种 GRPO 的病来讲。

## GRPO 实际会踩哪些坑

组相对优势 $A_i=(r_i-\bar r)/\sigma_r$ 能去掉 value model，但训着训着常见这些情况：回复越来越长，熵往下掉，clip 上界太紧把稀有正优势 token 的更新裁掉，组内全对或全错浪费样本。这些毛病跟没有 critic 关系不大，是对称的 clip、按序列等权的损失和硬截断奖励叠在一起造成的。所以我会先讲失败的原因，再讲对应的改动。

举个例子：模型偶然写出一步很关键的「先验算一下」，这个 token 概率很低，优势很高。对称 clip 下，它的概率涨一点就碰到 $1+\varepsilon$ 的上界被裁掉，这种刚冒头的探索很快就没了，策略越来越锁在已有的高概率模式上。

## DAPO 四类改动分别治什么

Clip-Higher 就是治上面这个例子的。它把 clip 做成非对称的，放宽正优势那一侧的上界，让低概率但高 $A$ 的 token 有上升空间。

Dynamic Sampling 丢掉 accuracy 为 0 或 1 的 group，保证 batch 里有有效优势。它是跟着当前策略做的动态过滤，题并没有被永久删掉。

Token-level PG 让损失更接近每个 token 等权，避免「一条回复一个权重」时，长序列里单个 token 的梯度被摊薄。

Overlong shaping 处理的是截断。硬截断会把奖励从 1 直接打到 0，这是一种不连续的噪声，换成更平滑的超长惩罚，可以减轻长度 hack。

DAPO 也讨论过和 KL 有关的设计，但它的核心是采样和 clip 的工程，跟「去 KL」不是同一个卖点。落地时要把消融复现出来，别把所有变体都叫 DAPO。

## 落地时别喊口号

clip 上界放宽，更新会更猛，要盯住熵、长度和 holdout。动态采样如果长期只留下当前能解的题，会变成一种隐性的 curriculum，所以要定期去探测全错的那一桶。token 级损失也不总是比序列级好，取决于你想要序列等权还是 token 等权。

最后收一句：GRPO 提供组相对基线，DAPO 在它上面修 clip、有效样本、长度加权和截断噪声。

## 追问

**Clip-Higher 和熵崩有什么关系？**
稀有好 token 的正向提升如果很快被上界裁掉，策略就更容易锁进已有的高概率模式，熵随之往下掉。

**Dynamic Sampling 会不会偏科？**
会。只保留当前能解的输入提示（prompt），可能把超难题丢掉，要配覆盖配额，并定期再探测。

**去掉 KL 算不算 DAPO？**
不算。那是另一条取舍，见去 KL 那张卡，别把后续工作的开关都贴到 DAPO 上。

**怎么证明改动有效？**
按失败模式做消融，看无效 group 比例、平均长度、熵、clip fraction，光报一个平均奖励分数（reward）说明不了问题。

相关：`pt-grpo`、`pt-dapo`、`xiaohongshu-grpo-drop-kl`、`gaode-dapo-no-kl`
