---
id: stepfun-sft-loss-start
section: posttrain
order: 149
level: A
title: 阶跃星辰：SFT loss 的起点数值和收敛该怎么看？
quick: >-
  起点应接近 $-\log p_{\mathrm{base}}(\mathrm{answer}\mid\mathrm{prompt})$ 的量级，突然从 10+
  跳起多半是 mask / 模板错。收敛看 holdout CE 与业务分，不看训练 CE 是否到 0；混合加训起点常高于单域 continue。
tags:
  - StepFun
  - SFT
  - Loss
realInterview: true
status: published
format: markdown
updatedAt: 2026-08-19
sources:
  - title: 阶跃星辰大模型算法实习一面
    url: https://www.nowcoder.com/feed/main/detail/5cb1ebe809fd402d844cce47380a926f
    type: candidate-first-hand
---

## 真题记录

- 公司：阶跃星辰（StepFun）
- 团队 / 岗位：大模型算法实习
- 届别 / 流程：实习；一面
- 面试时间：原帖未披露；帖子发布于 2026-03-27
- 来源类型与可信度：牛客候选人原帖，B
- 原始措辞：**“Sft loss的起点数值和收敛情况。”**

不要编造一个全球标准起点。能报自己实验的区间最好；报不出就讲「如何诊断异常起点」。词表 $V\sim 10^5$ 时均匀 CE 约 $\ln V\approx 11.5$，但 chat 基座对规范回答的条件 CE 通常低得多。突然从 10+ 跳起，多半是 mask / 模板错，不是「模型太差」。原帖同时问混合加训——混合数据更杂，起点和平台期都可能高于单域 continue，不能据此判失败。

## 起点：应对齐基座的条件 CE

期望量级是 $-\log p_{\mathrm{base}}(\mathrm{answer}\mid\mathrm{prompt})$：用同一模板、只在回答 token 上算，扫一小批就能得到参照。起步接近该参照，说明数据与基座对得上。起步接近均匀随机，优先检查：是否对 prompt 也计了 loss、label 错位（右移漏了）、base 模板套在 chat 数据上、或特殊 token 没进词表。LoRA 刚挂上一般不应把 CE 打到 10+，除非输入已经对不上。

报数时说明 reduction（token mean / 样本 mean）和是否含 prompt，否则无法和别人的「起点 2.x」对比。

## 收敛：看 holdout 和业务，不看训到 0

训练 CE 持续降但 holdout 升是过拟合。CE 很低但格式乱，是评测与训练模板不一致，或 loss 没打在该打的字段上。业务分不涨、CE 却很好，说明示范和成功标准不是一回事——该补偏好或 verifier，而不是继续压训练 CE。混合加训因数据更杂，起点和平台期都可能高于单域 continue，应以锚点任务和新任务成功为准。

不要把「收敛到 0」当目标：词表大、回答多样时，合理平台可以明显大于 0。

## 和混合 / continue 一起看

Continue 单域数据齐，起点往往更低、下降更快。混合掺了锚点，CE 更高是分布更宽，不是没初始化好。两套实验不要比绝对 CE，要比各自 holdout。异常是「同数据、同模板，起点突然比昨天高一截」——那才回头查 mask 和并行有效 batch。

## 追问

- **有没有标准起点？** 没有。用基座在同样 mask 下扫一批当参照。
- **起点 11 左右是什么？** 接近均匀 CE，优先查 prompt 是否被打进 loss、模板是否错。
- **训练 CE 到很低就停吗？** 看 holdout 与格式合法率。过拟合和模板错位都可能 CE 很低。
- **混合比 continue 起点高正常吗？** 正常。数据更杂；用锚点 holdout 判，不用绝对 CE。
