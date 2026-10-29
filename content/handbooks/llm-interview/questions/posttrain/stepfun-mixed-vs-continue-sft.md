---
id: stepfun-mixed-vs-continue-sft
section: posttrain
order: 131
level: S
title: 阶跃星辰：混合加训和 continue SFT 哪个效果好？
quick: >-
  没有绝对赢家。continue SFT 只喂新数据，适配快但容易丢通用能力；混合加训把新数据和 general-capability regression
  data 按有效 token 配比一起训，更抗遗忘。选哪个看领域偏移多大、哪些 holdout 必须保住；没有 regression data，就别只做
  continue 还说不会忘。
tags:
  - StepFun
  - Continual Training
  - SFT
  - Forgetting
realInterview: true
status: published
format: markdown
updatedAt: 2026-08-21T00:00:00.000Z
sources:
  - title: 阶跃星辰大模型算法实习一面
    url: 'https://www.nowcoder.com/feed/main/detail/5cb1ebe809fd402d844cce47380a926f'
    type: candidate-first-hand
---

## 真题记录

- 公司：阶跃星辰（StepFun）
- 团队 / 岗位：大模型算法实习
- 届别 / 流程：实习；一面
- 面试时间：原帖未披露；帖子发布于 2026-03-27
- 来源类型与可信度：牛客候选人原帖，B
- 原始措辞：**“如何进行混合加训”**；**“混合加训和 continue sft 你觉得哪个效果好，为什么？”**

两种没有绝对的赢家：continue 适配快，混合更稳，选哪个看领域偏移有多大、哪些 holdout 必须保住。偏移小、旧能力可以放弃，continue 就够；偏移大、通用基准或旧业务必须保住，混合几乎总是更稳。答「混合一定更好」，却说不出 regression data 从哪来，是更糟的答法：没有可复现的 replay 池，所谓混合就是随手掺点旧数据，配比实验也做不成。

先说 continue SFT。它在已有的指令模型上只继续吃新任务、新领域的数据，实现简单，新任务涨得快，适合领域很近、只需要补格式的情况。分布一偏，通用指令、安全和旧业务的 holdout 就容易掉，这是典型的灾难遗忘，每一步梯度都在把概率质量推向新领域。1T 级只喂单一语料时，还会把模型洗成那份语料的风格，通用能力回不来。当然，如果产品只上新领域、旧能力可以弃，continue 也可以是正确选择，前提是先把「允许掉哪些 holdout」说死，再去省 replay 的成本。

混合加训（replay / mixture）是把新数据和通用指令、旧业务 regression data、少量预训练或高质量公开指令放在一起训。新能力照样能学，但每一步更新都同时受到 regression data 的影响。配比要按有效 token 数算，别按条数：新领域样本如果更长，条数 1:1 实际上已经偏向新领域了。代价是数据工程更重，要维护可复现的 replay 池、做配比扫描、两边都留 holdout。

原帖还连着问了 SFT 的初始 loss，正好可以一起答。混合的数据更杂，起步的 cross entropy loss（CE）往往更高，平台期也可能高于单领域 continue，这说明不了训练失败。判断效果要把 regression evaluation set 和新任务的成功率放在一起看，光追新数据上的 CE 不行。1T 级继续训时，混合还能降低模型被洗成单一语料风格的风险。

所以面试里我会给一个简单的决策：偏移小、旧能力可弃，用 continue；偏移大、要保 holdout，用混合。再补一句混合怎么配，以及为什么它的 loss 起点不能当唯一判据。

## 追问

**regression data 从哪来？**
旧业务抽样、通用指令、高质量公开集都行，但要可复现，每次随机抓一批不行。

**配比怎么扫？**
扫有效 token 的比例，同时看新任务和 regression evaluation set，停在两边都通过 acceptance checks 的那个点。

**混合的 loss 更高，是不是没学好？**
不一定。数据更杂，CE 的平台期本来就高，要看 holdout 和业务分。

**和继续预训练是什么关系？**
领域知识有大洞，应该先做领域 pretrain 或调配比，再做 SFT。只靠 continue SFT 补不回底座。
