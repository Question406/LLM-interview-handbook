---
id: afm-director-mock
section: mock
order: 80
level: A
title: Director／VP 30 分钟模拟：预算、阶段选择与暂停 self-training
quick: 先给可执行决策，再用证据解释取舍。面试官连续改变预算、来源和风险约束，候选人须说明哪些结论保持、哪些需新实验，而不是每次重新堆术语。
companies:
  - apple
tags:
  - Apple
  - AFM 补全 2026-10
  - 全流程模拟
realInterview: false
status: published
format: markdown
updatedAt: '2026-10-26'
sources:
  - title: Scaling Laws for Reward Model Overoptimization
    url: 'https://arxiv.org/abs/2210.10760'
    type: primary
  - title: RewardBench 2
    url: 'https://arxiv.org/abs/2506.01937'
    type: primary
---

## 候选人起始材料
原创情景：你接手截图工具助手，公开榜涨5点，独立复杂任务降2点；proxy reward 涨，inference cost 涨40%；不能用私有截图做全球模型训练。只剩4周和一半原预算。请给本周决策、成功标准及暂停条件。所有数字均为虚构。

## 连续30分钟脚本
0–3分钟：用不超过60秒讲主项目或论文，随后说明当前方案的首要目标。
3–9分钟：选择本周最有价值的诊断与数据实验，说明减少什么投入。
9–15分钟：面试官问“为什么不直接上更多 SFT，pre/mid/post 如何选？”要求给竞争假设和阶段证据。
15–21分钟：追加“RM 和 teacher 同家族，线上 long-tail 只能看隐私聚合”；要求兼顾独立评价与合规复现。
21–26分钟：追加“self-training 连续三轮涨榜，但复杂任务不涨”；要求选继续、缩小还是暂停，并给可改变决定的新证据。
26–30分钟：用90秒总结人员/算力分配、里程碑、未确定事项及对合作团队的依赖。

## 参考决策框架
先审计指标与环境，冻结真正目标和关键风险。优先低成本受控诊断与一项可 attribution 数据干预，缩减未验证的大规模生成。保留独立评价和治理；不能因预算紧直接删掉。继续 self-training 的条件是独立任务收益及风险/成本满足预先约定，不以重复公开榜优化为证据。

模型阶段按缺口决定：基础覆盖、领域 continued pre-training、行为与工具协议分别比较；阶段定义依 training recipe，阶段名不能替代实验。线上聚合只能指导失败类别，复现用许可或合成材料，不能反向恢复用户内容。

## 评分及追问
五项各0–4：决策清晰、证据与反证、预算和阶段取舍、隐私与风险、简洁沟通。14分为自练通过线。
**如果你最支持的方案失败？** 给事前停止阈值、可恢复数据版本和下一条假设。
**VP 打断怎么办？** 先答“我建议__，依据__，本周用__验证”，细节留给追问。
**没有规模化证据？** 直接说明外推限制，提出 small model 结果到 large model 的验证预算，而非保证迁移。
