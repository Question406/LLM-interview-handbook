---
id: arl-gigpo
section: agentrl
order: 122
level: S
title: 多轮 Agent 上 GRPO 不够用时，GiGPO 的两层组相对优势在比什么？
quick: >-
  单轮数学 GRPO 比的是同一题的整条回复。多轮 Agent 终局 $0/1$ 会灌进几十步工具调用，分不清哪一步值钱。GiGPO
  外层仍按整条轨迹做组相对优势，内层把不同轨迹里重复出现的环境状态收成一组，对从该状态出发的动作再比一次。不另训
  Critic，但前提是状态能哈希对齐。
tags:
  - GiGPO
  - Credit Assignment
  - Agent RL
  - GRPO
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-24
sources:
  - title: Group-in-Group Policy Optimization for LLM Agent Training
    url: https://arxiv.org/abs/2505.10978
    type: primary
  - title: Trinity-RFT GiGPO
    url: https://agentscope-ai.github.io/Trinity-RFT/en/main/build_api/trinity.algorithm.advantage_fn.gigpo_advantage.html
    type: secondary
---

原帖 35 题没把 LLM RL 和 Agentic RL 拆开，但同一问在 Agent 上答案会变。普通 GRPO 把结局奖励广播到所有 action token，50 步工具轨迹上这就是粗信用，见 `arl-credit`、`arl-vs-reasoning`。GiGPO（`2505.10978`）要在 **不训 Critic、不多采一套 rollout** 的前提下，给逐步相对优势。

## 两层组

**外层（episode）。** 同一任务的 $G$ 条完整轨迹，用回报做和 GRPO 一样的宏观 $\hat A_E$。这条告诉模型「这局整体比组内均值好不好」。

**内层（step / anchor state）。** 跨轨迹找重复的环境状态（论文用状态哈希；Trinity 里是 `env_state_hash`）。从同一状态出发的不同动作收成一组，用折扣回报 $R_t$ 再算微观 $\hat A_S$。只出现一次的锚点 $\hat A_S=0$，没有对照就不硬编逐步优势。

合成后广播到该步的 action token：

$$
\hat A=\hat A_E+\omega\hat A_S.
$$

$\omega$ 管逐步信号有多响。$\gamma$ 仍是逐步折扣，不要和外层组均值拧成一个超参。默认 agent 基准上逐步项甚至可以不做 std 归一（`fnorm=none`），避免小锚点组把噪声放大，对照 `fund-adv-norm-bias`。

## 什么时候别用

论文在 ALFWorld、WebShop、搜索增强 QA 上有效，因为这些环境有可重复的锚点（房间、模板页、可哈希检索状态）。完全开放、每次 DOM 都不同的网页，内层组是空的，GiGPO 退回普通 GRPO。状态哈希若把无关 UI 噪声算进去，会把不该一组的动作捆在一起。

PRM / 逐步规则分是另一条 dense 路，见 `pt-prm-orm-critic`、`byte-agentic-rl-process-reward`。GiGPO 不训练打分头，用的是 **组内对照**。过程奖励会 hacking；锚点哈希会错组。和过程分怎么选，见 `arl-process-vs-gigpo`。

现场口令：外层比轨迹，内层比「同一状态下换一个动作」。没有重复状态，就没有内层。

## 追问

- **和 GAE / Critic？** Critic 估 $V(s)$，要多一个头、多一份 stale。GiGPO 用组统计代替 $V$，换的是必须能对齐状态。
- **工具返回要不要进组？** 观察是环境，动作才进 $\pi$。token mask 见 `pt-agent-grpo-token-mask`。哈希应对齐环境状态，不要把思维链文本算进 state id。
- **多 Agent？** GiGPO 论文是单 Agent 多步。多人还要分谁的动作，见 `arl-multi-credit`。不要把 GiGPO 说成已经解决 team reward。
- **和过程奖励怎么选？** 有可验证事件先写门；有重复状态再分组。选型见 `arl-process-vs-gigpo`。
