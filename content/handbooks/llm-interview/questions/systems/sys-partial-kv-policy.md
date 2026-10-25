---
id: sys-partial-kv-policy
section: systems
order: 273
level: S
title: partial / 异步 rollout 能不能把旧 policy 的 KV cache 接着用？
quick: "同一 policy 版本续写可以复用 KV，换权重后继续生成就要重算 prefix KV，因为 KV 本身也是权重的函数。否则旧 K/V 配新 Q 得到的分布和 logprob 都不属于完整的新策略。跨版本轨迹还要逐 token 记版本，并对旧段做 mask 或截断 IS。"
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

同一 policy 版本续写可以保留 KV，换成新权重继续生成时就要重算前缀。比如一条 partial rollout 跨过 `update_weights`，旧缓存记录的是旧参数算出的 K/V，不能直接交给新参数的 Q。半截 token 本身也仍有旧策略来源，abort 和回收机制见 `slime-dynamic-partial`。

## KV 为什么随权重改变

$$
K_t^{\mathrm{old}},V_t^{\mathrm{old}}=f_{\theta_{\mathrm{old}}}(x_{\le t}),\qquad
K_t^{\mathrm{new}},V_t^{\mathrm{new}}=f_{\theta_{\mathrm{new}}}(x_{\le t}).
$$

注意力拿旧 K/V 和新 Q 做点积，得到的不是 $\pi_{\theta_{\mathrm{new}}}$ 的条件分布。logprob 会错，后面的 ratio 也会错。prefix cache / RadixAttention 能复用，是因为 **权重没变**。

因此要区分几种后续用途：

- **同版本续写**：同一 episode 仍由 $\theta_{\mathrm{old}}$ 生成，KV 留下，逐 token 生成（decode） 从断点接着走。这是 partial 的吞吐收益。
- **换版本接着生成**：AReaL 的 interruptible worker 在 `update_weights` 时丢掉旧 KV，用新权重算 prefix，再继续未完成序列。轨迹会由两段不同 $\theta$ 拼起来，必须按 token 记版本。
- **换版本但拿去训练、不再续写**：KV 可以扔。训练图会重新 forward 整段（或 mask 掉旧前缀）。留着旧 KV 也帮不上 trainer。

## 续写后怎样处理旧策略样本

异步系统为了利用率，会让未完成请求活过一次权重同步。合法处理只有三条：重算 KV 后当新政策续写；把旧前缀 mask 掉只训新 token；对旧 token 做截断 IS。三条都关 = 用错误的条件分布采样，再假装 $\rho=1$。

flush KV 需要重新 prefill，重建前缀缓存。长 思维链（CoT，即分步推理过程） 上这很贵，所以 AReaL 才把「何时打断、打断后是否重算」当成系统旋钮，而不是默认永远复用。slime 的 `--mask-offpolicy-in-partial-rollout` 走的是训练侧 mask，默认并不宣称跨版本 KV 可复用。

恢复续写时，要同时确认缓存版本和训练时使用的 token mask / IS 权重；prefix cache 跨 checkpoint 也要遵守相同的版本约束。

## 追问

**只更新 LoRA，base 冻住，KV 能复用吗？**
严格说不能：Q/K/V 投影只要有 adapter，K/V 就变。近似复用是在赌 adapter 很小，评测和 ratio 会 silently 偏。
**量化 rollout（FP8 KV）+ BF16 训练呢？**
那是精度隙，不是版本隙。训练图仍要重算 logp，见 `meituan-verl-recompute-logprob`。KV 能不能跨版本复用，和 dtype 无关。
**MoE 路由变了呢？**
更不能复用。旧 KV 来自另一组 expert，连 hidden 都不在同一子网络上，见 `sys-moe-train-infer-routing-mismatch`。
