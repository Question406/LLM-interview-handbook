---
id: pt-reference-model-refresh
section: posttrain
order: 234
level: A
title: PPO / DPO 的 reference model 何时该刷新，何时必须冻结？
quick: >-
  单阶段、需要复现和审计时冻结 $\pi_{\mathrm{ref}}$；做了几轮迭代偏好或 RL、能力已明显超过初始 SFT，再周期性刷新到近期强
  checkpoint，放开优化空间。刷新等于换尺子，$\beta$、KL 目标和 evaluation protocol 要一起改，否则涨分只是约束变松。
tags:
  - KL Penalty
  - DPO
  - PPO
  - Reference Policy
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-21T00:00:00.000Z
sources:
  - title: Direct Preference Optimization
    url: 'https://arxiv.org/abs/2305.18290'
    type: primary
  - title: InstructGPT
    url: 'https://arxiv.org/abs/2203.02155'
    type: secondary
---

$\pi_{\mathrm{ref}}$ 是 KL 的 reference policy。单阶段训练、需要复现或审计相对 SFT 的偏离时，就冻结它；做了几轮迭代偏好或 RL、能力已经系统性高过初始 SFT 时，可以刷新到近期的强 checkpoint。但刷新等于换了尺子，$\beta$、KL 目标和 reporting convention 都得跟着改，否则涨的分只是约束变松了。

为什么说是换尺子。PPO 罚的是 $\mathrm{KL}(\pi_\theta\|\pi_{\mathrm{ref}})$，DPO 的隐式奖励是

$$
r_\theta(x,y)=\beta\log\frac{\pi_\theta(y\mid x)}{\pi_{\mathrm{ref}}(y\mid x)}.
$$

reference policy 越旧越保守，越新约束越弱，等于当前策略时就没有约束了。刷新会同时改变可优化的空间和隐式奖励的零点。InstructGPT 把 SFT 策略当 RL 的起点，让相对这个锚的偏离可以讲清楚；DPO 的推导也假设一次优化里 ref 是固定的。

冻结的场景很明确：单阶段、数据一次性给齐、要复现实验，或者监管要求能审计相对 SFT 基线的偏离。offline DPO 里 $\pi_{\mathrm{ref}}$ 是隐式奖励的分母，中途换掉等于换了奖励坐标系，chosen / rejected 的间隔就不可比了。要对照 $\mathrm{KL}(\pi\|\pi_{\mathrm{SFT}})$ 曲线，ref 版本也得固定。这时候「KL 太大」往往是能力离开过时基线的真实代价，偷换 ref 只是假装约束还在。极端情况是 $\pi_{\mathrm{ref}}=\pi_\theta$：DPO 的 log 比为 0、梯度消失，PPO 的 KL 项也没了锚，所以「把 ref 设成当前策略」等于拆掉正则。冻结还有一个好处，能回答监管式的追问：相对哪一条 SFT、KL 多少、安全回退多少，定义不会每周换一次。

刷新适合迭代的场景。比如先 SFT，再做两轮 iterative DPO：第二轮还拿 SFT 当 ref，偏好梯度要对抗很大的 KL；换成上一轮胜出的策略，同样的 $\beta$ 更能吸收新 pair，但要盯着 safety 和格式有没有回归。常见做法是 $\pi_{\mathrm{ref}}\leftarrow\pi_{\theta_t}$ 或 EMA，同时重置 KL 控制器的目标、重标 $\beta$。一直锚在旧 ref 上，KL 预算都花在「离开过时基线」上，没花在新能力上的精调。

刷新之后有几件事要跟上。评估如果还对比最初的 SFT，训练 KL 却已经相对新 ref，你看的就是两套尺子，对外报告要同时给 $\mathrm{KL}(\pi\|\pi_{\mathrm{SFT}})$ 和 $\mathrm{KL}(\pi\|\pi_{\mathrm{ref}}^{\mathrm{new}})$。约束变松后 proxy 会涨，过优化也来得更快，见 `pt-reward-ood-failure`。刷新节奏别快过数据 freshness：ref 已经追上当前策略、pair 还是旧的，等于锚松开了却没有新监督。EMA 比硬切换平滑，但有滞后，容易让 KL 控制器误判，切换当时就要重置目标值，别沿用旧 setpoint。每次刷新后都要把安全回归集跑一遍，KL 突然变小的那几步最容易丢掉 refusal criteria。

用 trust region 的话说：冻结 ref 是全程待在同一个邻域里，刷新是把邻域搬到新中心。搬完要重新声明半径，也就是 $\beta$ 或 KL 目标，否则中心变了、半径还在旧尺度上，约束名存实亡。面试时我会先问一句「现在的 KL 相对哪一条策略」，定义不一致，就先别谈涨分。

## 追问

**刷新是免费涨分吗？**
不是。约束变松，proxy 会涨，过优化和安全回退也会更快。

**offline DPO 能中途换 ref 吗？**
不建议。隐式奖励的坐标系会漂，旧 pair 的间隔就失效了。要换就新开一个阶段，并写明 ref 版本。

**EMA 和硬切换怎么选？**
EMA 更平滑但滞后更大；硬切换要立刻重调 KL 目标，否则控制器会以为突然违约了。

**刷新后 $\beta$ 还能沿用吗？**
通常不能沿用旧表。新 ref 离当前策略更近，同样的 $\beta$ 有效约束更弱，刷新后一般要重新扫一遍 $\beta$。
