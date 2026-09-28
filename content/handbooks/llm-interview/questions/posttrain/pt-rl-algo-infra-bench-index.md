---
id: pt-rl-algo-infra-bench-index
section: posttrain
order: 244
level: A
title: 2026 RL 算法 / Infra 面试 35 题该按什么顺序准备？
quick: >-
  社区 35 题（算法 19 + Infra 16）不是另一套八股，是把 PPO / GRPO 家族和 rollout 系统拆开追问。下面按原帖编号对照手册里的卡。
  算法先钉 Actor-Critic、KL / IS、advantage、clip，再谈 DAPO / GSPO / CISPO / SAPO / DPPO；Infra 先会显存角色、KV
  传输、continuous batching、异步 staleness。Data 题原帖故意没收。
tags:
  - GRPO
  - RL Infra
  - 真题导航
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-24
sources:
  - title: RL面试问题详解
    url: https://zhuanlan.zhihu.com/p/2047692889384292931
    type: secondary
  - title: sheriyuo 35-question RL benchmark（中文题单同源）
    url: https://zhuanlan.zhihu.com/p/2046740446353811230
    type: secondary
  - title: DeepSeekMath / GRPO
    url: https://arxiv.org/abs/2402.03300
    type: primary
---

2026 春招前后流传一套 35 题 RL benchmark。原帖强调可延伸、算法岗也会问系统，**不给标准答案**。手册按题拆卡，本页只做编号对照。点下面每条跳到对应题。

Data 相关题目原帖故意没收：几乎没法背，全靠你自己的数据经历。

## 算法 1–19

1. 为什么要用 Actor-Critic 而不是纯 Critic？`fund-ac-vs-value-based`
2. KL 散度和交叉熵、MLE 的关系？`fund-ce-kl`
3. 不同 RL 场景应该如何设计 Reward？`pt-reward-design`
4. 如何理解 RL 中的 importance sampling / rejection sampling 等 Monte Carlo 方法？`fund-is`，以及何时该上 on-policy RL：`pt-rejection-sampling-vs-rl`
5. PPO / GRPO 的 advantage 怎么算、为什么减 baseline、一定要除 std 吗？`pt-gae`、`pt-grpo`、`fund-adv-norm-bias`
6. RL training 和 test-time scaling 各自如何 explore？`pt-rl-vs-tts-explore`
7. PPO 如何 clip、为什么取 min、不 clip 会怎样、CISPO 怎么做？`pt-ppo-clip`、`pt-cispo`
8. GRPO 为什么加 KL、KL 怎么算、为什么 DAPO / GSPO 又去掉？`ant-grpo-kl-vs-ppo`、`xiaohongshu-grpo-drop-kl`
9. LLM 训练时如果不小心多 AllReduce 了几次 loss，会发生什么？`sys-allreduce-loss-scale`
10. DPO 的 reward 是什么，会不会 reward hacking，如何解决？`pt-dpo-implicit-reward-hack`
11. 有哪些解决 MoE 训推不一致的算法？`sys-moe-train-infer-routing-mismatch`；R2 / R3 / Keep Routing 分层见 `pt-r3-routing-replay`；DeepSeek 的 Keep Routing 见 `pt-deepseek-rl-lineage`
12. group size / learning rate / PPO epoch / generation length 如何设置？`pt-rl-hparams-joint`
13. 相比 GRPO，Dr.GRPO / DAPO / GSPO / CISPO / SAPO / DPPO / MaxRL / SimKO 如何改进？`pt-dapo`、`pt-gspo`、`pt-cispo`、`pt-drgrpo`、`pt-grpo-family-sapo-simko`；DPPO 信任域见 `pt-dppo-areal-trust-region`；组内过滤压长度见 `pt-gfpo`
14. TRPO / DPPO / AReaL 如何用 trust region 约束 RL objective？`pt-dppo-areal-trust-region`
15. RL 能否拓展 LLM 的能力边界？`pt-rlvr-discovery-vs-reweighting`
16. 结合 ProRL 等工作，如何 scale RL 训练边界？`pt-prorl-scale-boundary`
17. OPD 相比传统 RL / SFT 改了什么？`pt-on-policy-distillation`
18. LLM 推理能力是在哪一个训练阶段产生的？`pt-where-reasoning-comes-from`
19. DeepSeek R1 到 V3.2 / V4，RL 部分有哪些改进，MoE RL 有什么不同？`pt-deepseek-rl-lineage`

