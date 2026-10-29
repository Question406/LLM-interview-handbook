---
id: nio-trl-verl-ray
section: systems
order: 233
level: A
title: 蔚来一面：TRL、veRL、Ray 各管哪一层，怎么选型？
quick: >-
  TRL、veRL 和 Ray 分处不同层：TRL 提供算法和 HF Trainer 训练循环，适合先做原型；veRL 把 rollout 与训练拆成
  worker，并用 HybridEngine 处理布局；Ray 负责分布式调度和放置。选择框架时要看模型规模、资源拓扑、训练后端和是否需要工具循环。
tags:
  - NIO
  - TRL
  - VeRL
  - Ray
  - OpenRLHF
realInterview: true
status: published
format: markdown
updatedAt: 2026-08-21T00:00:00.000Z
sources:
  - title: 蔚来大模型强化学习训练一面
    url: 'https://www.nowcoder.com/discuss/863132498270695424'
    type: candidate-first-hand
  - title: TRL
    url: 'https://huggingface.co/docs/trl'
    type: primary
  - title: OpenRLHF
    url: 'https://github.com/OpenRLHF/OpenRLHF'
    type: primary
  - title: verl
    url: 'https://github.com/verl-project/verl'
    type: primary
---

## 真题记录

- 公司：蔚来
- 岗位：大语言模型 RL 算法实习；一面
- 来源类型与可信度：牛客候选人原帖，A
- 原始措辞：**“有关 RL 算法的代码库，TRL，VERL，Ray 等”**

TRL 管算法和 HuggingFace Trainer 训练循环，veRL 管拆开 rollout 与训练后的 RL Infra，Ray 则管 worker 调度和放置。它们可以一起用，选型时要先分清所在的层。

比如先在数卡上验证 7B GRPO，可以从 TRL 开始；到了多机大模型，还要考虑训练分片怎样变成推理布局、生成池怎样放置，以及工具调用和稀疏奖励是否稳定。解释自己的实验时，再补上 `rollout.n`、是否重算 logp 和 clip 是否触发，才能说清框架实际解决了什么。

## 先看各自负责什么

| 名字 | 层 | 典型后端 |
| --- | --- | --- |
| Ray | 调度 / 放置 | 多节点 worker、actor 池 |
| TRL | 算法 + 训练循环 | Accelerate / HF generate 或外挂 vLLM |
| veRL | 算法 + HybridFlow | FSDP2 / Megatron + vLLM / SGLang |
| OpenRLHF | 算法 + 异构 actor | DeepSpeed ZeRO + 独立 vLLM 池 |
| slime | 算法 + 摊开 loop | Megatron + SGLang router |

Ray 可以被 veRL / OpenRLHF / slime 当运行时；说明使用 Ray 后，还要交代算法和 sampling 训练流程。TRL 把 GRPO 塞进 Trainer，适合 7B 原型、数卡、HF ckpt；rollout 往往还是 HF generate 或薄薄一层 vLLM，没有 HybridEngine 那套 reshard，也缺少 Data Buffer / partial / fully-async 一等开关。先跑通选 TRL；卡一多、要 Megatron / 同卡少一份整模，再迁 veRL。

## 再按资源放置方式选择

veRL HybridEngine：同卡、同进程换训练分片 ↔ 推理 TP，少一份整模，一步默认串行。OpenRLHF：vLLM 独立 Ray actor，可异构扩容，多一份权、要同步。slime：默认 Megatron + SGLang，`--colocate` 是两进程 offload，不是 HybridEngine；分卡用 `--actor-num-gpus-per-node` + `--rollout-num-gpus`。70B+ 同构卡紧偏 veRL；要 SGLang router / PD / 自定义 `--custom-generate-function-path` 偏 slime；已经有独立推理池偏 OpenRLHF。TRL 不解决这套放置题。

算法开关对照：veRL `algorithm.adv_estimator`、`actor_rollout_ref.rollout.n`；slime `--advantage-estimator`、`--n-samples-per-prompt`。重算 logp、weight sync、动态 batch 是 Infra 题，TRL 文档里往往一带而过。被问「生产怎么训」时不要只停在 TRL。



先报模型规模、卡是否同构、ckpt 是 HF 还是 Megatron、要不要 Agent 工具循环。7B 验证算法：TRL。多机 GRPO/DAPO、要 HybridEngine：veRL。绑定 SGLang 生产栈：slime。生成池已隔离：OpenRLHF。Ray 是它们底下的调度，不是第四个算法库。补实验细节：`rollout.n` 多少、logp 是否训练图重算、clip 有没有真触发。只报库名不足以说明选型依据。

## 追问

**Ray 是 RL 库吗？**
不是。它调度 worker 和放置。veRL、OpenRLHF、slime 都可以跑在 Ray 上。因此还要说明算法和 rollout、训练的拆分方式。
**TRL 和 veRL 差在哪？**
TRL 把 GRPO 塞进 HuggingFace Trainer，适合原型；veRL 把 rollout/train 拆成 worker，并用 HybridEngine 同卡换布局。规模、资源放置方式、对 logp 重算的原生支持都不同。
**slime 算不算 veRL 竞品？**
同层 Infra。slime 默认 Megatron + SGLang，`--colocate` 是两进程 offload，不是 HybridEngine。不要说「slime 也有 HybridEngine」。自定义 generate 是 slime 的强项。
**70B 一定 veRL？**
不是。已有独立推理池、或必须 SGLang router / PD / delta 同步时，分卡或 slime 可能更合适。先报卡数、是否同构、能否接受一步串行。
**实习项目怎么选？**
先 TRL 跑通 GRPO 数学，再读 veRL `actor_rollout_ref` 或 slime `train.py` 时间线，能讲 reshard、weight sync、重算 logp 即可。补一句你的 `rollout.n` 和 clip 是否触发。
