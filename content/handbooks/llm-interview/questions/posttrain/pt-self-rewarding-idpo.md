---
id: pt-self-rewarding-idpo
section: posttrain
order: 35
level: S
title: 让同一个 LLM 当 Judge、产生偏好并做 Iterative DPO，如何避免自证循环？
quick: 不能把“自己给高分”当真值。隔离 judge 与 policy 版本，做位置交换和长度偏差校准，周期性接入人工或外部 judge，并始终用未参与偏好生成的独立评测集做 regression gate。
tags:
  - Self-Rewarding
  - DPO
  - Judge
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-17
sources:
  - title: Self-Rewarding Language Models
    url: https://arxiv.org/abs/2401.10020
    type: primary
---

迭代偏好优化可以扩大标注供给，但 judge、数据生成器和被训练 policy 若同步更新，模型可能强化自己的措辞、长度或立场偏好。至少要 pin 住每轮 judge 版本，并把候选顺序随机交换，测量 position bias、verbosity bias 和自洽性。

对高影响样本采用外部 verifier、人工锚点或多个独立 judge；对 judge 不确定/分歧大的 pair 不应强制硬标签。每轮保留 prompt、候选、rubric、judge rationale 和版本，才能定位偏差从哪一轮进入。

评估不能沿用同一个 self-judge。需要外部质量集、对抗集和跨风格测试；一旦 win rate 只在本轮 judge 上涨，应停止迭代并重校准。
