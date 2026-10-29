---
id: dt-trigger-ood
section: labs
order: 11
level: A
title: Tesla / Scale：车队 trigger 和影子模式，接到 LLM 评测失败怎么说？
quick: >-
  把车队 trigger 的思路换成「评测失败触发收集」：固定评测失败、judge 或人与 RM 的分歧、工具验证失败和低置信步骤，才值得进 feedback
  loop，再用许可或 synthetic data 复现。影子模式的输出当不了 gold labels，用户没改摘要也不等于认可。可验证样本自动扩，主观
  hard examples 按人工预算处理。
companies:
  - apple
tags:
  - Tesla
  - Scale AI
  - Active Learning
  - Apple
realInterview: false
status: published
format: markdown
updatedAt: 2026-10-12T00:00:00.000Z
sources:
  - title: Tesla AI Day 2022
    url: 'https://www.youtube.com/watch?v=ODSJsviD_SU'
    type: primary
  - title: Tesla AI
    url: 'https://www.tesla.com/AI'
    type: primary
  - title: How Do You Train Autonomous Vehicles for the Toughest Edge Cases? (Scale)
    url: >-
      https://learn.scale.com/public/blogs/qanda-how-do-you-train-autonomous-vehicles-for-the-toughest-edge-cases
    type: secondary
---

可以借车队 trigger 的思路，把触发源换成评测失败：固定评测里失败的任务，两个 judge 或人与 RM 判断不一致的 preference pairs，工具任务里的验证失败、空结果和低置信步骤。进下一轮的是这些题目，以及用许可或 synthetic data 做的复现。

为什么要 trigger？Tesla AI Day 和 Scale 的 AV 讲座都讲过，车队每秒都在产生数据，有用的只是那一小段失败。Karpathy 早期说过，99.9% 的时间都很好开，要找的是那 0.1%。Scale 举的例子是阴影被当成车道线，于是专门去挖同类光照下的下匝道 clip。随机 sampling 在这种分布下几乎拿不到有用样本。

车队回传的条件是低置信、多相机互斥或人机分歧，LLM 这边对应的就是评测失败触发收集。影子模式的输出也当不了 gold labels，车上如此，LLM 上「用户没改摘要」同样不能当 chosen。LLM 上对应影子模式的检查，是让新模型在旧评测上运行、和旧模型对比，线上的隐式点击不当标签。

触发出来的样本按可验证性分层处理：可验证的自动扩充，验证不了的交给有限的人工预算，见 `dt-human-budget`。这里的带宽约束是人时和 GPU，不可能把所有失败都合成十遍。参考标签仍然要有协议和抽查，见 `dt-annotator-protocol`。

## 追问

**能直接把失败的用户对话拿回来训吗？**
默认不回收用户数据。记下失败类型，用许可或 synthetic data 复现。

**失败太稀，触发不出来怎么办？**
提高触发召回，离线再筛。

**评测里还没有的任务怎么办？**
研究集要覆盖产品将要新增、但评测还没包含的任务，见 `dt-novel-bootstrap`、`dt-see-around-corners`。稀有 locale 和工具路径用合成来补，等它们自然出现，往往要等到线上出事故。

**和 us-tech 的 Tesla 卡怎么分？**
`tesla-data-engine` 讲车端 feedback loop，包括延迟、占用和自动标注几何；这张卡只回答选什么进 feedback loop。
