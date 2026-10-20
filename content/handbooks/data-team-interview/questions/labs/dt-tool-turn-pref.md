---
id: dt-tool-turn-pref
section: labs
order: 22
level: A
title: Llama 3：工具对话按整段标偏好，还是按每一跳？
quick: "按助手消息逐步标偏好：在相同上下文中比较候选，再把选中或编辑后的回答写回对话继续。工具返回不能由标注员修改，也不作为偏好候选。可执行检查负责判断调用是否正确；仅按整段成功与否评分，很难定位哪一步出了问题。"
companies:
  - apple
tags:
  - Meta
  - Tool Use
  - Preference
  - Apple
realInterview: false
status: published
format: markdown
updatedAt: 2026-10-12
sources:
  - title: The Llama 3 Herd of Models
    url: https://arxiv.org/abs/2407.21783
    type: primary
  - title: Apple Intelligence Foundation Language Models Tech Report 2025
    url: https://machinelearning.apple.com/research/apple-foundation-models-tech-report-2025
    type: primary
  - title: Toolformer
    url: https://arxiv.org/abs/2302.04761
    type: primary
---

在相同上下文下生成两条助手消息，让人选择或编辑。将 chosen / edited 写回上下文，再继续对话。标注员不能给工具输出打分，也不能改工具输出。可执行的对错（字段和类型规范（schema）、状态核验）走规则，不要用人比。人比的是「这一跳该不该这样问用户 / 该不该换工具」。工具 observation 不计入训练 loss，也不写进偏好数据的 chosen 文本。每条轨迹要记录对应的环境版本。`dt-traj-quality` 已经写了 监督微调（SFT） 留成功的主要执行路径，这张卡把偏好标到跳。

不这么选的理由：按整段终局标「订到了餐厅」。可能是参数对、返回被读懂，也可能是参数错、用户后来口头纠正。整段一条偏好，奖励模型（RM） 会把运气算进调用质量。人改工具返回是在伪造环境，模型会学到「返回想成什么样就能什么样」。

接到苹果：AFM 工具平台吐树：成功的主要执行路径合法多轮 SFT，其他尝试路径是放弃的尝试。偏好数据应对齐这棵树。失败的尝试不要当 chosen；两条都有大问题就改其中一条，改完的那条像 `dt-llama-edit-pref` 的 edited。端侧工具更短，PCC 上更长，两边的 message 级标签不要混成一个 mix 还不记 `surface`。候选来自研究集或合成复现，用户原文不进。

公开锚点：Llama 3 工具节写对话里常有多条助手消息（先调用，再读返回），他们在消息级收人反馈；标注员不能给工具输出打分，也不能改工具输出。

## 追问

- **只标最后一句对用户的话？** 能抓语气，抓不住中间坏调用。产品事故多半在中间。
- **两条候选谁来生成？** 不同策略或不同温度。同一策略两条太近，会落到「差不多」被丢掉。
- **人能不能改工具返回来教模型？** 不能。那是在伪造环境。模型会学到「返回想成什么样就能什么样」。
