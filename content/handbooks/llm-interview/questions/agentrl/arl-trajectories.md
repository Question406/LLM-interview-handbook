---
id: arl-trajectories
section: agentrl
order: 1
level: S
title: 为什么只训练成功 Agent Trajectories 不够？
quick: >-
  成功 teacher trajectories 只覆盖“正确 state distribution”。Student 一旦犯错进入 OOD
  state，就没有 recovery behavior，形成 imitation learning 的 compounding error。
tags:
  - Agent Data
  - Imitation Learning
realInterview: false
status: published
format: markdown
provenance: legacy-handbook-v2
updatedAt: 2026-08-19
sources:
  - title: DAgger
    url: 'https://arxiv.org/abs/1011.0686'
    type: primary
---

只 SFT 成功教师轨迹，学生学的是「正确状态上的正确动作」。部署时一步走偏，后续观测离开教师分布，没有恢复策略，错误会 compounding——这是模仿学习的老问题（DAgger）。陷阱是「成功率数据越干净越好」。教师 $\pi_T$ 很少进入学生 $\pi_S$ 常去的坏状态；你越清洗失败，部署时越不会修。

## 成功-only 缺的是恢复与近失败

理想数据应覆盖：干净成功；绕路成功（做效率偏好）；**near-miss**（只错关键一步）；**recovery**（发现错误并修）；不可恢复失败（该停、该问用户）；澄清（正确动作是要信息）。没有后几类，模型一旦选错文件或工具参数，就会在坏状态下继续「假装自己还在成功轨迹上」。

失败轨迹也不能整条当正 SFT，否则会模仿错误动作。更合理：标 first-error；prefix 可留；错误步做 rejected；若后续有 recovery，把 recovery suffix 当正目标。或走 preference / 逐步标注，而不是行为克隆整条失败。这和 `data-hard-negative` 的 pair 构造同一思想，但本题强调的是 **状态分布**，不只是一条 rejected 文本。

## 怎么补 near-miss：改一步，真实接着跑

主动构造：从成功轨迹复制，只替换一个关键 action，真实执行得到后续失败，credit 更干净。On-policy 采集、error injection、人在环纠正（DAgger 式把学生状态交给专家标动作）都能把分布拉回。RL 吃自己的失败，但需要奖励或偏好，避免学会「失败样子」。评测不要只报专家轨迹上的 action match；要看注入错误后的恢复率、该停时的停、以及 near-miss 是否被修。只有成功演示的 SFT，这些数都会接近零。

采集时记下失败原因（参数错、权限、超时、过早结束），否则失败轨迹无法切片，只能当噪声丢掉——那又回到成功-only。

配比上成功演示仍要有，负责「会做」；near-miss 与 recovery 负责「做错了怎么办」；不可恢复失败负责「该停」。缺中间两类，SFT 会看起来 loss 很低、一上线就在坏状态里空转。评测集应主动注入 first-error，而不是只回放教师成功路径。和 DAgger 对齐的说法是：去学生会去的状态上标动作，而不是只在教师状态上模仿。面试收口：成功-only SFT 没有恢复；要 near-miss、失败切片和 recovery，失败整条不当正例。采集时记下失败原因才能切片，否则失败轨迹只能当噪声丢掉，数据又缩回成功-only，部署时仍不会修，compounding 还会继续。

## 追问

- **如何构造 Hard Negative Trajectory？** 从成功轨迹复制，只替换一个关键 action，再真实执行得到后续 failure。保持前后上下文相似，credit 才干净，避免整条打乱变成「轨迹不像」。
- **如何从失败轨迹提取可训练数据？** 标 first-error：prefix 可留作正上下文，错误 action 做 rejected；若后面有 recovery，把 recovery suffix 当正目标。不要整条失败做 SFT。
- **和 hard-negative 数据题？** `data-hard-negative` 讲 pair 构造与 confound；本题强调状态分布与 compounding error。没有 near-miss/recovery，只堆 rejected 文本仍不会修。
- **评测只看专家轨迹匹配够吗？** 不够。要注入 first-error，看恢复率、该停时是否停。只回放成功教师路径，会把「不会修」藏过去。
