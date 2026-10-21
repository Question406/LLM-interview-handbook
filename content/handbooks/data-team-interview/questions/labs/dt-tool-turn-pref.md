---
id: dt-tool-turn-pref
section: labs
order: 22
level: A
title: Llama 3：工具对话按整段标偏好，还是按每一跳？
quick: "按每一跳标。在相同上下文中生成两条助手消息让人选择或编辑，把选中或编辑后的回答写回对话再继续。工具返回不能由标注员修改，也不作为偏好候选；调用对错交给可执行检查。整段只标一个成败，奖励模型会把运气算进调用质量，也定位不到哪一步出错。"
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

按每一跳标。整段只标一个「订到了餐厅」，看不出是哪一步做对、哪一步做错；按助手消息逐条比较，才能把偏好落到具体的调用和提问上。

## 为什么整段标不行

整段成功可能是参数对、返回也被读懂了，也可能是参数错了、用户后来口头纠正。整段一条偏好，奖励模型（RM）就会把运气算进调用质量。Llama 3 的工具章节写到，对话里常有多条助手消息（先调用，再读返回），所以他们在消息级收集人类反馈；标注员不能给工具输出打分，也不能改工具输出。

不能改工具返回的原因是：人改返回等于伪造环境，模型会学到「返回想成什么样就能什么样」。

## 怎么标

1. 在相同上下文下生成两条助手消息，让人选择或编辑。
2. 把 chosen 或 edited 写回上下文，再继续对话，下一跳在新的上下文上重复。
3. 分工：可执行的对错（schema 校验、状态核验）交给规则，不让人比。人比的是「这一跳该不该这样问用户、该不该换工具」。
4. 工具 observation 不计入训练 loss，也不写进偏好数据的 chosen 文本。
5. 每条轨迹记录对应的环境版本。不同工具环境的消息级标签混进同一个 mix 时，要记下 `surface`。

`dt-traj-quality` 已经写了监督微调（SFT）只留成功的主要执行路径，偏好数据也应该对齐这个结构。AFM 2025 报告的工具平台产出的是一棵树：成功的主要执行路径用于多轮 SFT，其他路径是被放弃的尝试。失败的尝试不要当 chosen；如果两条候选都有大问题，就改其中一条，改完的那条相当于 `dt-llama-edit-pref` 里的 edited。

## 追问

- **只标最后一句对用户说的话行不行？** 能抓语气，抓不住中间的坏调用，而事故多半出在中间。
- **两条候选谁来生成？** 用不同策略或不同温度。同一策略生成的两条太接近，标注员会选「差不多」，样本就被丢掉了。
