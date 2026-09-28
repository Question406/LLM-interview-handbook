---
id: data-hard-negative
section: data
order: 2
level: S
title: Preference Data 怎么构造 Hard Negative？
quick: >-
  高价值 rejected 应该 plausible but wrong，别拿「我不知道」凑数。最好只在一个关键维度上比 chosen 差，让模型学真正 decision boundary，同时控制长度、风格等 confound。
tags:
  - Preference Data
  - Hard Negative
realInterview: false
status: published
format: markdown
provenance: legacy-handbook-v2
updatedAt: 2026-08-21
sources:
  - title: Training a Helpful and Harmless Assistant with RLHF
    url: 'https://arxiv.org/abs/2204.05862'
    type: primary
---

最容易的 negative 是 chosen 完整正确、rejected 写「我不知道」。这种 pair 只教模型少说废话，学不到 correctness 边界。Hard negative 必须 plausible but wrong：看起来像样，只在一个关键维度上比 chosen 差。错法：堆「一眼假」的 rejected，DPO/RM 表面 loss 很好，线上仍分不清细错。Anthropic HH 的价值也在「有帮助但略越界 / 无害但没用」这类近边界对比，正确 vs 胡话不够。

## 只动一个关键维度

有效构造往往只改一处：推理链错一步；主体、时间、单位细偏；代码整体能跑但边界 case 错；工具选对但 argument 错；内容对但违反格式或安全约束；Agent 轨迹只在一个决策上选错文件或过早 terminate。对照应尽量 length-matched、风格相近，否则模型学的是「长=好」或 style classifier。多维 rubric + pair difficulty 分桶，才能知道你在训哪条边界，避免所有 hard pair 其实都是「更短所以输」。

Easy negative 仍有用：少量「别胡说」能稳住底线。配比上先 easy 后提高 hard 比例；全 hard 且无校准，梯度噪声会很大。

## 控制 confound，保留标不准的不确定性

若所有 chosen 更长、更客气，梯度会走 nuisance。做法：长度匹配、对调风格的 counterexample pair、分维度打分后再合成偏好。Annotator 对极难 pair 分歧大时，不要强行二值化：保留 tie、软概率，或降权。Hard 过了头、人类和 judge 都抖，就是 label noise，会毒 RM。同时看 pair margin、annotator agreement、verifier confidence。三者都低，这条不该进硬偏好。见 `data-annotator-agreement`。

## Agent 轨迹上的 hard negative

从成功轨迹复制，只替换一个关键 action（错 repo 文件、错 tool 参数、过早结束），再在真实环境跑出后续失败，使 credit 集中。不要整条随机打乱，那会变成「轨迹不像」而不是「决策错」。失败后缀一般不当正 SFT：错误步做 rejected，若有 recovery 则 recovery 做正例。这和 `arl-trajectories` 是同一思想在 pair 构造上的落地。

挖掘来源不要只会手写：线上错误、judge 与 human 不一致的 pair、模型高置信但 verifier 失败的样本，都是现成 hard negative 矿。过滤仍按「只差一维、长度风格匹配、人能稳定分」三关。数量上 hard 应逐渐占偏好集的主体，但每桶都留一点 easy，防止模型忘了「胡话也是错」。发布时按难度分桶报 win-rate，只报总体赢面会掩盖「细错仍不会抓」。

## 追问

- **如何构造 Agent trajectory negative？** 复制成功轨迹，只改一个关键 action（错文件、错参数、过早结束），在真实环境执行得到后续 failure。前后上下文保持相似，credit 才集中在那一步。
- **Hard negative 太难会怎样？** 人/judge 自己都抖就会引入 label noise，RM 拟合的是争吵。要用 pair margin、annotator agreement 和 verifier confidence 三道门，过不了就降权或当 tie。
- **和 easy negative 怎么配比？** 先用少量 easy 稳住「别胡说」，再提高 hard 比例。全 hard 且无校准，loss 会抖、模型忘底线；按难度分桶报 win-rate，避免总体分掩盖细错。
