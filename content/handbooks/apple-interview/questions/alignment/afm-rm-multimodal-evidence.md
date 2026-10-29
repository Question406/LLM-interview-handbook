---
id: afm-rm-multimodal-evidence
section: alignment
order: 115
level: A
title: multimodal RM：会写漂亮说明，却看不到图中的错误，怎么揭穿？
quick: 我会先确认 judge 真的看到了图片，再检查它的选择会不会跟着图中的关键证据变化。
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
  - title: Multimodal RewardBench 2
    url: 'https://arxiv.org/abs/2512.16899'
    type: primary
---

## 面试官可能这样问

multimodalRM 把写得漂亮、但读错图的答案选上去了，怎么查？

## 可以这样回答

我会先确认评审器拿到了什么。有时叫 multimodal 评价，实际只把 OCR 文本或 caption 交给 judge，那它可能根本看不到小数点、位置关系或图里的矛盾。

然后我会做很小的图像变化，比如把票据总额从18.50改成1850，其他内容尽量保持一样。两条候选回答的正确性应该随证据改变；如果 RM 仍然只喜欢更详细的那条，就说明值得进一步查视觉证据的使用。最终我会用字段真值或实际状态核验，而不是再让同一个模型写一段解释证明自己看对了。

## 技术备查

## 场景与问题
两条截图问答都很流畅，一条把金额 18.50 读成 1850，RM 更偏爱错误但更详细的回答。如何造 hard examples 并验证 RM 用到了视觉？

## 参考答案
先检查评审实际拿到的是图、OCR 还是只有 caption。做成对截图：只改金额、小数点或按钮状态；同一回答在证据变动后应改变正确性排序。对图替换、遮挡或不匹配作为诊断干预，报告任务分层，避免把任意遮挡引发的 out-of-distribution (OOD) 表现当作 causal 结论。

Multimodal RewardBench 2 扩展到图文理解、编辑与交错生成等偏好评价；本题围绕金额构造的方案是原创。补证据正确但简洁、流畅但证据错误、只靠 OCR 不够的困难对。独立视觉专家和可执行状态验证做 calibration，不能用同一个生成器再写一段漂亮解释证明自己正确。

## 追问
**图像编辑只用 CLIP 相似度行吗？** 不行，局部编辑要求、保留区域和安全约束需单独检验。
**所有错例都给高权重？** 先查是否有可识别证据与可靠标签，否则高权重会放大噪声。

