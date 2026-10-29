---
id: sys-unsloth-when
section: systems
order: 280
level: A
title: 什么时候用 Unsloth 做 LLM RL？为什么进不了和 veRL / slime 同一张选型表？
quick: "单机少卡、想先跑通 7B 数学 GRPO 时，可以用 Unsloth：它通过 LoRA、融合 kernel 等手段省显存、加快训练。多机 rollout、MoE 专家并行和异步长尾调度需要 veRL、slime 或 AReaL 这类框架。"
tags:
  - Unsloth
  - TRL
  - VeRL
  - slime
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-24
sources:
  - title: unslothai/unsloth
    url: https://github.com/unslothai/unsloth
    type: primary
  - title: TRL
    url: https://huggingface.co/docs/trl
    type: primary
  - title: verl
    url: https://github.com/verl-project/verl
    type: primary
---

Unsloth 适合单机少卡上的原型、ablation 和小模型训练。比如想用一张或几张消费级 / 数据中心卡，当晚把 7B 数学 GRPO 跑出曲线，可以先选它；多机 rollout 的调度能力则要另外考虑。

它针对 Hugging Face 模型和 LoRA 优化反向显存、融合部分 kernel、使用梯度检查点，也能接 TRL 的 GRPO trainer。量化、长上下文优化和单机 FSDP 还可以继续节省资源。TRL 提供 HF 的 RL API，Unsloth 主要负责让这台机器训练得更快、放得下模型。

规模扩大后，问题会变成组不齐、最长 chain of thought（CoT）拖住整个 batch、权重如何同步到推理引擎，以及 partial abort、MoE EP 和跨机 PD 传 KV。Unsloth 几乎没有多机 rollout 控制面，这些工作分别需要 veRL HybridEngine、slime Data Buffer、AReaL async worker 一类组件。单卡训练步快，并不能推出它可以线性扩到 128 卡 MoE。

选型时，原型 / ablation / 小模型可以用 Unsloth 或 TRL；要 FSDP + vLLM 并复现 DAPO，可以选 veRL；要 Megatron + SGLang 透传，可以选 slime；同步训练被长尾拖住，需要 fully async 时再看 AReaL。Ray 在这里负责调度，不是另一个 RL 算法。

Unsloth 和 veRL 的 GRPO 损失（loss）可以写成同一公式，主要差别在数据怎么流动。Unsloth 的 generate 和 train 往往更近，甚至同进程，省掉调度成本；veRL 把 rollout 当服务，更方便处理 continuous batching 的版本记录和引擎量化。

## 追问

**Unsloth 做量化 rollout，要重算 logp 吗？**
要。精度差异和引擎差异都会影响 logp，见 `meituan-verl-recompute-logprob`。

**能用 Unsloth 训练、vLLM 生成吗？**
可以自行对接，但要保证版本与 tokenizer 一致。继续加入同步和调度能力，相当于自己实现 veRL 的一部分。

**怎么把它放进框架选型里？**
先区分单机训练加速和分布式 rollout 调度。总图见 `sys-llm-rl-framework-index`；多机选型见 `sys-verl-vs-slime`、`sys-areal-vs-slime`，continuous batching 的版本问题见 `sys-rl-cont-batch-onpolicy`。
