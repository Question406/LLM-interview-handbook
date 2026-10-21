---
id: dt-trigger-ood
section: labs
order: 11
level: A
title: Tesla / Scale：车队 trigger 和影子模式，接到 LLM 评测失败怎么说？
quick: "把车队 trigger 的思路换成「评测失败触发收集」：固定评测失败、judge 或人与 RM 的分歧、工具验证失败和低置信步骤，才值得进闭环，再用许可或合成数据复现。影子模式的输出不能当金标，用户没改摘要也不等于认可。可验证样本自动扩，主观难例按人工预算处理。"
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
updatedAt: 2026-10-12
sources:
  - title: Tesla AI Day 2022
    url: https://www.youtube.com/watch?v=ODSJsviD_SU
    type: primary
  - title: Tesla AI
    url: https://www.tesla.com/AI
    type: primary
  - title: How Do You Train Autonomous Vehicles for the Toughest Edge Cases? (Scale)
    url: https://learn.scale.com/public/blogs/qanda-how-do-you-train-autonomous-vehicles-for-the-toughest-edge-cases
    type: secondary
---

可以借车队 trigger 的思路，把触发源换成评测失败：固定评测中的失败任务、两个 judge 或人与 RM 判断不一致的偏好对、工具任务里的验证失败、空结果和低置信步骤。进入下一轮的是这些题目，以及用许可或合成数据做的复现。

## 为什么要用 trigger

Tesla AI Day 和 Scale 的 AV 讲座都讲过：车队每秒都在产生数据，有用的只是那一小段失败。Karpathy 早期说过，99.9% 的时间都很好开，要找的是那 0.1%。Scale 举的例子是阴影被当成车道线，于是专门去挖同类光照下的下匝道 clip。随机采样在这种分布下几乎拿不到有用样本。

车队回传的条件是低置信、多相机互斥或人机分歧；LLM 这边对应的是评测失败触发收集，数据来源用许可或合成复现，不默认上传用户原文。影子模式的输出也不能当金标：车上如此，LLM 上「用户没改摘要」同样不能当 chosen。

## 怎么做

1. 定触发源：评测失败、评分分歧、工具异常和低置信步骤。研究集还要覆盖产品将要新增、但评测还没包含的任务，见 `dt-novel-bootstrap`、`dt-see-around-corners`。
2. 复现失败类型：用许可或合成数据复现，不默认回收用户数据。
3. 按可验证性分层：可验证的样本自动扩充，无法验证的交给有限的人工预算，见 `dt-human-budget`。这里的带宽约束是人时和 GPU，不能把所有失败都合成十遍。
4. 管标签质量：参考标签仍需协议和抽查，见 `dt-annotator-protocol`。

LLM 上对应影子模式的检查，是让新模型在旧评测上运行并和旧模型对比，线上的隐式点击不当标签。失败太稀时就提高触发召回，离线再筛。稀有 locale 和工具路径用合成补，等它自然出现，往往要等到线上出事故。

## 追问

- **和 us-tech 的 Tesla 卡怎么分？** `tesla-data-engine` 讲车端闭环，包括延迟、占用和自动标注几何；这张卡只回答选什么进闭环。
