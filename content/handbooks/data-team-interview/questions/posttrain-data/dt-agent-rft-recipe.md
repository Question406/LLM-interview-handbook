---
id: dt-agent-rft-recipe
section: posttrain-data
order: 29
level: S
title: OpenAI Agent RFT talk：他们让客户怎么写环境和奖励？
quick: "先在接近生产的任务分布上跑基线，把 prompt、任务范围和工具调好，确认还有提升空间再上 RFT。每条 rollout 用独立环境；奖励以正确性为门，过了门再加风格分，别给「尝试」部分分。多次采样都找不到更好的解，训练就没有学习信号。"
companies:
  - apple
tags:
  - Apple
  - Agent
  - RL
  - OpenAI
realInterview: false
status: published
format: markdown
updatedAt: 2026-10-12
sources:
  - title: "Agent Reinforcement Fine Tuning (Will Hang, Cathy Zhou)"
    url: https://ai.engineer/talks/agent-reinforcement-fine-tuning
    type: primary
  - title: "Fine Tuning the Enterprise: Reinforcement Learning in Practice"
    url: https://www.infoq.com/presentations/rft-openai-model/
    type: secondary
  - title: Reinforcement fine-tuning (OpenAI)
    url: https://developers.openai.com/api/docs/guides/reinforcement-fine-tuning
    type: secondary
  - title: Apple Intelligence Foundation Language Models Tech Report 2025
    url: https://machinelearning.apple.com/research/apple-foundation-models-tech-report-2025
    type: primary
---

先别急着改权重。我会先让任务分布接近生产场景，用基座跑一遍基线，优先调 prompt、任务范围和工具集合；这些都做好之后如果还有提升空间，再考虑 RFT。RFT 能学的前提是多次采样里能出现更好的解，奖励也要以正确性为门槛。

## 公开配方怎么做

依据是 OpenAI 微调组 Will Hang 和 Cathy Zhou 的 Agent RFT talk。训练时模型调用你托管的 tool 端点，一条采样轨迹（rollout）结束后再调用你的 grader 端点。他们强调，这是 OpenAI 第一次让训练过程接触客户环境。

数据量上，Will 说有人用大约 10 条就训出了变化，这只是 talk 里展示样本效率的例子，别当成论文给出的最小 $N$。Cognition 那组据称约 100 条提升 5 分，1000 条提升 10 分。现场的结论是数据要「小而干净、对齐生产」，10 条只是个例子。

## 环境怎么搭

每条轨迹一个隔离的 VM 或容器。Cognition 给 Devin 的规划阶段单独起虚拟机，各条 shell 互不串扰。每条 rollout 分配一个 UUID，所有工具调用都挂在这个 ID 下。这样 grader 能检查模型中间每一步做了什么，最后一句回答只是其中一部分。

工具预算也可以写进奖励。幻灯片上的例子是：超过 10 次调用给 $-1$，正常收尾给 $0.7$。Qodo 训完之后，长尾的 15 次以上调用消失了，集中到 2 到 4 次。

## 奖励怎么设计：三个案例

**Cognition。** 用户 query 对应用户真正改过的文件，奖励是文件集合的 F1：精确率检查有没有选错文件，召回率检查有没有漏掉该改的文件。训完之后，规划从 8 到 10 步收敛到约 4 步，并且学会了第一步就并行搜索。

**Cosine。** 有 30 个工具。早期给「尝试」部分分，结果模型去优化文风。后来改成测试不过奖励就是 0；过了测试再用 LLM 打风格分、罚 emoji，并奖励模型自己跑测试和 lint。奖励变稀疏后，就加大 batch，让每组里能出现正例。选 GPT-5 当基座，是因为它已经能采到成功轨迹。

**Mako（GPU kernel）。** 大约 100 条 PyTorch prompt。先查 hack：直接交参考实现、空 kernel、恒等 kernel，法官模型给这些打零分，再用 AST 确认 kernel 真的 launch 了。之后才评正确性和相对 PyTorch 的加速。Cathy 报了后续数字，记住「先堵 hack 再看速度」这个顺序就行，不必背那个百分比。

Will 最后总结了四条：成功定义清楚；数据像生产；多次采样能找到更好的解；堵住 hack，可以有连续奖励，但部分分不能替代正确性。这和 `dt-agent-reward-spec`、`dt-agent-passk-zero` 的结论一致。它和公开的 SWE 强化学习（RL）也是同一套结构：隔离环境、轨迹级奖励、正确性门，差别只是客户环境放进了训练环。

## 追问

- **grader 用模型行不行？** 主门我仍然用测试或状态检查。他们 FinQA 的例子用模型 grader，是为了吃下答案格式上的差异。除此之外，模型打分只用在过门之后评风格。
