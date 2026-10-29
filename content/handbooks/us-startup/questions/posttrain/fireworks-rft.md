---
id: fireworks-rft
section: posttrain
order: 4
level: A
title: Fireworks：客户只写一个打分函数，没有偏好对
quick: >-
  假设客户给每条回答一个可执行评分函数，例如检查生成的 tool call 参数是否正确。现有数据是输入、回答和分数，未必有同一输入下的
  chosen/rejected pair。
tags:
  - Fireworks
  - RLVR
  - Post-training
  - Reward
  - 口述改写 2026-10-28
realInterview: false
status: published
format: markdown
updatedAt: '2026-10-28'
sources:
  - title: Reinforcement Fine Tuning
    url: 'https://fireworks.ai/blog/reinforcement-fine-tuning'
    type: primary
  - title: 'Cheaper Tokens, Smarter Models, Benny Chen'
    url: 'https://www.opensourceceo.com/p/benny-chen-interview'
    type: primary
  - title: 'Software Engineering Daily, Fireworks AI transcript'
    url: >-
      https://softwareengineeringdaily.com/wp-content/uploads/2026/03/SED1919-FireworksAI.txt
    type: primary
---

## 回答思路

> **问题与场景：** 假设客户给每条回答一个可执行评分函数，例如检查生成的 tool call 参数是否正确。
>
> **做法与原因：** 这更自然地对应基于 reward 的训练：模型生成候选，评分程序执行检查，再用反馈更新策略。
>
> **检查与取舍：** 我会先测试评分函数能否被钻空子，再用独立任务衡量效果。

## 可以这样回答

假设客户给每条回答一个可执行评分函数，例如检查生成的 tool call 参数是否正确。现有数据是输入、回答和分数，未必有同一输入下的 chosen/rejected pair。

这更自然地对应基于 reward 的训练：模型生成候选，评分程序执行检查，再用反馈更新策略。若想做 DPO，还需要构造成对比较，不能把一个分数直接当成 preference pair。

我会先测试评分函数能否被钻空子，再用独立任务衡量效果。这里讨论的是公开产品方向的准备场景。

## 技术备查

客户能写出打分函数时，我会直接把分数当奖励做 RL；格式本身难学，就先拿少量演示做一轮 SFT。Fireworks 的强化微调产品采用的就是这条路径，客户不用先准备 DPO 所需的偏好对。

先交代题的来历。Fireworks 没有公开的后训练面经逐字稿，`realInterview: false`。联合创始人 Benny Chen 在访谈里讲过他们怎么卖后训练，博客把产品叫 Reinforcement Fine-Tuning，面这家的训练或推理岗，面试官多半会追这个产品。博客的定义很简单：客户写一个 Python 函数给模型输出打分，其余的编排和训练由平台运行。它适合答案能被自动批改的任务，博客把这称为 RLVR，支持的基座包括 Llama、Qwen、DeepSeek。

拿博客里的函数调用当例子：客户手里每条 prompt 配一个标注好的正确调用，打分函数把模型生成的调用和这个 ground truth 一比，返回一个分。这时数据是 $(x, y, s)$，$s$ 是打分函数的返回值。DPO 要的是同一条 prompt 下的 chosen 和 rejected，这里只有一个回答和一个分数，凑不出一对。

$s$ 能验证，我就直接拿它当奖励做 RL，不必先训 reward model。函数调用按 schema 做精确匹配或者跑单测，奖励稀疏，可是很难钻空子，模型写得再长也骗不过编译器。打分函数要是另一个 LLM，就得把它当成一个会偏长度、偏位置的裁判来防，和 Snorkel 在 `snorkel-iterative-dpo` 里碰到的是同一类问题。

格式本身很怪的时候，比如严格的 JSON、固定的工具名，我会先用少量正确演示做 SFT，把模型带进格式，再用打分函数做 RL。只做 RL 的话，大量 sampling 落在格式外面，奖励几乎全是 0，梯度没有方向。博客里的函数调用例子就是 SFT 和 RFT 叠着用的。博文还说有个客户案例，32B 开源模型用 SFT 加这套强化微调，在客户自己的评测上超过了 GPT-4o。这是客户的评测，没上公开榜。

Chen 讲旧的定制是这样做的：要有会管标注员的 MLE，标注员得固定一批才不丢上下文，来回两个月才拿到 SFT 数据。新路径是让能写清「什么算好」的人交一段裁判代码。裁判写错了，模型会把错的标准学进去，所以裁判本身也要有测试。

他还强调了两件和环境有关的事。一是训练用的数值要和推理引擎一致：训练在一种 kernel、一种精度上把奖励刷高，上线换一套 kernel，同样的输出 token 对不上，奖励优化的就不是你实际服务的那个模型。二是别在模拟器里训完再丢进生产，他们让人从生产追踪里取轨迹做 RL。这样一来，生产环境要是没隔离，策略在学习时就能执行真实的副作用，他举的例子是训练过程中把数据库删了。所以有写操作的工具，在训练里换成只记录调用、不执行，或者打到沙箱，只读工具才可以连真实依赖。

## 追问

**打分函数返回连续分还是 0/1？**
精确匹配就是 0/1，麻烦在一组 sampling 容易全 0，GRPO 的组内标准差是 0，这组没有优势。可以先加一个只看格式的部分分，权重远小于对错，免得模型只学格式。

**裁判和被训的模型能是同一个吗？**
最好别。同一份权重的话，模型可以生成裁判喜欢的口吻给自己加分。裁判用冻结的另一份权重，再抽一批人看过的例子，看裁判分和人的相关系数。

**客户评测上超过 GPT-4o，说明什么？**
只说明在那份私有集、那个打分函数下分更高。打分函数本身就是优化目标，报分上升只是目标上升，想说明模型真的变好，还要一份没进训练的人评。
