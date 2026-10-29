---
id: dt-case-web-internalize
section: cases
order: 4
level: S
title: 案例 3/4：用 rejection sampling + SFT + RL 把 skill 训进模型，哪些样本算好数据？
quick: >-
  带着 skill sampling，用渲染、功能、视觉三道检查过滤，训练时把 skill 从 prompt 里拿掉做 SFT，之后再上
  RL。最值钱的样本是「不带 skill 失败、带 skill 成功」的那些，它们正好是 skill 补上的能力。
companies:
  - apple
tags:
  - Apple
  - Synthetic Data
  - RL
  - Agent
  - Data Story
realInterview: false
status: published
format: markdown
updatedAt: 2026-10-22T00:00:00.000Z
sources:
  - title: 'Learning by Distilling Context (Snell, Klein, Zhong)'
    url: 'https://arxiv.org/abs/2209.15189'
    type: primary
  - title: 'STaR: Bootstrapping Reasoning With Reasoning'
    url: 'https://arxiv.org/abs/2203.14465'
    type: primary
  - title: >-
      Beyond Human Data: Scaling Self-Training for Problem-Solving with Language
      Models (ReST-EM)
    url: 'https://arxiv.org/abs/2312.06585'
    type: primary
  - title: >-
      ReLook: Vision-Grounded RL with a Multimodal LLM Critic for Agentic Web
      Coding
    url: 'https://arxiv.org/abs/2510.11498'
    type: primary
  - title: 'Thinking Machines: On-Policy Distillation (Kevin Lu)'
    url: 'https://thinkingmachines.ai/blog/on-policy-distillation/'
    type: secondary
  - title: 'Skill-SD: Skill-Conditioned Self-Distillation for Multi-turn LLM Agents'
    url: 'https://arxiv.org/abs/2604.10674'
    type: primary
---

简单说，带着 skill 让模型自己生成，把不合格的滤掉，训练时把 skill 拿掉，让模型不看规则也能做出同样的页面，之后再上 RL。

sampling 时每个 prompt 带着 skill 生成〔填：N〕个候选，依次过三道检查。先看能不能渲染，这一步最便宜，大部分废样本在这里就挡掉了；再跑功能测试；最后让 VLM 按 checklist 打视觉分。

过滤完，我们把每个 prompt 不带 skill 也跑了一遍，留哪些数据主要靠这一步。两边都能过的题，模型本来就会，留一点防遗忘就够了；两边都过不了的，skill 也帮不上，记下来以后另外造数据；只有带 skill 才过的那些，正好是 skill 补上的能力，优先留，还加了权重。另外，同一个 prompt 的多个通过样本，按字体、配色、布局聚一下类，每类只留一个，免得模型又学出一种新的默认风格。〔填：你们有没有遇到过风格单一，怎么发现的。〕

SFT 的输入只放原始任务，输出是带 skill 时生成的页面。训完看两件事：不带 skill 的新模型，分数要接近带 skill 的老模型；其他能力，比如通用对话和别的代码任务，不能掉。

SFT 之后上 RL。奖励一层层叠上去：渲染不出来直接 0 分，功能测试按通过的比例给分，再加上视觉分。〔填：权重和算法。〕视觉 judge 最容易被钻空子，比如堆渐变、堆大字，或者首屏很漂亮、下面全空着，所以截图要全页、多个时刻，judge 用和 policy 不同家族的模型，还要定期拿 human evaluation 对一下。数字 hallucination 的问题也和视觉奖励有关，见 `dt-case-web-grounding`。

## 追问

**这种做法有名字吗？**
就是 context distillation，Snell、Klein、Zhong 2022 年那篇：带着指令生成，再训模型不看指令也给出同样的答案。sampling 加过滤这部分和 STaR、ReST-EM 是一个思路。

**为什么不直接拿更强的模型做的网页来 SFT？**
可以拿来冷启动，但强模型的分布离自己的模型远，学到的多半是表面风格。自己的模型带着 skill 生成的样本离 student 近，distillation 起来更稳。

**怎么知道是学会了，还是记住了训练题？**
留一批训练里没出现过的行业或页面类型做 held-out。只在训练里见过的类别上涨，就是记住了。

**SFT 之后其他能力掉了怎么办？**
混一些通用数据，或者再做一轮 on-policy distillation 拉回来。Thinking Machines 的博客里有个例子：Qwen3-8B 只训内部文档之后 IF-eval 从 85% 掉到 45%，混了数据再做一轮 on-policy distillation，回到了 83%。

**RL 太贵，有没有便宜点的办法？**
让带 skill 的模型当 teacher、不带 skill 的当 student，在 student 自己的 rollout 上逐 token 做 distillation，每个 token 都有监督，比 RL 的稀疏奖励密得多。Skill-SD 在 AppWorld 上用这个办法比普通 GRPO 高 14%。

相关：`dt-case-web-skill`、`dt-rejection-sample-code`、`dt-math-passk-band`、`dt-forget-sft`、`dt-teacher-bias`
