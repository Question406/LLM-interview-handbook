---
id: pt-rlvr-reasoning-eval
section: posttrain
order: 38
level: S
title: 为什么 Pass@K 可能错误判断 RLVR 只是压缩多样性？如何评测推理本身正确而非只看最终答案？
quick: Pass@K 只问候选里是否出现正确最终答案，混淆覆盖率、选择器和轨迹质量。应联合报告 Pass@1、Pass@K、正确轨迹率、过程 verifier 分数与独立 trace audit，并固定采样温度和 K。
tags:
  - RLVR
  - Evaluation
  - Reasoning
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-17
sources:
  - title: RLVR Implicitly Incentivizes Correct Reasoning
    url: https://arxiv.org/abs/2506.14245
    type: primary
---

若 RL 后 Pass@1 上升、Pass@K 不变，可能是把已有正确模式重加权，也可能是采样多样性下降；反过来，Pass@K 上升但 Pass@1 不涨可能是覆盖变多却缺乏可靠选择。只用一个指标无法判断。

对能检查的任务，给每条 trace 标注最终正确性、关键中间断言正确性和是否存在无效跳步；对不可完全形式化的任务，用独立 judge 加人工抽检。报告 trace-level 指标时需防止 reward/verifier 与评测 oracle 共用同一漏洞。

实验还应控制温度、长度上限、K 和计算预算。否则所谓“推理改善”可能只是测评协议换了，或输出更多候选增加了碰巧命中的机会。
