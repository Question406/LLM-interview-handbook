---
id: sys-rl-response-mask
section: systems
order: 30
level: A
title: GRPO / PPO 的损失为什么只加在 response token 上？
quick: "Prompt 是给定的条件，response 才是模型采样出的动作，因此优势、ratio、KL 和熵都要用 response mask 限定在生成段。Agent 多轮也按同样原则处理：Thought / Action 参与损失，工具返回的 observation 只作为条件。"
tags:
  - LLM RL
  - GRPO
  - Mask
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-21
sources:
  - title: DeepSeekMath / GRPO
    url: https://arxiv.org/abs/2402.03300
    type: primary
  - title: veRL GRPO docs
    url: https://verl.readthedocs.io/en/latest/algo/grpo.html
    type: primary
---

PPO / GRPO 只应对模型自己选择的 response token 计算策略损失，因为 prompt 是给定的观测，response 才是动作。比如用户题干也进了 ratio 和优势加权，梯度就在提高题干的似然，无法对应「让好答案更常出现」。这和 SFT 只对 label 段算 CE 的思路一致：先用 `response_mask` 划清责任范围，再决定 `token-mean` 或按序列平均。

## 动作是谁选出来的

把序列写成 $\text{prompt}+\text{response}$。对 prompt 位置 $t$，token 来自数据集或用户，不是 $\pi_\theta$ 的采样结果；对 response 位置，$a_t\sim\pi_\theta(\cdot\mid s_t)$，这才是策略梯度的 $a_t$。PPO / GRPO 的 ratio $\rho_t=\pi_\theta(a_t\mid s_t)/\pi_{\mathrm{old}}(a_t\mid s_t)$ 和优势 $\hat A_t$ 只应乘在这些 $a_t$ 上。把 prompt 的 $\log\pi$ 乘进损失，梯度在「改题干的似然」，方向与「让好答案更常出现」无关；严重时会把系统提示词往奖励高的方向扭曲，看起来 reward 在涨、holdout 却垮。

KL 同样只应约束生成段：prompt 上的 KL 没有策略意义，还会把均值拉偏，让你误判「KL 已经很大该降学习率」。组内优势是序列标量再广播到生成 token，广播的目的地也必须是 mask=1 的位置，见 `sys-rl-grpo-loop-roles`。$n$ 条对比的是 completion，不是题干；题干相同才成组，见 `sys-rl-group-n`。

## 实现上就是一条 mask

veRL 里是 `response_mask`：loss / entropy / KL 只在 mask $=1$ 的位置求平均。`loss_agg_mode`（`token-mean` 还是按序列再平均）也只在这些位置上算，见 `baidu-grpo-loss-agg`。padding、EOS 之后的无效位必须为 0，否则短答案被 pad 稀释，长答案被虚假 token 拉偏，长度奖励会从 pad 里漏出来。EOS 本身通常要训（它是「停」这个动作）；EOS 之后的 pad 不要训。

实现上先生成 `attention_mask`，再与「第一个 response token 起」的区间做与，不要靠「非 pad 全训」偷懒。那会把 prompt 和 pad 一起放进来。Agent 轨迹里 Thought / Action 为 1，工具返回 / 观测结果（observation） 为 0。日志里抽一条样本核对 mask 的 0/1 边界，比看平均 loss 更能发现漏 mask。Dr.GRPO / 长度归一是 mask 之后的事，先保证 prompt 没漏进，见 `pt-drgrpo`。

多轮里模型自己写的 Thought / function call 是动作；搜索引擎、代码沙箱、浏览器返回的 observation 是环境。把整段轨迹当 completion 一起反传，等于让模型去「学」搜索引擎说了什么，credit 会漏到不可控文本上，工具格式稍变梯度就抖。正确做法是只对模型发出的 token 置 1，工具结果当条件。和「只训 response」是同一条原则，只是 response 被切成了多段。

组内优势仍按整条轨迹的标量奖励广播到这些 mask=1 的位置。环境延迟往往超过 逐 token 生成（decode），一步实际耗时不再能用 MFU 解释，见 `sys-rl-infra`；但那是调度问题，不能反过来成为「所以 observation 也该训」的理由。多轮 mask 写错更难查：loss 看着正常，策略却在模仿检索片段。从 batch 抽一条，打印 prompt 长度、response 长度、mask 为 1 的个数，对不上就是实现 bug。

曲线上若「reward 不动、KL 却在涨」或系统提示被改得像高分答案，优先查 mask。长度奖励、EOS 惩罚、format reward 都挂在同一条 mask 上，mask 错了它们一起错。

还有一种容易漏掉的错误，是直接用 `attention_mask` 作为损失计算范围。attention 必须看见 prompt，策略 loss 则只更新模型发出的 token，所以两套 mask 的起点不同。tokenize 后 prompt 长度和字符串切分差 1、BOS 或 chat template 的 special token 被算进 response，都会把系统提示最后几个 token 训进去。对账：decode mask=1 的片段，看是不是模型写的那一段；对不上就停训修管线。padding 进平均或 EOS 之后仍为 1，也会让长度从 pad 里漏出来，先修边界再看 `sys-rl-longer-after-rl`。

## 追问

**padding 要不要进平均？**
不要。EOS 之后的无效位会改变长短答案的权重，看起来像 loss 在抖、长度在无奖励地涨。
**EOS 本身呢？**
通常要训，它是停止动作；EOS 之后的 pad 不要训。不训 EOS，模型会学会拖到 max length。
**按 token 均还是按序列均？**
会改变长短答案的权重，那是 `baidu-grpo-loss-agg` / Dr.GRPO，先保证 prompt 没漏进 mask。
**prompt 漏进 mask 的症状？**
系统提示词被改、KL 虚高、reward 没动但 prompt 段 logp 在涨。抽样本看 mask 比看曲线快。
**工具返回能不能当正例？**
不能。那是环境，不是策略。只训 Thought / Action。把检索原文当 completion，等于让模型背语料。
**和 SFT 的 label mask 是不是一回事？**
是同一思想：只对模型该负责的 token 算损失。RL 多了 ratio 和优势，mask 的边界更不能含糊。
**优势是序列标量，为什么还要 token mask？**
标量广播到每个生成 token，再乘 mask。广播到 prompt 上，题干也会被推一把。组内对比的是 completion 质量，题干相同才成组，把题干推进损失等于在改环境。
**只 mask loss、不 mask KL 行不行？**
不行。prompt 上的 KL 没有策略意义，还会让你误判正则已经很大。entropy 同理，只在生成段上才表示探索。
**format reward 要不要另开一段 mask？**
不必。它仍是序列标量，广播到 Thought / Action 即可；不要把 JSON 里工具返回的字段也算进 format 正例。
**chat template 的 special token 算谁的？**
系统提示和用户轮次算 prompt，模型这一轮发出的才是 response。差 1 个 BOS 就会把提示词最后几个字训进去，decode mask=1 片段即可发现。
**和「RL 之后变长」怎么区分？**
先确认 pad / EOS 没有漏进 mask。mask 事故也会让长度涨，那不是奖励形状问题，见 `sys-rl-longer-after-rl`。
**先保证哪一件？**
prompt 没漏进 mask。平均方式是下一张卡。
