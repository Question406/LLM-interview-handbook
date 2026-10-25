---
id: sys-llm-rl-framework-index
section: systems
order: 229
level: A
title: 现在做 LLM RL，面试会问哪些训练框架题？
quick: "这张卡可以按框架结构、训练与 rollout 的边界、性能瓶颈三个方向准备。公开面经会问 veRL / TRL / OpenRLHF / Ray；用过 veRL 和 slime 时，还要讲清 HybridEngine 与 `--colocate`+offload、Hydra YAML 与 Megatron/SGLang 透传、Reward Manager 与 Data Buffer 的差别。同步长尾再看 AReaL，单机省显存再看 Unsloth。"
tags:
  - VeRL
  - slime
  - TRL
  - OpenRLHF
  - 真题导航
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-24
sources:
  - title: 字节大模型agent算法一面分享
    url: https://www.nowcoder.com/feed/main/detail/f6e62eddaae1460fa80c0a0052f3267a
    type: candidate-first-hand
  - title: 美团大模型研发二面-日常实习
    url: https://www.nowcoder.com/feed/main/detail/23e19d8300c54f2eb9ed9933aeaa5129
    type: candidate-first-hand
  - title: 蔚来大模型强化学习训练一面
    url: https://www.nowcoder.com/discuss/863132498270695424
    type: candidate-first-hand
  - title: verl
    url: https://github.com/verl-project/verl
    type: primary
  - title: THUDM/slime
    url: https://github.com/THUDM/slime
    type: primary
---

这张卡把公开面经里的框架问题和机制对照放在一起，可以先按自己用过的框架找题，再补相邻框架的差别。比如用过 veRL 和 slime，除了介绍组件，还要解释权重同步、rollout 和 update 怎样衔接，以及什么情况下值得换框架。下面标题可点击跳转。

## 一手面经

- 字节 Agent 算法一面：讲讲 veRL 的结构、关键组件，怎么魔改？
- 美团二面：veRL 为什么要重新 forward 算 logprob，生成时记下的不够吗？
- 美团二面：GRPO 哪个阶段最耗时？rollout 采样卡在哪？
- 蔚来一面：TRL、veRL、Ray 各管哪一层，怎么选型？
- 滴滴一面：用 veRL 做 RL 时，看哪些指标判断训练在走？
- 蚂蚁 26 秋招：VeRL 的 rollout 与 update batch 参数如何共同决定每卡样本数？
- 阶跃：用 VeRL 训搜索工具 Agent 时，各类角色怎么设计？
- [[stepfun-verl-search|阶跃：介绍一下 trl / verl 架构（见搜索工具卡）]]
- AI Infra 实习：RL 里 rollout 大概占多少时间？MFU 和 $6ND$ 怎么算？
- AI Infra 实习：RL rollout 有哪些优化？量化、异步分别换什么？
- AI Infra 实习：训练完的权重怎么同步到推理引擎？
- AI Infra 实习：Megatron TP 切 MLP 时，两个矩阵怎么切、通信是什么？
- 百度后训练一面：GRPO 序列级损失怎么落到每个 文本处理单位（token）？

## 机制对照

- veRL 的 HybridEngine 解决什么？和 OpenRLHF 把 vLLM 单独拉一套有何不同？
- veRL 里 rollout 用 vLLM 还是 SGLang？多轮 Agent 怎么选？
- veRL 训练后端选 FSDP 还是 Megatron？
- veRL 的 `use_dynamic_bsz` 和写死 micro-batch 有何不同？
- TRL / veRL / OpenRLHF 里为什么 clip fraction 会一直是 0？
- 为什么 RL Systems 比 SFT 复杂？
- 字节 27 暑期：GRPO rollout 长尾拖低 GPU 利用率，工程上怎么解？

代码路径（优势在哪算、clip 在哪个函数、归约怎么除）见「手写 PPO / GRPO / GSPO：TRL 和 verl 各改哪一段？」，以及 Miles / verl / TRL 三张拆解：Miles 里 GRPO / GSPO / PPO 的代码从 train.py 走到哪？、verl 里优势在 driver、clip 在 worker，代码怎么接？、TRL 的 GRPOTrainer 把变体都收进 loss_type，代码怎么分支？

## veRL × slime（两套都用过时）

- 你用过 veRL 和 slime，两者差在哪、什么时候换？
- slime 训推一体和训推分离怎么配？和 veRL HybridEngine 是一回事吗？
- slime 的 Data Buffer 是干什么的？Agent 多轮要改哪一层？
- slime 权重怎么推到 SGLang？delta 同步和重算 logp 是一回事吗？
- slime 为什么死磕 SGLang？`--sglang-` 前缀和 BF16 训 + FP8 rollout 怎么讲？
- slime 为什么不能直接 load HuggingFace 权重？
- slime 里 GRPO / GSPO / CISPO / PPO 怎么切？
- slime 做多轮工具 / 自定义 reward，该换哪一层函数？
- slime 里 DAPO 动态采样和 partial rollout 怎么配？半截轨迹算 on-policy 吗？
- slime 的异步训练怎么开？挪 `ray.get` 和 `train_async.py` 是一回事吗？
- slime 的 rollout / global / micro batch 怎么对到 veRL 那套字段？
- slime 什么时候上 PD 分离？
- slime 怎么接已经拉起来的 SGLang？
- slime 怎么同时 serve actor 和冻住的 ref / 奖励分数（reward）？
- 多轮 Agent 在 slime 里为什么要把 router 改成 session affinity？
- slime 的 `--use-dynamic-batch-size` 和 veRL `use_dynamic_bsz` 怎么对？
- AReaL 和 slime 对 rollout bottleneck 的理解差在哪？
- partial / 异步 rollout 能不能把旧 policy 的 KV cache 接着用？
- RL 训练开 continuous batching，会破坏 on-policy 边界吗？
- 什么时候用 Unsloth 做 LLM RL？为什么进不了和 veRL / slime 同一张选型表？
- 2026 RL 算法 / Infra 面试 35 题该按什么顺序准备？

我会按场景选：原型用 TRL 或 Unsloth；Ray 异构生成池用 OpenRLHF；FSDP / vLLM / DAPO 复现用 veRL；Megatron 透传 + SGLang router / PD / FP8 / 自定义 generate 用 slime；同步等长尾、要 fully async 再评估 AReaL。Ray 仍是调度层。Unsloth 为什么进不了多机控制面比较，见选型表那条。
