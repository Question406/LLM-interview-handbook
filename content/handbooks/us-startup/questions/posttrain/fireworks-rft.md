---
id: fireworks-rft
section: posttrain
order: 4
level: A
title: Fireworks：客户只写一个打分函数，没有偏好对
quick: "他们的强化微调吃的是一个给输出打分的 Python 函数，对应可验证奖励，不是 直接偏好优化（DPO） 的 chosen/rejected。 联合创始人把旧路径说成先找标注员做 监督微调（SFT）。训练和推理的数值要一致，并且不要在会写生产库的环境里训。"
tags:
  - Fireworks
  - RLVR
  - Post-training
  - Reward
realInterview: false
status: published
format: markdown
updatedAt: 2026-09-22
sources:
  - title: Reinforcement Fine Tuning
    url: https://fireworks.ai/blog/reinforcement-fine-tuning
    type: primary
  - title: Cheaper Tokens, Smarter Models, Benny Chen
    url: https://www.opensourceceo.com/p/benny-chen-interview
    type: primary
  - title: Software Engineering Daily, Fireworks AI transcript
    url: https://softwareengineeringdaily.com/wp-content/uploads/2026/03/SED1919-FireworksAI.txt
    type: primary
---

## 题怎么来的

Fireworks 没有公开的后培训面经逐字稿。联合创始人 Benny Chen 在访谈里讲他们怎么卖后训练，博客把产品叫做 Reinforcement Fine-Tuning。面这家的训练或推理岗，这就是他们会追的产品。`realInterview: false`。

博客的定义：你写一个 Python 函数给模型输出打分，其余的编排、训练他们来跑。适用面是答案能够被批改的任务，他们直接写成 基于可验证奖励的强化学习（RLVR）。支持的基座包括 Llama、Qwen、DeepSeek。例子是函数调用：打分函数把生成的调用和标注好的 ground truth 比较。博文说一个客户案例中，32B 开源模型用 监督微调（SFT） 加这套强化微调，在客户自己的评测上超过了 GPT-4o。这是他们的客户评测，不是公开榜。

## 没有偏好对时不能上 直接偏好优化（DPO）

DPO 需要同一条 输入提示（prompt） 下的 chosen 和 rejected。客户只有「这条约对不对」时，数据是 $(x, y, s)$，$s$ 是打分函数的返回值，不是一对回答。

能验证的 $s$ 我直接当奖励做 RL，不必先训奖励模型。函数调用按 schema 用精确匹配或单测，奖励稀疏，但是难钻：模型没法靠写长骗过编译器。打分函数若是另一个 LLM，它就是一个会偏长度和位置的裁判，和 Snorkel 在 `snorkel-iterative-dpo` 里碰到的是同一类问题。

格式本身很怪时（严格的 JSON、固定的工具名），我先用少量正确演示做 SFT，让模型进入格式，再用打分函数做 RL。只做 RL，大量采样在格式外，奖励几乎全是 0，梯度没有方向。博客里的函数调用例子就是 SFT 和 RFT 叠在一起。

Chen 把旧的定制说成：要有会管标注员的 MLE，标注员固定一批才不丢上下文，来回两个月才得到 SFT 数据。新路径是能写出「什么算好」的人交一个裁判片段。裁判片段写错，模型会把错的标准学进去，所以裁判本身要有测试。

## 训练环境就是线上环境

他强调训练用的数值和推理引擎一致。训练在一种 kernel、一种精度上把奖励刷高，换一套 kernel 上线，同样的输出 token 对不上，奖励优化的不是你服务的那个模型。

另一句是不要在模拟器里训、再丢进生产。他们让人从生产追踪里取轨迹做强化学习。生产环境若没有隔离，策略在学习时可以执行真实副作用。他举的例子是训练过程中把数据库删掉。有写操作的工具在训练里换成记录调用、不执行，或者打到沙箱。只读工具才可以打到真实依赖。

## 追问

**打分函数返回连续分还是 0/1？** 精确匹配是 0/1，组里容易全 0，GRPO 的组内标准差是 0，这组没有优势。可以先加一个只看格式的部分分，权重远小于对错，避免模型只学格式。

**裁判和被训模型是同一个吗？** 同一权重时，模型可以生成裁判喜欢的口吻给自己加分。裁判用冻结的另一份权重，并且抽一批人看过的例子看相关系数。

**客户评测超过 GPT-4o 说明什么？** 只说明在那份私有集、那个打分函数下更高。打分函数就是优化目标时，报分上升是目标上升，还要一份没进训练的人评。
