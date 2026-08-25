---
id: sys-unsloth-when
section: systems
order: 280
level: A
title: 什么时候用 Unsloth 做 LLM RL？为什么进不了和 veRL / slime 同一张选型表？
quick: >-
  Unsloth 强在单机 / 少量卡上把 LoRA、梯度检查点、融合 kernel 做到极致，适合 7B～32B 原型、课程作业、先跑通
  GRPO。它几乎没有多机 rollout 控制面：没有 HybridEngine、没有 SGLang router / PD、没有 Data
  Buffer 和 staleness 账本。多机 MoE、异步长尾、自定义 generate，换 veRL / slime / AReaL。
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

35 题 Infra 最后一问常把 Unsloth 和 veRL / slime / AReaL 并列。这块容易答「Unsloth 更快所以生产也用」。快的是 **单卡训练步**，不是大规模 rollout。框架总图见 `sys-llm-rl-framework-index`。

## Unsloth 实际换到的

针对 Hugging Face 模型和 LoRA：更省显存的反向、部分 kernel 融合、梯度检查点、和 TRL 的 GRPO trainer 能接上。你在一张或几张消费级 / 数据中心卡上，想当晚把 7B 数学 GRPO 跑出曲线，它比从头配 Megatron 合理。量化、长上下文、单机 FSDP 也能再挤一截。

它 **不** 替你解决：组不齐、最长 CoT 钉死 batch、权重同步到推理引擎、partial abort、MoE EP、跨机 PD 传 KV。这些是 veRL HybridEngine、slime Data Buffer、AReaL async worker 的工作，见 `sys-verl-vs-slime`、`sys-areal-vs-slime`。

## 怎么开口

「原型 / 消融 / 小模型用 Unsloth 或 TRL；FSDP + vLLM + 复现 DAPO 用 veRL；Megatron + SGLang 透传用 slime；同步等长尾、要 fully async 再看 AReaL。」Ray 仍是调度层，不是第四个 RL 算法。

面试被追「那 Unsloth 的 GRPO 和 veRL 差在哪」：loss 可以写成同一公式，**数据面不同**。Unsloth 路径往往 generate 和 train 更近、甚至同进程；veRL 把 rollout 当服务。同进程省调度，却更难做 continuous batching 的版本账和引擎量化，见 `sys-rl-cont-batch-onpolicy`。

不要承诺 Unsloth 能线性扩到 128 卡 MoE。那是另一套软件。

## 追问

- **Unsloth 量化 rollout 要重算 logp 吗？** 要。精度隙和引擎隙是同一类，见 `meituan-verl-recompute-logprob`。
- **能不能 Unsloth 训练 + vLLM 生成？** 能焊，版本和 tokenizer 要对齐。一旦开始焊，你已经在手写 veRL 的子集。
- **和 TRL？** TRL 是 HF 的 RL 库；Unsloth 是加速补丁。选型时 TRL 管 API，Unsloth 管这台机器能不能放下。
