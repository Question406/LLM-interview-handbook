---
id: arl-gigpo
section: agentrl
order: 122
level: S
title: 多轮 Agent 上 GRPO 不够用时，GiGPO 的两层组相对优势在比什么？
quick: >-
  GiGPO 做两层组相对：外层和 GRPO 一样比同一任务的整条轨迹，内层把不同轨迹里重复出现的环境状态收成一组，比从这个状态出发的不同动作。这样不另训
  Critic 也能估逐步优势，比把终局 0/1 广播到几十步更细，前提是状态能哈希对齐。
tags:
  - GiGPO
  - Credit Assignment
  - Agent RL
  - GRPO
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-24T00:00:00.000Z
sources:
  - title: Group-in-Group Policy Optimization for LLM Agent Training
    url: 'https://arxiv.org/abs/2505.10978'
    type: primary
  - title: Trinity-RFT GiGPO
    url: >-
      https://agentscope-ai.github.io/Trinity-RFT/en/main/build_api/trinity.algorithm.advantage_fn.gigpo_advantage.html
    type: secondary
---

GiGPO 在两层上做组相对比较。外层和 GRPO 一样，比同一任务的几条完整轨迹谁更好；内层把不同轨迹里重复出现的同一个环境状态收成一组，比从这个状态出发的不同动作谁更好。这样不用另训 Critic，也不用多采一套 sampling 轨迹（rollout），就能估出逐步的相对优势，前提是状态能哈希对齐。

普通 GRPO 不够用，是因为它把结局奖励广播到所有 action token 上，50 步的工具轨迹里很难分清各步的贡献，见 `arl-credit`、`arl-vs-reasoning`。原帖 35 题没把 LLM RL 和 Agentic RL 拆开，但这一问放到 Agent 上，答案会变。

举个家居任务的例子：好几条轨迹都走到了「站在厨房、柜子关着」这个状态，有的接着打开柜子，有的转身去了客厅。把这几次选择收成一组，比较各自后面的折扣回报，就能看出在这个状态下开柜子比去客厅好。内层组比的就是这个。

## 两层组

外层是 episode 级：同一任务的 $G$ 条完整轨迹，用回报算出和 GRPO 一样的宏观 $\hat A_E$，告诉模型这局整体比组内均值好还是差。内层是 step 级，也叫 anchor state：跨轨迹找重复的环境状态，论文用状态哈希，Trinity 里对应 `env_state_hash`；从同一状态出发的不同动作收成一组，用折扣回报 $R_t$ 再算微观 $\hat A_S$。只出现一次的 anchor state $\hat A_S=0$，没有对照就不硬编逐步优势。

两者合成后，广播到该步的 action token：

$$
\hat A=\hat A_E+\omega\hat A_S.
$$

$\omega$ 控制逐步优势的权重。$\gamma$ 仍然是逐步折扣，别和外层组均值拧成一个超参。默认 agent 基准上，逐步项甚至可以不做 std 归一（`fnorm=none`），免得小 anchor-state group 把噪声放大，对照 `fund-adv-norm-bias`。

## 什么时候别用

论文（`2505.10978`）在 ALFWorld、WebShop、搜索增强 QA 上有效，因为这些环境有可重复的 anchor state：房间、模板页、可哈希的检索状态。完全开放、每次 DOM 都不一样的网页，内层组是空的，GiGPO 就退回普通 GRPO。状态哈希要是把无关的 UI 噪声算进去，又会把不该一组的动作捆在一起。

PRM 或逐步规则分是另一条 dense 路线，见 `pt-prm-orm-critic`、`byte-agentic-rl-process-reward`。GiGPO 不训练打分头，靠的是组内对照。两条路各有风险：过程奖励会被 hack，anchor-state hashing 会分错组。

## 追问

**和 GAE / Critic 比怎么样？**
Critic 估 $V(s)$，要多一个价值头，也会遇到估计随策略更新而过时的问题。GiGPO 用组统计代替 $V$，代价是状态必须能对齐。

**工具返回要不要进组？**
观察属于环境，只有动作进 $\pi$，token mask 见 `pt-agent-grpo-token-mask`。哈希要对齐环境状态，别把 chain of thought 文本算进 state id。

**多 Agent 能用吗？**
GiGPO 论文做的是单 Agent 多步。多人还要分清是谁的动作，见 `arl-multi-credit`，别把 GiGPO 说成已经解决了 team 奖励分数（reward）。

**和过程奖励怎么选？**
有可验证的事件，先设计过程评分规则；有重复状态，再分组。选型见 `arl-process-vs-gigpo`。
