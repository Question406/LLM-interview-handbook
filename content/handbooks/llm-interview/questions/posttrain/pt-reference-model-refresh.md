---
id: pt-reference-model-refresh
section: posttrain
order: 234
level: A
title: PPO / DPO 的 reference model 何时该刷新，何时必须冻结？
quick: >-
  $\pi_{\mathrm{ref}}$ 定义 KL 锚点：长期冻结可审计但限制能力跃迁；周期性刷新到近期强 checkpoint
  能放开优化空间，但必须同时改 $\beta$ 与评估口径，否则只是约束变松后的假涨分。
tags:
  - KL Penalty
  - DPO
  - PPO
  - Reference Policy
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-21
sources:
  - title: Direct Preference Optimization
    url: https://arxiv.org/abs/2305.18290
    type: primary
  - title: InstructGPT
    url: https://arxiv.org/abs/2203.02155
    type: secondary
---

这块容易把「刷新 $\pi_{\mathrm{ref}}$」当成免费涨分。PPO 罚 $\mathrm{KL}(\pi_\theta\|\pi_{\mathrm{ref}})$，DPO 的隐式奖励是

$$
r_\theta(x,y)=\beta\log\frac{\pi_\theta(y\mid x)}{\pi_{\mathrm{ref}}(y\mid x)}.
$$

$\pi_{\mathrm{ref}}$ 是 KL 锚点：越旧越保守，越新（甚至等于当前策略）约束越弱。刷新会同时改变可优化空间和隐式奖励的零点，必须和 $\beta$、数据 freshness、评估基线一起改。InstructGPT 把 SFT 政策当 RL 起点并保持相对该锚的偏离可叙述；DPO 的推导也假设一次优化里 ref 固定。改锚点等于换尺子。

## 何时必须冻结

单阶段、数据一次性、需要可复现的对齐边界、或监管要求「相对 SFT 基线的偏离可审计」：冻结。Offline DPO 把 $\pi_{\mathrm{ref}}$ 当作定义隐式奖励的分母；训练中途改 ref，等于换了奖励坐标系，chosen / rejected 间隔不可比。要复现实验或对照 $\mathrm{KL}(\pi\|\pi_{\mathrm{SFT}})$ 曲线，ref 必须钉死。此时「KL 太大」往往是能力已经离开过时基线的真实代价，不该靠偷换 ref 假装约束还在。极限情况 $\pi_{\mathrm{ref}}=\pi_\theta$ 时 DPO 的 log 比为 0，梯度消失，PPO 的 KL 项也失去锚。「把 ref 设成当前策略」不是刷新，是拆掉正则。冻结还让你能回答监管式追问：相对哪一条 SFT、KL 多少、安全回退多少，口径不会每周换一次。

## 何时刷新、刷新后改什么

迭代偏好、多轮 RL 后能力已系统性高于初始 SFT：继续锚在旧 $\pi_{\mathrm{ref}}$ 会把 KL 预算耗在「离开过时基线」而非「在新能力面上精调」。常见 $\pi_{\mathrm{ref}}\leftarrow\pi_{\theta_t}$ 或 EMA，并重置 KL 控制器目标、重标 $\beta$。先 SFT 再两轮 iterative DPO：第二轮仍用 SFT 作 ref，偏好梯度要对抗巨大 KL；改用上一轮胜出策略后，同样 $\beta$ 更能吸收新 pair，但要盯 safety / 格式回归。刷新后若评估仍对比最初 SFT，而训练 KL 已改成相对新 ref，你在看两套尺子。对外报告应同时给 $\mathrm{KL}(\pi\|\pi_{\mathrm{SFT}})$ 和 $\mathrm{KL}(\pi\|\pi_{\mathrm{ref}}^{\mathrm{new}})$。约束变松后 proxy 会涨，过优化也会更快，见 `pt-reward-ood-failure`。刷新节奏不要比数据 freshness 更快：ref 已经追上当前策略、pair 还是旧的，等于既松开锚又没有新监督。EMA 刷新比硬切换平滑，但滞后会让 KL 控制器误判，切换当时应重置目标值而不是沿用旧 setpoint。和 trust-region 的关系：冻结 ref 是全程相对同一邻域；刷新是把邻域搬到新中心。搬完必须重新声明半径（$\beta$ 或 KL 目标），否则半径在旧尺度上、中心已变，约束名存实亡。安全回归集在每次刷新后都要跑一遍，因为最容易在「KL 突然变小」的那几步丢掉拒答边界。

冻结是为了可审计的坐标系；刷新是为了别把预算浪费在过时基线上。改 ref 必改 $\beta$ 与报告口径。现场先问「现在的 KL 相对哪一条政策」，口径对不上就不要谈涨分。

## 追问

- **刷新是免费涨分吗？** 不是。约束变松，proxy 会涨，过优化和安全回退也会更快，见 `pt-reward-ood-failure`。
- **Offline DPO 能中途改 ref 吗？** 不建议。隐式奖励坐标系会漂，旧 pair 的间隔失效。应新开阶段并声明 ref 版本。
- **EMA 和硬切换？** EMA 更平滑，滞后更大；硬切换要立刻重调 KL 目标，否则控制器会以为突然违约。
- **和 $\beta$？** 新 ref 更近，同样 $\beta$ 的有效约束更弱。刷新后通常要重新扫 $\beta$，不能沿用旧表。
