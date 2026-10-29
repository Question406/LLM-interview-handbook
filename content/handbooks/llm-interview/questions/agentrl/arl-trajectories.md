---
id: arl-trajectories
section: agentrl
order: 1
level: S
title: 为什么只训练成功 Agent Trajectories 不够？
quick: "成功的教师轨迹只教了正确状态下该做什么。学生一步走偏，就进入训练里没见过的状态，又没学过怎么恢复，错误越滚越大，这就是模仿学习的 compounding error。所以数据里还要有 near-miss、recovery 和该停的失败。"
tags:
  - Agent Data
  - Imitation Learning
realInterview: false
status: published
format: markdown
provenance: legacy-handbook-v2
updatedAt: 2026-08-21
sources:
  - title: DAgger
    url: https://arxiv.org/abs/1011.0686
    type: primary
---

因为成功轨迹只教了「在正确状态上做正确动作」。部署时学生一步走偏，后面的观测就离开了教师分布，它没学过怎么恢复，错误会一路累积。这是模仿学习的老问题，DAgger 讲的就是这种 compounding error。

比如一个 Agent 打开文件时选错了文件，教师轨迹里从来没出现过「打开了错误文件」这个状态，学生就会在坏状态下继续「假装自己还在成功轨迹上」，接着往错的地方改。教师 $\pi_T$ 很少进入学生 $\pi_S$ 常去的那些坏状态，失败洗得越干净，部署时越不会修。

所以数据要覆盖几类：干净的成功；绕路但成功的，用来做效率偏好；near-miss，只错了关键一步；recovery，发现错误并修好；不可恢复的失败，这时该停或者该问用户；还有澄清，正确动作是去要信息。成功演示负责「会做」，near-miss 和 recovery 负责「做错了怎么办」，不可恢复失败负责「该停」。缺了中间两类，SFT 的 loss 看着很低，一上线就在坏状态里空转。

失败轨迹也不能整条当正例做 SFT，那样会模仿错误动作。我会标 first-error：前缀可以留作正的上下文，错误那一步当 rejected，后面要是有 recovery，就把 recovery 那段当正目标；或者走 preference、逐步标注，别对整条失败做行为克隆。这和 `data-hard-negative` 构造 pair 是同一个思路，区别在于这题关心的是状态分布，一条 rejected 文本解决不了。

near-miss 最干净的造法，是从成功轨迹复制一份，只换掉一个关键 action，然后真实执行，拿到后面的失败，这样 credit 很干净。另外 on-policy 采集、error injection、人在环纠正都能把分布拉回来，DAgger 式的做法就是把学生走到的状态交给专家标动作，去学生会去的状态上标，别只在教师状态上模仿。RL 能吃自己的失败，但需要奖励或偏好，不然会学会失败的样子。采集时顺手记下失败原因，参数错、权限、超时、过早结束，否则失败轨迹没法切片，只能当噪声丢掉，又回到只有成功的数据。

## 追问

**怎么构造 hard negative trajectory？**
从成功轨迹复制，只替换一个关键 action，再真实执行拿到后续 failure。前后上下文保持相似，credit 才干净；整条打乱的话，模型学到的只是「轨迹不像」。

**这题和 `data-hard-negative` 有什么不同？**
那题讲 pair 怎么构造、怎么避开 confound；这题讲状态分布和 compounding error。没有 near-miss 和 recovery，只堆 rejected 文本，模型还是不会修。

**评测只看专家轨迹上的 action match 够吗？**
不够。只回放教师成功路径，会把「不会修」藏起来。评测集要主动注入 first-error，看恢复率、该停的时候停没停、near-miss 有没有被修好。只靠成功演示训出来的 SFT，这几个数都会接近零。
