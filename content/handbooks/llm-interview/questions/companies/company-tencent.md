---
id: company-tencent
section: companies
order: 3
level: A
title: 腾讯混元：公开面经反映的考察风格是什么？
quick: >-
  覆盖面很宽：Qwen vs DeepSeek、MoE vs Dense、LoRA / 全参对比实验、ZeRO 1/2/3、SFT
  数据构造、RLHF，再穿插括号生成 / 最长子串 / 零钱兑换。需要对齐算法和训练系统都没有明显短板。
tags:
  - Tencent
  - Hunyuan
  - 真题导航
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-18
sources:
  - title: 日常实习 腾讯混元大模型一面 好难
    url: https://www.nowcoder.com/feed/main/detail/8066dff3170547c98738ed3b1ba1b496
    type: candidate-first-hand
  - title: 腾讯-混元大模型面经-华5硕
    url: https://www.nowcoder.com/feed/main/detail/692fed73109e4d31915e46d34d27c762
    type: candidate-first-hand
  - title: 腾讯混元TEG大模型三面-实习面经
    url: https://www.nowcoder.com/feed/main/detail/30d3886e7f4c4a76a5f1a4f3c243dfb4
    type: candidate-first-hand
  - title: 秋招面经-腾讯WXG NLP算法一面
    url: https://www.nowcoder.com/feed/main/detail/0bdb10f282b541bda9ae11db203a40eb
    type: candidate-first-hand
---

混元 / TEG / WXG 都容易从你项目细节追机制：数据怎么配、reward 为何有效、ZeRO-3 省的是什么、通信是什么。不要只背定义。

## 准备主线

1. **架构选型**：MoE 收益与通信代价；Qwen 与 DeepSeek 差在路由 / MLA / 后训练。
2. **微调实验**：LoRA vs 全参要能设计对照，不只说「LoRA 省显存」。
3. **系统**：ZeRO 三级、除 DeepSpeed 外的优化、72B 单卡估算。
4. **对齐**：SFT 之后为何还要 RL；GSPO / SPO 在 WXG 会被追。
5. **手撕**：括号生成、最长无重复子串、零钱兑换、MHA。

## 本手册真题卡

点击下面每条即可跳到对应题。

- 腾讯混元：ZeRO-3 微调 Qwen2-72B 时如何估算单卡显存？
- 腾讯混元：LoRA 的 A/B 矩阵如何初始化？还有哪些初始化？
- 腾讯混元：为什么 SFT 之后还要做 RLHF？只用 SFT 可以吗？
- 腾讯 TEG：什么情况下使用 GRPO 效果会不好？构造数据要符合什么要求？
- 腾讯 TEG：使用 GRPO 时，构造数据要符合什么要求？
- 腾讯大模型实习：怎样证明自动数据筛选与人工标准对齐？
- 腾讯 WXG：如何估算 SFT 参数量与显卡利用率？
- 腾讯 WXG：GSPO 的优化是什么？腾讯的 SPO 有何不同？
- 腾讯 WXG：用 RL 训练小模型，相比大模型要改什么？
- 腾讯 26 校招：GRPO 的 rollout 如何设定？为什么不直接用连续奖励？
- 腾讯混元一面：Qwen 和 DeepSeek 差在哪，什么时候你会换底座？
- 腾讯混元一面：MoE 相对 Dense 赚在哪、亏在哪？
- 腾讯混元一面：LoRA 和全参微调怎么设计对照实验？
- 腾讯混元：ZeRO-1 / 2 / 3 各分什么，什么时候升到 3？
- 腾讯混元：除了 DeepSpeed，训练还能靠哪些优化？
- 腾讯混元：微调 Qwen 时数据怎么构造、清洗和配比？
- 腾讯混元一面：生成所有合法括号组合
- 腾讯混元一面：手写 Multi-Head Attention 要交代哪些形状？
- 腾讯混元：最长无重复字符子串
- 腾讯 TEG 三面：零钱兑换 I / II 差在哪？
