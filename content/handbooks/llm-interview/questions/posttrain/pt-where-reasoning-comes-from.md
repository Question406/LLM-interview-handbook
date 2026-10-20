---
id: pt-where-reasoning-comes-from
section: posttrain
order: 248
level: A
title: LLM 的推理能力主要是在哪一段训练里长出来的？
quick: "预训练提供知识和推理的潜在模式；SFT 把它们整理成可读的步骤和格式；RL / RLVR 把概率质量推向能通过 verifier 的长 CoT 和自检；蒸馏再把这些行为迁到小模型。"
tags:
  - Reasoning
  - Pretrain
  - SFT
  - RLVR
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-23
sources:
  - title: DeepSeek-R1
    url: https://arxiv.org/abs/2501.12948
    type: primary
  - title: Does RL Really Incentivize Reasoning Beyond the Base Model?
    url: https://arxiv.org/abs/2504.13837
    type: primary
  - title: ProRL
    url: https://arxiv.org/abs/2505.24864
    type: primary
---

常见误区是：「推理是 RL 训出来的」或「全是预训练，后训练只是对齐格式」。分层讲，面试官才能追每一段的失败模式。拼多多那张卡问的是 pretrain vs 监督微调（SFT） 各解决什么，见 `pdd-pretrain-vs-sft`；本题把 强化学习（RL） 和蒸馏接上。

## 四段各自贡献什么

**预训练** 学语言、世界知识、程序和数学的统计结构。没有足够强的 base，后面的 RL 很难凭空变出复杂算法。R1-Zero 从 base 直接 GRPO，能冒出长思考和自检，前提仍是 base 已经见过相关模式。

**SFT / cold-start** 把能力变成可用行为：按步骤写、框答案、合法 JSON、工具调用格式。它不负责探索没见过的解；示范错了，RL 会把错格式也放大。生产上仍常用少量高质量 思维链（CoT，即分步推理过程） 冷启动，再进 RL，见 `pt-cold-start-to-multistage-rl`。

**RL / 基于可验证奖励的强化学习（RLVR）** 改策略分布。可验证奖励把质量推向能拿分的轨迹：更长 CoT、复查、换一种拆题。它可以提高 pass@1，也可能只是重加权，见 `pt-r1zero`、`pt-rlvr-discovery-vs-reweighting`。开放式任务用 奖励模型（RM） 时，这一段还在学「讨好 judge」，不一定是真推理。

**蒸馏** 把强模型的推理轨迹压到学生上。On-policy 蒸馏在学生自己的状态下给稠密教师信号，比离线 SFT 更贴推理分布，见 `pt-on-policy-distillation`。学生能力上限仍受教师和 base 卡住。

## 不要用一个阶段概括产品表现

评测涨了，先问涨的是格式、覆盖还是新路径。只做 SFT，指令遵循会好，竞赛数学往往不够。只做短 RL，pass@1 好看、换分布就回退。只堆预训练数据不管后训练，模型会做题但不会按你的协议输出。DeepSeek 公开线是：V3 把 MoE / MLA / 负载均衡做进底座并接 SFT+RL；R1 把推理向 RL 配方写清楚。V3.2 公开重点是稀疏注意力和长上下文效率，不要把没写进报告的 RL 细节编出来。

现场三句：预训练给潜在电路，SFT 给可读接口，RL 给高奖励轨迹的权重。被追「那 RL 有没有创造能力」，应给出 pass@K 对照实验，而不是只用形容词判断。

## 追问

- **为什么小模型 RL 常常更难？** base 的可达成功集更小，组内全错比例高。先蒸馏或冷启动把 $p$ 抬过临界区，再 RL，见 `tencent-small-model-rl-changes`。
- **指令预训练算哪一段？** 仍属底座：把指令数据提前混进 pretrain 配比。不等于已经对齐到产品格式。
- **过程奖励能替代预训练吗？** 不能。过程信号只改变信用分配，不补知识空洞。
