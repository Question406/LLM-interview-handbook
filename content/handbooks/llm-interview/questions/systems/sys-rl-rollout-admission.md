---
id: sys-rl-rollout-admission
section: systems
order: 266
level: S
title: RL 训练如何准入、丢弃或重试 rollout，而不是把轨迹一股脑塞进 batch？
quick: >-
  这不是 API 过载的 429。训练环要决定轨迹进不进本步更新：超长截断或丢掉、全对/全错组丢掉重采、policy
  stale 降权或丢弃、verifier 超时重试而不是当 0 分。优化的是吞吐、freshness 和有效梯度，不是 SLO。
tags:
  - RL Infra
  - Admission Control
  - Rollout
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-21
sources:
  - title: HybridFlow / veRL
    url: https://arxiv.org/abs/2409.19256
    type: primary
---

这块容易讲成 LLM API 过载时的拒绝与排队。那是 `sys-admission-control`：保护 TTFT / error budget，容量单位是 token 与 KV。本题发生在 **RL 训练环**：轨迹已经在生成或刚打完分，要不要放进这一步的训练 batch。判据不是用户 SLO，而是这批样本对 $\pi_\theta$ 有没有有效梯度、会不会把一步墙钟和 off-policyness 搞砸。HybridFlow 把 generation、reward、advantage、update 拆成可组合 dataflow；准入是这条 dataflow 的闸门，不是网关限流。

## 四类闸门：长度、零方差组、stale、verifier

先画时间轴，见 `sys-rl-grpo-loop-roles`：rollout $\to$ reward $\to$ advantage $\to$ update。每一段都可以把样本挡在 batch 外。

- **长度。** 长 CoT / 长 episode 占满 KV，一步墙钟跟最长那条走。超过 `max_response_len` 应截断并打 `truncated`，不要假装 EOS；再长就丢掉或拆到下一 micro-batch，按每卡 token 帽拼，见 `sys-verl-dynamic-bsz`。短任务可以填气泡，但不要为了填满而把未完成的超长轨迹提前当负例。
- **全对 / 全错组。** GRPO 的 $\hat A_i=(r_i-\mathrm{mean}(r))/(\mathrm{std}(r)+\varepsilon)$ 在 $\mathrm{std}(r)=0$ 时为 0，这步白算，见 `sys-rl-group-n`。准入应丢掉零方差组并重采（DAPO 动态采样），而不是把 $n$ 条满分轨迹送进 backward。名义组数和有效组数要对账。
- **Stale policy。** 异步栈里轨迹带 `policy_version`。Gap 过大则 $\rho=\pi_\theta/\pi_{\mathrm{old}}$ 偏离 1，方差爆炸。按最大 gap 丢弃或按 age 降权，盯 KL 与 $\rho$ 分位数，见 `sys-rl-infra`。Freshness 是算法约束，不是「旧数据也能当 SFT」。
- **Verifier / 环境超时。** Sandbox、编译器、裁判没在 deadline 返回，不能默默当 $r=0$。那会学到「超时=失败」。应 retry、标 `unknown` 不进 batch，或走部分信用；超时杀死要记原因，避免把环境故障写成策略差。

决策只有三种：**accept / drop / retry**。排队在训练里对应「下一 micro-batch 再拼」，不是无限 FIFO。和 serving 的对照一句就够：那边保的是 deadline，这边保的是 **有效优势与版本对齐**。

## 和吞吐旋钮怎么一起拧

准入会改「一步看见几条」，不要和动态 batch、动态采样当成同一个开关。动态 batch 管显存形状；动态采样管零方差组；本题管 **这条轨迹配不配进当前更新**。超长先砍尾部再拼 token 帽；有效组比例低先滤零方差再加 $n$；stale 高就降异步 gap 或丢掉旧轨迹，而不是先加学习率。Agent 场景还要算 sandbox 槽位：同时进行的长 episode 太多，GPU 等环境，整群空转，见 `sys-rl-infra`。

指标不要报平均 reward：admission 率、按原因的 drop 直方图、零方差组占比、轨迹年龄、verifier 超时率、tokens/step、最长尾。平均分好看可能只是全对组没被丢掉。过载时优先 drop 无信息样本（零方差、未知超时、过期版本），而不是随机丢短轨迹。短轨迹往往是能填气泡的有效梯度。

## 追问

- **和 `sys-admission-control` 差在哪？** 那题是在线 API：按 SLO 拒绝、排队、降级。本题是训练：按长度、组方差、policy 版本、verifier 完整性决定进 batch。不要用 429 回答 GRPO 零梯度。
- **超时轨迹当 0 分行不行？** 不行。环境故障会被当成策略错误。Retry 或标 unknown；只有确认「模型自己写不完」才打截断惩罚。
- **全对组为什么必须 drop？** $\hat A=0$，backward 白做还占 token 帽。丢掉重采是为了有效 $n$，不是为了让准确率数字更好看。
- **stale 到多少必须丢？** 看 $\rho$ 分位数和 KL，而不是固定步数。Gap 允许范围是算法选择；超过就丢，比硬训更干净。
- **重试会不会让 off-policy 更严重？** 会。Retry 期间 $\theta$ 可能又更新了。重试也要带 `policy_version`，超时预算算进 admission，避免重试风暴占满 sandbox。
---
