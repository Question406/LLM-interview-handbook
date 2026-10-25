---
id: stepfun-sft-loss-start
section: posttrain
order: 149
level: A
title: 阶跃星辰：SFT loss 的起点数值和收敛该怎么看？
quick: "起点应该接近基座在同一模板下对回答的条件 CE；从 10+ 起步多半是 mask 或模板错了。收敛看 holdout CE 和业务分，训练 CE 不需要压到 0。"
tags:
  - StepFun
  - SFT
  - Loss
realInterview: true
status: published
format: markdown
updatedAt: 2026-08-21
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

SFT loss 没有全球统一的起点，合理的起点应该接近基座在同一模板、同一 mask 下对回答的条件交叉熵损失（CE）；收敛看 holdout 和业务分，训练 CE 不用压到 0。能报自己实验的区间最好，报不出来就讲怎么诊断异常的起点，别编一个数。

先给一个参照。词表 $V\sim 10^5$ 时，均匀分布的 CE 约为 $\ln V\approx 11.5$，可 chat 基座对规范回答的条件 CE 通常低得多。所以如果 loss 突然从 10+ 起跳，多半是 mask 或模板错了，跟模型太差没什么关系。

## 起点该对齐什么

期望的量级是 $-\log p_{\mathrm{base}}(\mathrm{answer}\mid\mathrm{prompt})$。用同一个模板、只在回答 token 上算，扫一小批数据就能得到这个参照。起步接近参照，说明数据和基座对得上。起步接近均匀随机，就按顺序查：是不是把输入提示也算进了损失、label 有没有错位（右移漏了）、是不是把 base 模板套在了 chat 数据上、特殊 token 有没有进词表。LoRA 刚挂上一般不会把 CE 打到 10+，除非输入本身已经对不上了。

报数时要说明 reduction（token mean 还是样本 mean）、有没有包含 prompt，不然没法和别人说的「起点 2.x」对比。

## 收敛怎么看

训练 CE 一直降、holdout 却在升，是过拟合。CE 很低但格式乱，要么是评测和训练的模板不一致，要么 loss 没打在该打的字段上。CE 很好、业务分不涨，说明示范和成功标准不是一回事，该补偏好监督或验证器，继续压训练 CE 没用。词表大、回答又多样时，合理的平台期可以明显高于 0，「收敛到 0」本来就不是目标。

原帖还问了混合加训，这里正好接上。单领域继续训练的数据比较一致，起点往往更低、下降更快；混合掺了锚点，分布更宽，起点和平台期都可能更高，这不代表没初始化好，要以锚点任务和新任务的成功为准。两套实验别比绝对 CE，各自比 holdout。真正的异常是「同样的数据、同样的模板，起点突然比昨天高一截」，这时才回头查 mask 和并行下的有效 batch。

## 追问

**有没有标准的起点？**
没有。用基座在同样的 mask 下扫一批，当参照。

**起点在 11 左右说明什么？**
接近均匀分布的 CE，优先查 prompt 有没有被算进 loss、模板对不对。

**训练 CE 降到很低就可以停了吗？**
要看 holdout 和格式合法率。过拟合和模板错位都可能让 CE 很低。

**混合加训的起点比 continue 高，正常吗？**
正常，数据更杂。用锚点 holdout 来判断，别比绝对 CE。
