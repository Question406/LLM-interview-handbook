---
id: dt-agent-rft-recipe
section: posttrain-data
order: 29
level: S
title: OpenAI Agent RFT talk：他们让客户怎么写环境和奖励？
quick: "先在接近生产任务的环境中跑基线，改好 prompt、任务范围和工具，再看是否还有值得 RFT 改善的空间。每条 rollout 使用独立环境，最终奖励先检查正确性，通过后再加风格分；采样找不到更好解时，训练缺少学习信号。"
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

先让任务分布接近生产场景，用基座跑一遍基线。优先调整 prompt、任务范围和工具集合，如果这些都做好后仍有提升空间，再考虑 RFT。公开锚点是 OpenAI 微调组 Will Hang、Cathy Zhou 的 Agent RFT talk：训练时模型打你托管的 tool 端点，采样轨迹（rollout） 结束再打你的 grader 端点。他们强调这是 OpenAI 第一次让训练过程碰到客户环境。

常见误区是：一上来改权重，或给「尝试」部分分。模型会去优化文风；探索采不到更好的解，就没有学习信号。

Will 说有人用大约 10 条就动过。这是 talk 里的样本效率例子，不是论文里的最小 $N$。Cognition 那组：约 100 条据说抬 5 分，1000 条抬 10 分。现场报「小而干净、对齐生产」，别把 10 当 SLA。

## 环境

每条轨迹一个隔离 VM / 容器。Cognition 给 Devin 的规划阶段单独起虚机，shell 互不串。每条 rollout 一个 UUID，所有 工具调用 挂这个 ID，grader 才能看「做了什么」而不只看最后一句。

工具预算可以写进奖励：超过 10 次调用给 $-1$，正常收官给 $0.7$（幻灯片上的例子）。Qodo 训完长尾 15+ 次调用消失，集中到 2 到 4 次。

## 奖励

Cognition。用户 query 对上用户真正改过的文件，奖励是文件集合 F1。精确率检查有没有选错文件，召回率检查有没有漏掉该改的文件。规划从 8 到 10 步收到约 4 步，而且学会第一步并行搜。

Cosine。30 个工具。早期给「尝试」部分分，模型去优化文风。改成：测试不过，奖励就是 0。过了测再用 LLM 打风格、罚 emoji，并奖励自己跑测 / lint。稀疏了就加大 batch，让组里出现正例。GPT-5 当基座是因为已经能采到成功轨迹。

Mako（GPU kernel）。大约 100 条 PyTorch prompt。先查 hack：交参考实现、空 kernel、恒等 kernel。法官模型打零，AST 确认 kernel 真的 launch。然后才打正确性和相对 PyTorch 的加速。Cathy 报了后续数字，现场当「先堵 hack 再打速度」，不要背那个百分比。

Will 收四条：成功定义清楚；数据像生产；多采样能找到更好解；堵 hack，连续奖励可以有，但别让部分分替代正确性。和 `dt-agent-reward-spec`、`dt-agent-passk-zero` 对得上。

苹果：许可仓库、合成环境、参考模型。用户生产流量默认不进基础模型，不能照抄「对齐生产用户日志」。能对齐的是许可环境里的任务分布。

## 追问

- **grader 用模型行不行？** 主门我会仍用测试 / 状态。他们 FinQA 例子用模型 grader 吃格式差。模型分只能打过门之后的风格。
- **和公开 SWE 强化学习（RL）？** 同一套：隔离环境、轨迹级奖励、正确性门。差别是客户环境在训练环里。苹果侧客户环境换成许可仓库或合成环境。
- **苹果怎么对齐生产？** 对齐许可环境里的任务分布，不把用户会话灌进基础模型。
