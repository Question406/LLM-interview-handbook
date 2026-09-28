---
id: sys-partial-kv-policy
section: systems
order: 273
level: S
title: partial / 异步 rollout 能不能把旧 policy 的 KV cache 接着用？
quick: >-
  KV 是权重的函数。同一条轨迹、同一个 rollout 版本接着写，保存 KV 是对的。权重一旦更新还想用新 $\pi$ 续写，必须重算
  prefix KV，否则 logits / logprob 都不是新策略的。工程上可以留着旧 KV，但要把这段标成旧版本，mask 或 TIS，不能当 on-policy
  prefix。
tags:
  - Partial Rollout
  - KV Cache
  - Staleness
  - AReaL
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-23
sources:
  - title: AReaL
    url: https://arxiv.org/abs/2505.24298
    type: primary
  - title: slime 使用文档
    url: https://thudm.github.io/slime/zh/get_started/usage.html
    type: primary
  - title: vLLM PagedAttention
    url: https://arxiv.org/abs/2309.06180
    type: primary
---

partial rollout 怎么 abort / 回收半截，见 `slime-dynamic-partial`。那张卡强调半截 **token** 不是新的 on-policy。本题再问一层：**半截的 KV 能不能留给下一版权重**。

## KV 跟的是 $\theta$，不是文本

$$
K_t^{\mathrm{old}},V_t^{\mathrm{old}}=f_{\theta_{\mathrm{old}}}(x_{\le t}),\qquad
K_t^{\mathrm{new}},V_t^{\mathrm{new}}=f_{\theta_{\mathrm{new}}}(x_{\le t}).
$$

注意力拿旧 K/V 和新 Q 做点积，得到的不是 $\pi_{\theta_{\mathrm{new}}}$ 的条件分布。logprob 会错，后面的 ratio 也会错。prefix cache / RadixAttention 能复用，是因为 **权重没变**。

所以：

- **同版本续写**：同一 episode 仍由 $\theta_{\mathrm{old}}$ 生成，KV 留下，decode 从断点接着走。这是 partial 的吞吐收益。
- **换版本接着生成**：AReaL 的 interruptible worker 在 `update_weights` 时丢掉旧 KV，用新权重算 prefix，再继续未完成序列。轨迹会由两段不同 $\theta$ 拼起来，必须按 token 记版本。
- **换版本但拿去训练、不再续写**：KV 可以扔。训练图会重新 forward 整段（或 mask 掉旧前缀）。留着旧 KV 也帮不上 trainer。

## 和 stale 样本怎么同时讲

异步系统为了利用率，会让未完成请求活过一次权重同步。合法处理只有三条：重算 KV 后当新政策续写；把旧前缀 mask 掉只训新 token；对旧 token 做截断 IS。三条都关 = 用错误的条件分布采样，再假装 $\rho=1$。

flush KV 的代价是 prefill 重算。长 CoT 上这很贵，所以 AReaL 才把「何时打断、打断后是否重算」当成系统旋钮，而不是默认永远复用。slime 的 `--mask-offpolicy-in-partial-rollout` 走的是训练侧 mask，默认并不宣称跨版本 KV 可复用。

同权续写可以留 KV；换权必须重算，或把旧段标成 off-policy。prefix cache 不能跨 checkpoint 白用。

## 追问

- **只更新 LoRA，base 冻住，KV 能复用吗？** 严格说不能：Q/K/V 投影只要有 adapter，K/V 就变。近似复用是在赌 adapter 很小，评测和 ratio 会 silently 偏。
- **量化 rollout（FP8 KV）+ BF16 训练呢？** 那是精度隙，不是版本隙。训练图仍要重算 logp，见 `meituan-verl-recompute-logprob`。KV 能不能跨版本复用，和 dtype 无关。
- **MoE 路由变了呢？** 更不能复用。旧 KV 来自另一组 expert，连 hidden 都不在同一子网络上，见 `sys-moe-train-infer-routing-mismatch`。
