---
id: nio-trl-verl-ray
section: systems
order: 233
level: A
title: 蔚来一面：TRL、veRL、Ray 各管哪一层，怎么选型？
quick: >-
  Ray 是分布式调度，不是算法。TRL 把 GRPO 塞进 HuggingFace Trainer，适合单机到数卡原型。veRL /
  OpenRLHF 把 rollout 和训练拆成 worker：veRL 用 HybridEngine 同卡换布局，OpenRLHF 用独立
  vLLM Ray actor。70B+ 或要 Megatron 选 veRL；先跑通选 TRL。
tags:
  - NIO
  - TRL
  - VeRL
  - Ray
  - OpenRLHF
realInterview: true
status: published
format: markdown
updatedAt: 2026-08-21
sources:
  - title: 蔚来大模型强化学习训练一面
    url: https://www.nowcoder.com/discuss/863132498270695424
    type: candidate-first-hand
  - title: TRL
    url: https://huggingface.co/docs/trl
    type: primary
  - title: OpenRLHF
    url: https://github.com/OpenRLHF/OpenRLHF
    type: primary
  - title: verl
    url: https://github.com/verl-project/verl
    type: primary
---

## 真题记录

- 公司：蔚来
- 岗位：大语言模型强化学习算法实习；一面
- 来源类型与可信度：牛客候选人原帖，A
- 原始措辞：**“有关强化学习算法的代码库，TRL，VERL，Ray等”**

这块容易把 TRL、veRL、Ray 并列成「三个同类库」。Ray 是调度 / 放置，不是 GRPO 实现。TRL 是算法 + HuggingFace Trainer。veRL / OpenRLHF / slime 才是把 rollout 和训练拆成 worker 的 RL Infra。选错层会把「单机跑通」和「70B 同卡换布局」混成同一句话。Agentic RL 岗还会追工具稳定性、稀疏奖励；框架答完我会补一句用过的 `rollout.n`、是否重算 logp、clip 是否真的触发。

## 三层不要并列

| 名字 | 层 | 典型后端 |
| --- | --- | --- |
| Ray | 调度 / 放置 | 多节点 worker、actor 池 |
| TRL | 算法 + 训练循环 | Accelerate / HF generate 或外挂 vLLM |
| veRL | 算法 + HybridFlow | FSDP2 / Megatron + vLLM / SGLang |
| OpenRLHF | 算法 + 异构 actor | DeepSpeed ZeRO + 独立 vLLM 池 |
| slime | 算法 + 摊开 loop | Megatron + SGLang router |

Ray 可以被 veRL / OpenRLHF / slime 当运行时；单独说「我们用 Ray 做 RL」等于没说算法。TRL 把 GRPO 塞进 Trainer，适合 7B 原型、数卡、HF ckpt；rollout 往往还是 HF generate 或薄薄一层 vLLM，没有 HybridEngine 那套 reshard，也缺少 Data Buffer / partial / fully-async 一等开关。先跑通选 TRL；卡一多、要 Megatron / 同卡少一份整模，再迁 veRL。

## 放置决定框架，不是品牌

veRL HybridEngine：同卡、同进程换训练分片 ↔ 推理 TP，少一份整模，一步默认串行。OpenRLHF：vLLM 独立 Ray actor，可异构扩容，多一份权、要同步。slime：默认 Megatron + SGLang，`--colocate` 是两进程 offload，不是 HybridEngine；分卡用 `--actor-num-gpus-per-node` + `--rollout-num-gpus`。70B+ 同构卡紧偏 veRL；要 SGLang router / PD / 自定义 `--custom-generate-function-path` 偏 slime；已经有独立推理池偏 OpenRLHF。TRL 不解决这套放置题。

算法开关对照：veRL `algorithm.adv_estimator`、`actor_rollout_ref.rollout.n`；slime `--advantage-estimator`、`--n-samples-per-prompt`。重算 logp、weight sync、动态 batch 是 Infra 题，TRL 文档里往往一带而过。被问「生产怎么训」时不要只停在 TRL。

## 怎么开口选型

先报模型规模、卡是否同构、ckpt 是 HF 还是 Megatron、要不要 Agent 工具循环。7B 验证算法：TRL。多机 GRPO/DAPO、要 HybridEngine：veRL。绑定 SGLang 生产栈：slime。生成池已隔离：OpenRLHF。Ray 是它们底下的调度，不是第四个算法库。补实验细节：`rollout.n` 多少、logp 是否训练图重算、clip 有没有真触发。只报库名会被追问拆穿。

选型按层说。Ray 回答「worker 怎么放、怎么等」；TRL 回答「HF 生态里怎么把 GRPO 跑通」；veRL / OpenRLHF / slime 回答「rollout 和训练怎么拆、权怎么同步、70B 放不放得下」。把 Ray 和 TRL 比快慢没有意义。实习项目 7B、数卡、HF ckpt：TRL 足够验证 clip 和组优势；要写进周报的 Infra 细节（HybridEngine、重算 logp、`rollout.n`）再去读 veRL。生产同构大模型卡紧：veRL HybridEngine 少一份整模。已经绑定 SGLang、要 router / PD / `--custom-generate-function-path`：slime。生成节点规格和训练不同：OpenRLHF 独立 vLLM actor。Agent 岗追问工具循环时，TRL 往往要自己接 env；slime / veRL 有一等 RM + generate 接口。最后补三个数字：`n`、是否重算 logp、clip 触发率，证明跑的是算法而不是 `import`。框架是放置策略的实现，先报拓扑再报名字。

## 实习怎么答

7B 数卡先 TRL 验证组优势和 clip。要写 HybridEngine、重算 logp、`rollout.n` 再读 veRL。同构 70B 卡紧偏 veRL；绑 SGLang router / 自定义 generate 偏 slime；生成池已隔离偏 OpenRLHF。Ray 只是调度。最后报 $n$、是否训练图 logp、clip 触发率。框架跟在拓扑后面，不要先报品牌。

## 追问

- **Ray 是强化学习库吗？** 不是。它调度 worker 和放置。veRL、OpenRLHF、slime 都可以跑在 Ray 上。单独说「我们用 Ray 做 RL」等于没说算法，也没说 rollout 和训练怎么拆。
- **TRL 和 veRL 差在哪？** TRL 把 GRPO 塞进 HuggingFace Trainer，适合原型；veRL 把 rollout/train 拆成 worker，并用 HybridEngine 同卡换布局。规模、放置、是否重算 logp 的一等支持都不同。
- **slime 算不算 veRL 竞品？** 同层 Infra。slime 默认 Megatron + SGLang，`--colocate` 是两进程 offload，不是 HybridEngine。不要说「slime 也有 HybridEngine」。自定义 generate 是 slime 的强项。
- **70B 一定 veRL？** 不是。已有独立推理池、或必须 SGLang router / PD / delta 同步时，分卡或 slime 可能更合适。先报卡数、是否同构、能否接受一步串行。
- **实习项目怎么选？** 先 TRL 跑通 GRPO 数学，再读 veRL `actor_rollout_ref` 或 slime `train.py` 时间线，能讲 reshard、weight sync、重算 logp 即可。补一句你的 `rollout.n` 和 clip 是否触发。
