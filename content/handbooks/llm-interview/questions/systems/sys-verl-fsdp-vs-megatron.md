---
id: sys-verl-fsdp-vs-megatron
section: systems
order: 241
level: A
title: veRL 训练后端选 FSDP 还是 Megatron？
quick: >-
  7B 到 30B、要快落地：FSDP/FSDP2，和 HF 权重点齐。70B+、要 TP/PP/EP、MoE 专家并行：Megatron。HybridEngine
  两种都能接 vLLM，但 reshard 路径不同。不要在还没 OOM 时上 Megatron。
tags:
  - VeRL
  - FSDP
  - Megatron
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-21
sources:
  - title: verl
    url: https://github.com/verl-project/verl
    type: primary
  - title: HybridFlow
    url: https://arxiv.org/abs/2409.19256
    type: primary
---

这块容易答「大项目都该 Megatron」，或「FSDP 不是正经训练」。veRL 把训练后端当成可换件：FSDP/FSDP2 和 Megatron 都能进 HybridEngine，再接到 vLLM / SGLang。差别在 **分片形状、MoE、落地速度**，不在「会不会 GRPO」。还没 OOM、没有专家并行需求时上 Megatron，是给自己买一套 ckpt 与并行参数的税。选型第一句我先报：模型多大、有没有 MoE、手里是 HF 还是 Megatron ckpt、集群同不同构。框架跟在这四句话后面。校招实习项目绝大多停在 FSDP 就能把 DAPO 跑通；真正逼你换的是 all-gather 之后仍放不下，或专家数已经需要 EP，或预训练栈就是 Megatron、转换本身更贵。没有这些信号，提前上 TP/PP 会把调试面扩大到算法和并行分不清。

## FSDP 适合什么

FSDP 按 unit wrap，分片参数 / 梯度 / 优化器，配置面小，和 HuggingFace 权重点齐，LoRA、PEFT、社区 ckpt 顺。7B 到 30B、单机或多机但层内还不需要 TP，先 FSDP 能最快跑通 `actor_rollout_ref`。弱项是超大模型跨节点 all-gather 气泡：每层要把分片收齐才能算，通信体积随参数走，长序列时还和激活抢带宽。MoE 专家并行不完整，稠密模型还行，上百专家时会力不从心。

FSDP2 在 veRL 里更常见于新路径：更清晰的 DTensor 布局，reshard 到推理 TP 时形状好讲。提到即可，说清你有没有真跑过，不要把文档路线图当生产经验。LoRA / 冻结底层只训一部分时，FSDP 的 wrap 和 `use_orig_params` 坑比 Megatron 少，校招实习项目绝大多数应停在这里。

## Megatron 适合什么

Megatron 是层内 TP、层间 PP，再加 CP / EP。通信模式固定（列切 / 行切），吞吐上限高，70B+ 和 MoE 是它的主场。代价：Megatron-Bridge、分片 `torch_dist` ckpt、并行参数（tp/pp/ep/cp）自己填，还要和 rollout TP 对齐。reshard 对不齐会退回几乎全量 gather，HybridEngine「少一份整模」的故事破产，见 `sys-verl-hybridengine`。

veRL 已支持 Megatron-FSDP 混合：不是「两个后端各跑各的」就结束了，有人用 Megatron 做稠密主干、FSDP 包其余模块。说清边界，比宣称「我们全 Megatron」诚实。

和 OpenRLHF 对比：那边训练默认 DeepSpeed ZeRO，不是 Megatron。选型先问「单卡是否放得下 + 有没有 MoE」，再问集群是否同构。slime 默认只走 Megatron，从 veRL FSDP 迁过去还有 ckpt 转换，见 `sys-verl-vs-slime`。

## HybridEngine 都能接，路径不同

两种后端推理仍是 vLLM/SGLang 的 TP。换后端改的是训练 shard 形状，不是「要不要 HybridEngine」这个动机。Megatron 带 PP 时，reshard 还要考虑流水线阶段和推理 TP 怎么对齐，比纯 FSDP 更绕。70B 同构卡紧：Megatron + HybridEngine 少一份整模。7B 要快出 DAPO 数：FSDP + vLLM 就够。不要用模型参数量当唯一开关。有无 MoE、有无现成 HF ckpt、团队会不会填并行表，同样决定成本。若目标就是 SGLang 生产栈，可能值得迁 slime；若只是想复现社区 GRPO，留在 FSDP 更短。OpenRLHF 的 DeepSpeed ZeRO 是第三条训练后端，分卡哲学和 Megatron 不同，不要三套并行术语混着用。

还没 OOM 时 FSDP 先把算法跑对，真正 all-gather 之后仍放不下或要 EP 再上 Megatron。信号不是「项目看起来大」。没跑过 Megatron 不要把文档当经验；跑过就讲一次分片 ckpt 或 reshard 对不齐的实锤。

## 追问

- **还没 OOM 为什么不 Megatron？** 并行参数、分片 `torch_dist` ckpt、和推理 TP 对齐是额外失败面。FSDP 先把算法跑对，真正 all-gather 之后仍放不下或要 EP 再换。提前上 TP/PP 会让「并行 bug」和「算法 bug」缠在一起。
- **FSDP 跨机一定慢吗？** 不一定。层少、带宽够、prefetch 做好可以。70B 每层 all-gather 叠加长激活时才明显变成气泡。用 profile 说话，不要用模型参数量当定理。
- **MoE 能不能 FSDP 硬上？** 小专家数可以凑；专家并行、token 路由、容量丢弃是 Megatron / 专用 EP 的主场，见 `sys-expert-parallel`。veRL 选 Megatron 的强信号往往是 MoE 而不是「看起来像大项目」。
- **换后端要不要换 rollout 引擎？** 不必。rollout 选 vLLM 还是 SGLang 是另一题，见 `sys-verl-vllm-vs-sglang`。HybridEngine 两种训练后端都能接，改的是 shard 形状。
- **和 slime / OpenRLHF 怎么对？** slime 默认 Megatron；OpenRLHF 默认 ZeRO。从 veRL FSDP 迁 slime 等于先付 ckpt 转换。选型跟已有训练图走，不跟框架热度走。
- **Megatron-FSDP 混合是什么？** veRL 支持部分模块走 Megatron、其余 FSDP wrap。提到即可，说清你有没有真跑过边界，不要把路线图当生产。
- **LoRA 该选哪边？** FSDP + HF 权重点齐，wrap 和 `use_orig_params` 坑更少，实习项目优先。Megatron 上 LoRA 要自己对接并行切分，除非主干已经是 Megatron。
- **reshard 对不齐会怎样？** HybridEngine 退回几乎全量 gather，少一份整模的故事破产，峰值显存和通信都回到朴素路径。并行表是一等公民，不是调完算法再填的附录。
- **一句话怎么选？** 7B 到 30B、HF ckpt、要快落地用 FSDP；70B+ 或 MoE 要 EP 用 Megatron。还没 OOM 不要上 Megatron。HybridEngine 两种都能接 vLLM，改的是 shard 形状。slime 默认 Megatron，从 FSDP 迁过去要先付 ckpt 转换；OpenRLHF 默认 ZeRO。先报规模、有无 MoE、ckpt 格式。