## Infra 1–16

1. 不考虑 CPU offload，GRPO 训练时显存里有几个模型，考虑了能省多少？`sys-rl-memory`
2. 分布式推理：KV cache 传输优化、多卡通信优化？`sys-kv-cache-transfer`
3. INT8 与 FP8 优劣，训推分别用什么精度？`sys-int8-vs-fp8`
4. RL rollout 中的长尾问题是什么，有哪些解决方案？`byte-grpo-rollout-tail-gpu`
5. continuous batching 在 RL 训练时会有什么问题，vLLM 和 SGLang 的区别？`sys-rl-cont-batch-onpolicy`、`sys-verl-vllm-vs-sglang`
6. vLLM / SGLang 怎么看利用率，KV cache 在训练里的利用率怎么看？`sys-rl-engine-kv-util`
7. 多机多卡 RL 训练时如何实现反向传播？`sys-rl-multinode-bwd`
8. RL 训练有哪些异步框架，解决了同步训练的什么问题？`sys-areal-vs-slime`、`slime-async-train`、`sys-staleness`；截断 IS 见 `pt-tis-async`
9. AReaL 或其他 partial rollout 框架，会不会保存之前 policy 的 KV cache？`sys-partial-kv-policy`；半截轨迹的 TIS / mask 见 `pt-tis-async`
10. MoE 的 EP 对 throughput 的影响？`sys-expert-parallel`
11. Long context 下 compute-communication overlap，Megatron 和 FSDP 各自的 parallelism？`sys-parallel`、`sys-dualpipe`
12. 确定性模式怎么开，什么是 batch invariance，atomicAdd 能解决吗？`sys-batch-invariance`
13. AReaL 和 slime 对 RL rollout bottleneck 的理解有什么不同？`sys-areal-vs-slime`
14. full async staleness 怎么看，训练时大概是多少？`sys-staleness`
15. slime 里 data 怎么流，Megatron 怎么结合，loss 怎么算？`slime-data-buffer`；归约见 `baidu-grpo-loss-agg`
16. VeRL / TRL / Unsloth / AReaL / slime 你会选哪个？`sys-llm-rl-framework-index`；Unsloth 单独选型见 `sys-unsloth-when`

一步 GRPO 谁采样谁打分，入门图见 `sys-rl-intro-index`。

## 原帖没收、但会被追的延伸

原帖强调三件事：Agent 场景答案会变、几乎每题都能追、Data 没法背。下面这些不改 1–35 的编号，是按这三条补的独立卡。

- 长度膨胀用组内过滤，而不是改标量奖励：`pt-gfpo`
- MoE 路由重放 R2 / R3，不要和 GSPO 说成同一种对齐：`pt-r3-routing-replay`
- 异步 / partial 的 TIS，不要和 CISPO 说成同一个 clip：`pt-tis-async`
- 多轮 Agent 的组内组优势 GiGPO：`arl-gigpo`
- Agent GRPO 的思维 / 调用 / 工具返回 mask：`pt-agent-grpo-token-mask`
- 单机 Unsloth 什么时候能进选型、什么时候不能：`sys-unsloth-when`
- Data：怎么筛 RLVR、熵塌怎么读、塌了先动哪几个旋钮：`data-rlvr-select`、`data-entropy-collapse`、`data-entropy-fix-order`
- Agent 过程奖励和 GiGPO 锚点哈希怎么选：`arl-process-vs-gigpo`

准备顺序：先能白板推 PG → PPO → GRPO；再对照 DAPO / GSPO / CISPO / SAPO / DPPO 各自改 clip 的哪一层；最后能画 rollout 与 trainer 解耦、说出 staleness 和 KV 版本。原帖强调「做算法也会问 Infra」，后两圈不是 Infra 岗专属。
