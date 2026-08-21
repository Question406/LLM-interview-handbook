---
id: stepfun-mixed-vs-continue-sft
section: posttrain
order: 131
level: S
title: 阶跃星辰：混合加训和 continue SFT 哪个效果好？
quick: >-
  混合加训把新领域数据与通用锚点数据按比例一起训，更抗遗忘；continue SFT 只喂新数据，适配快但易丢掉通用能力。选择看领域偏移大小和必须保住的 holdout；没有锚点数据就不要只 continue。
tags:
  - StepFun
  - Continual Training
  - SFT
  - Forgetting
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
- 原始措辞：**“如何进行混合加训”**；**“混合加训和 continue sft 你觉得哪个效果好，为什么？”**

没有绝对赢家。Continue 快、混合稳，选择看领域偏移和必须保住的 holdout。原帖还问 SFT loss 起点——混合因数据更杂，起步 CE 常更高，不能据此判失败。更糟的答法是「混合一定更好」却说不出锚点从哪来：没有可复现的 replay 池，所谓混合就是随机掺点旧数据，配比实验做不成。

## Continue SFT：适配快，容易忘

Continue SFT 在已有指令模型上只继续吃新任务 / 新领域数据。实现简单、新任务上升快，适合领域很近、只需补格式的情况。分布一偏，通用指令、安全和旧业务 holdout 容易掉，属于典型灾难遗忘：每步梯度都把概率质量推向新域。1T 级只喂单一语料时，还会把模型洗成该语料的风格，通用能力回不去。

若产品只上新域、旧能力可以弃，continue 可以是正确选择。要先把「允许掉哪些 holdout」说死，再省 replay 成本。

## 混合加训：锚点拉住梯度

混合加训（replay / mixture）把新数据与通用指令、旧业务锚点、少量预训练或高质量公开指令按**有效 token** 配比同训。新能力仍能学，但每步梯度被锚点拉住。代价是数据工程更重：要维护可复现的 replay 池、配比扫描和两边 holdout。起步 loss 常因数据更杂而更高，平台期也可能高于单域 continue——应以锚点 holdout 和新任务成功一起看，而不是只追新数据 CE。

配比按有效 token 而不是按条数：新域样本若更长，条数 1:1 实际已经偏新域。

## 怎么选：看偏移和必须保住什么

领域近、只需补格式，continue 可能够。领域远、必须保住通用基准或旧业务，混合几乎总是更稳。没有锚点数据就不要只 continue 还声称「不会忘」。1T 级继续训时，混合还能降低「把模型洗成单一语料」的风险。面试给决策表：偏移小 / 可弃旧 → continue；偏移大 / 要保 holdout → 混合。原帖两问应一起答：混合怎么配、以及为什么它的 loss 起点不能当唯一判据。

## 追问

- **锚点从哪来？** 旧业务抽样、通用指令、高质量公开集；要可复现，不能每次随机抓。
- **配比怎么扫？** 扫有效 token 比，同时看新任务和锚点 holdout，停在两边都过门禁的点。
- **混合 loss 更高是不是没学好？** 不一定。数据更杂，CE 平台更高；看 holdout 和业务分。
- **和继续预训练的关系？** 领域知识大洞应先领域 pretrain / 配比，再 SFT；只 continue SFT 补不回底座。
