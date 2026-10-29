---
id: pt-where-reasoning-comes-from
section: posttrain
order: 248
level: A
title: LLM 的推理能力主要是在哪一段训练里长出来的？
quick: >-
  分四段讲：预训练提供知识和推理的潜在模式，SFT 把它们整理成可读的步骤和格式，RL / RLVR 把概率质量推向能通过 verifier 的长 CoT
  和自检，distillation 再把这些行为迁到小模型。评测涨了，要先分清涨的是格式、覆盖还是新路径。
tags:
  - Reasoning
  - Pretrain
  - SFT
  - RLVR
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-23T00:00:00.000Z
sources:
  - title: DeepSeek-R1
    url: 'https://arxiv.org/abs/2501.12948'
    type: primary
  - title: Does RL Really Incentivize Reasoning Beyond the Base Model?
    url: 'https://arxiv.org/abs/2504.13837'
    type: primary
  - title: ProRL
    url: 'https://arxiv.org/abs/2505.24864'
    type: primary
---

推理能力是分段长出来的，我会分四段讲：预训练给知识和潜在的推理模式，SFT 把它整理成可读的步骤和格式，RL 把概率推向能拿分的长推理和自检，distillation 再把这些行为迁到小模型上。说「推理是 RL 训出来的」，或者「全靠预训练，后训练只是对齐格式」，都只说了一段，分层讲，面试官才能逐段追问失败模式。pretrain 和 SFT 各解决什么，拼多多那张卡单独问过，见 `pdd-pretrain-vs-sft`，这里把 RL 和 distillation 接上。

一个直观的例子是 R1-Zero：它从 base 直接做 GRPO，就冒出了长思考和自检。可前提是 base 已经见过相关的模式，没有足够强的底座，RL 很难凭空变出复杂算法。

## 四段各贡献什么

预训练学的是语言、世界知识、程序和数学的统计结构，这是后面一切的上限。

SFT / cold-start 把能力变成能用的行为：按步骤写、把答案框出来、输出合法 JSON、遵守工具调用格式。它不负责探索没见过的解法，示范要是错了，RL 还会把错格式一起放大。生产上仍然常用少量高质量的 chain of thought（CoT，即分步推理过程）冷启动，再进 RL，见 `pt-cold-start-to-multistage-rl`。

RL / RLVR 改的是策略分布。可验证奖励把概率推向能拿分的轨迹：更长的 CoT、复查、换一种拆题方式。它能提高 pass@1，但也可能只是在已有解法之间重新加权，见 `pt-r1zero`、`pt-rlvr-discovery-vs-reweighting`。开放式任务用 reward model（RM）时，这一段学的可能是讨好 judge，不一定是真推理。

distillation 把强模型的推理轨迹压到学生身上。On-policy distillation 在学生自己的状态下给稠密的教师信号，比离线 SFT 更贴近推理时的分布，见 `pt-on-policy-distillation`。学生的上限仍然被教师和 base 卡着。

## 别用一个阶段解释产品表现

评测涨了，先问涨的是格式、覆盖还是新路径。只做 SFT，指令遵循会变好，竞赛数学往往不够；只做短 RL，pass@1 好看，换个分布就回退；只堆预训练数据不管后训练，模型会做题，却不会按你的协议输出。DeepSeek 公开的路线可以当参照：V3 把 MoE / MLA / 负载均衡做进底座，再接 SFT+RL；R1 把面向推理的 RL 配方写清楚了；V3.2 公开的重点是稀疏 attention 和长上下文效率，报告里没写的 RL 细节别去编。

现场可以用三句话收住：预训练给潜在电路，SFT 给可读接口，RL 给高奖励轨迹加权重。要是被追问「RL 到底有没有创造能力」，就拿 pass@K 的对照实验回答，光用形容词判断不了。

## 追问

**为什么小模型做 RL 常常更难？**
base 能做对的题本来就少，组内全错的比例高。先用 distillation 或冷启动把 $p$ 抬过临界区，再做 RL，见 `tencent-small-model-rl-changes`。

**指令预训练算哪一段？**
仍然算底座，就是把指令数据提前混进 pretrain 的配比里，这不等于已经对齐到产品格式。

**过程奖励能替代预训练吗？**
不能。过程信号只改变 credit assignment，补不了知识上的空洞。
