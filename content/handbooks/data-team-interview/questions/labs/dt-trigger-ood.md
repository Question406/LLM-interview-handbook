---
id: dt-trigger-ood
section: labs
order: 11
level: A
title: Tesla / Scale：车队 trigger 和影子模式，接到 LLM 评测失败怎么说？
quick: "优先收集固定评测失败、评分分歧和工具异常等有信息的样本，再用许可或合成数据复现。用户未修改摘要，不等于认可，更不能直接当 SFT 金标。可验证样本自动扩，主观难例按人工预算处理。"
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

可以根据固定评测中的失败任务，或两个 judge、人和 RM 判断不一致的偏好对，触发数据收集。工具任务重点收集验证失败、空结果和低置信的步骤；研究集还要覆盖产品将新增、但评测尚未包含的任务，见 `dt-novel-bootstrap`、`dt-see-around-corners`。用于下一轮的是这些评测题及其许可或合成复现，不能默认回收用户收件箱。参考标签仍需协议与抽查，见 `dt-annotator-protocol`。

不这么选的理由：把车队「低置信、多相机互斥、人机分歧才回传」听成上传用户原文。随机采样也错。影子模式输出不能当金标：车上不能，LLM 上「用户没改摘要」同样不能当 chosen。

接到苹果：对应的影子检查是让新模型在旧评测上运行并对比，不把线上隐式点击当标签。带宽约束在这边是人时和 GPU，不能把所有失败都合成十遍。按任务分层：可验证的样本自动扩充，无法验证的交给有限人工预算，见 `dt-human-budget`。失败太稀就提高触发召回，离线再筛；稀有 locale / 工具路径用合成补，等自然出现会等到产品事故。us-tech 里 `tesla-data-engine` 写车端闭环，这张卡只答选什么进闭环。

公开锚点：Tesla AI Day / Scale AV 讲座：车队每秒都在产生数据，有用的是那一小段失败；Karpathy 早期讲过 99.9% 的秒很好开，要找那 0.1%。Scale 的例子是阴影被当成车道线，专门挖同类光照的下匝道 clip。

## 追问

- **影子模式能当 监督微调（SFT） 标签吗？** 车上不能。LLM 上「用户没改摘要」同样不能当 chosen。
- **失败太稀？** 提高触发召回，离线再筛。稀有 locale / 工具路径用合成补，等自然出现会等到产品事故。
- **和 us-tech Tesla 卡怎么分？** 车端延迟、占用、自动标注几何去那边。这里只答「选什么进闭环」。
