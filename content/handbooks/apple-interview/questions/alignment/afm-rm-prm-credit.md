---
id: afm-rm-prm-credit
section: alignment
order: 113
level: A
title: PRM vs outcome RM：最终答案对了，过程错了，怎么标、怎么聚合？
quick: 最终答对只能证明结果这一项，不能说明每一步都值得学。过程监督要先定义究竟在评价局部正确、进展，还是可恢复性。
companies:
  - apple
tags:
  - Apple
  - AFM 补全 2026-10
  - Reward Modeling
  - 口述版
realInterview: false
status: published
format: markdown
updatedAt: '2026-10-26'
sources:
  - title: Let's Verify Step by Step
    url: 'https://arxiv.org/abs/2305.20050'
    type: primary
---

## 面试官可能这样问

最终答案对了，过程里有错，还能整段奖励吗？

## 可以这样回答

我会把最终结果和过程分开。数学题可能中间算错了，最后碰巧得到正确答案；工具任务也可能先改错文件，再把结果补回来。它们都不适合简单地把每一步标成好。

如果收过程标签，我会先定义 annotator 到底判断什么：这一步是否正确，是否推动任务，还是出错以后能不能恢复。然后比较这些标签带来的收益和成本。有些任务有很可靠的最终执行结果，先用 outcome reward 就足够；没有必要因为 PRM 更细，就假定它一定更好。

## 技术备查

## 场景与问题
数学 trajectories 有一处错误但最后碰巧答对；tool-use trajectories 先写错再回滚成功。两条都给每一步正标签合理吗？

## 参考答案
不合理。数学要标明首个错误以及无法判断的步骤；终局正确不能自动给全程正例。工具任务需同时看最终状态、权限和副作用，若写操作违反约束，回滚不一定消除损害。过程标签的语义应是局部有效、可恢复性或成功潜力中的哪一种，不能混用。

Let's Verify Step by Step 研究过程监督在数学任务中的价值，不能推广成所有任务都必选 PRM。产品中比较最终 verifier、PRM 和混合方法，按标注成本与固定生成预算评估。把步骤概率连乘会随步骤数变小且假设相关性处理不足；min、sum 和学习聚合也各有偏好，应对等价步骤拆分做稳定性测试。

## 追问
**没有专家能标每步怎么办？** 使用可执行中间状态、sampling 标注和弃权，别拿模型自信代替真标签。
**只标第一处错够吗？** 对找错有用，但不完整监督后续恢复能力，取决于训练目标。

