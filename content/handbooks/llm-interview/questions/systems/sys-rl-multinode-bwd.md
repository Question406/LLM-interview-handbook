---
id: sys-rl-multinode-bwd
section: systems
order: 279
level: A
title: 多机多卡 RL 训练时反向传播是怎么走的？
quick: "只有 Actor 训练图对 response token 做 backward，rollout 引擎、Ref 和 RM 都不反传。梯度通信和 SFT 一样走 FSDP / Megatron；RL 多出的坑在 loss 怎么平均。"
tags:
  - Distributed Training
  - GRPO
  - Collectives
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-23
sources:
  - title: ZeRO
    url: https://arxiv.org/abs/1910.02054
    type: primary
  - title: HybridFlow / verl
    url: https://arxiv.org/abs/2409.19256
    type: primary
  - title: PyTorch Distributed
    url: https://pytorch.org/docs/stable/distributed.html
    type: primary
---

多机 RL 的反向传播仍由 Actor 训练图完成，梯度通信沿用 FSDP / Megatron 的并行方式。采样卡先 generate，训练卡或同一组卡 reshard 后重算 $\log\pi_\theta$，只对 response mask 覆盖的部分计算损失。比如各 rank 有效 token 数不同，平均 loss 时就要同步 token 计数，否则梯度权重会不一致。角色和 mask 见 `sys-rl-response-mask`、`sys-rl-grpo-loop-roles`；集合通信细节见 `sys-collectives`、`sys-parallel`。

## 一步里的梯度从哪来

1. 引擎生成 token，不建立训练计算图。
2. Trainer 用当前 $\theta$ 重算 $\log\pi$（必要时也算 ref logp）。old logprob / 奖励分数（reward） / advantage **detach**。
3. Policy loss（PPO / GRPO clip、可选 KL）只对 Actor 参数 `backward()`。
4. 数据并行：梯度 reduce-scatter / all-reduce，和 监督微调（SFT） 一样。FSDP 往往停在 shard，不必把整份梯度 all-gather 到每张卡。
5. TP / PP / EP 仍按训练后端的切分传激活和梯度。DualPipe 叠的是 PP 气泡和 EP，见 `sys-dualpipe`。这与 采样轨迹（rollout） 的 KV 传输无关，见 `sys-kv-cache-transfer`。

Ref 只前向。奖励模型（RM） / 验证器（verifier） 在奖励进程里，更不会进 Actor 的 autograd。把「GRPO 显存里有几份模型」和「几份在反传」分开：驻留可以有 Actor + Ref + 引擎副本，反传通常只有 Actor，见 `sys-rl-memory`。

## 强化学习（RL） 比 SFT 多踩的坑

- **对标量 loss 再 AllReduce。** 各 rank 已经在 micro-batch 上平均过，SUM 且没除 $n$ 等于学习率乘 world size。日志用的全局 loss 必须 `detach`。这是原帖算法题那条「多 AllReduce 几次 loss」，见 `sys-allreduce-loss-scale`。
- **归约粒度。** 先各卡对序列平均再 AVG，长回复被摊薄；先对有效 token 求和再除总 token，才是 token-mean。DAPO / 百度那问见 `baidu-grpo-loss-agg`。
- **动态 batch。** 各 rank 有效 token 数不同，必须按 token 计数同步，不能假定每卡 $B$ 相同，见 `sys-verl-dynamic-bsz`。

HybridEngine / slime colocate 让同一组卡在 generate 和 train 之间 reshard，backward 仍由原来的训练后端执行。权重推回引擎是参数广播或 delta，见 `infra-rl-weight-sync`，也不走 backward 图。反传落在 Actor 训练图上；通信仍是 DP/TP/PP/EP；多出来的是 loss 怎么平均、哪些 tensor 不许进图。

## 追问

**PP 的 backward 和 rollout 能重叠吗？**
异步系统里可以：一池 generate，一池 train。那是流水线，不是 DualPipe。样本会 stale，见 `sys-areal-vs-slime`。
**LoRA 只反传 adapter？**
是。基座冻住则梯度通信量按 adapter 的参数量计算，但 rollout 仍要完整 KV。
**为什么有人说 RL 反传比 SFT 轻？**
去掉 Critic 少一份大网络的 backward；但 $G$ 条长回复的激活可能更重。比较要锁序列长和 $G$，不要只锁「有没有 Critic」。
