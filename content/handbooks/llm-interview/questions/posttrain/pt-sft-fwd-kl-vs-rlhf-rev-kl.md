---
id: pt-sft-fwd-kl-vs-rlhf-rev-kl
section: posttrain
order: 220
level: S
title: SFT 在最小化哪种 KL？RLHF 又在最小化哪种？
quick: >-
  SFT / MLE 等价于 $\min D_{\mathrm{KL}}(p_{\mathrm{data}}\|\pi)$，正向、mode-covering。RLHF
  的主项是 $\max\mathbb{E}_{\pi}[r]$，等价于让 $\pi$ 去贴 $p^*\propto\pi_{\mathrm{ref}}e^{r/\beta}$，是反向
  KL；外加的 $\beta D_{\mathrm{KL}}(\pi\|\pi_{\mathrm{ref}})$ 也是反向。两阶段方向不同，不能说「对齐都在做正向
  KL」。
tags:
  - KL
  - SFT
  - RLHF
  - Post-Training
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-21
sources:
  - title: Direct Preference Optimization
    url: https://arxiv.org/abs/2305.18290
    type: primary
  - title: Forward vs Reverse KL in LLM Training
    url: https://www.hassanhamad.com/blog/forward-vs-reverse-kl/forward-vs-reverse-kl.html
    type: secondary
---

这是后训练八股里最常被连问的一张对照表。别答「SFT 和 RLHF 都在减小 KL」。方向由 **谁采样** 决定：数据固定、模型去覆盖，是正向；当前策略采样、去贴一个目标峰，是反向。白板定义见 `fund-kl-directions`。把两阶段说成同一种散度，后面蒸馏、DPO、GRPO 的公式都会写反。SFT 等价于 $\min D_{\mathrm{KL}}(p_{\mathrm{data}}\|\pi)$，mode-covering；RLHF 在最小化 $D_{\mathrm{KL}}(\pi\|\pi^*)$ 并外加反向 $D_{\mathrm{KL}}(\pi\|\pi_{\mathrm{ref}})$，mode-seeking。先 covering 铺技能，再 seeking 按奖励收窄，这是两阶段而不是重复同一项 KL。

## SFT：正向 KL，mode-covering

SFT 最大化 $\mathbb{E}_{y\sim p_{\mathrm{data}}}[\log\pi(y\mid x)]$。因为交叉熵分解

$$
H(p_{\mathrm{data}},\pi)=H(p_{\mathrm{data}})+D_{\mathrm{KL}}(p_{\mathrm{data}}\|\pi),
$$

$H(p_{\mathrm{data}})$ 与 $\pi$ 无关，MLE 等价于最小化正向 $D_{\mathrm{KL}}(p_{\mathrm{data}}\|\pi)$。期望在 **数据** 上取：数据里出现过的模式，模型都得给质量，漏峰会让 $\log(p/\pi)$ 爆炸。所以 SFT 是 mode-covering：宁可把分布摊「糊」，也不敢漏掉示范里的写法、格式、偶发毒性。多峰示范（同一问题几种都对的说法）会把概率摊开，这是正向 KL 的几何，不是数据没洗干净那么简单。

工程含义：SFT 擅长把「见过的都学会」，不擅长主动丢掉示范里不想要的峰。对齐如果只做 SFT，有害或啰嗦模式只要在数据里出现，模型就被逼着覆盖。同一问题多种都对的写法会把概率摊开，生成时显得「什么都能说一点、什么都不锋利」，这是 covering 的几何，不一定是温度没调。清洗示范能减少坏峰，但不能把正向 KL 变成 seeking：只要坏峰还在经验分布里，MLE 就得给质量。所以「多做 SFT 代替 RLHF」在方向上就接不上，SFT 没有「允许遗忘」这一项。

## RLHF：反向 KL，mode-seeking

带 KL 约束的 RLHF 目标（InstructGPT / DPO 同一族）写成

$$
\max_\pi\ \mathbb{E}_{x\sim\mathcal{D},\,y\sim\pi}[r(x,y)]-\beta\,D_{\mathrm{KL}}\big(\pi(\cdot\mid x)\,\|\,\pi_{\mathrm{ref}}(\cdot\mid x)\big).
$$

闭式最优策略 $\pi^*(y\mid x)\propto\pi_{\mathrm{ref}}(y\mid x)\,e^{r(x,y)/\beta}$。对正在优化的 $\pi$ 来说，这是在最小化 $D_{\mathrm{KL}}(\pi\|\pi^*)$：期望在 **当前策略** 上取，反向、mode-seeking。可以丢掉 $\pi_{\mathrm{ref}}$ 里不想要的峰（脏话、胡话），但不能跑到 $\pi_{\mathrm{ref}}\approx 0$ 的区域去黑奖。外加的 $\beta D_{\mathrm{KL}}(\pi\|\pi_{\mathrm{ref}})$ 本身也是反向：惩罚的是策略发明参考不会说的续写，见 `pt-rlhf-why-reverse-kl`。

主项 $\max\mathbb{E}_\pi[r]$ 已经是「从自己的分布里采、往高奖峰挤」；KL 项只是把可去的峰限制在参考 support 附近。两段都不是正向 KL。现场若把 RLHF 说成「再做一次 SFT 式的 KL」，方向就反了：正向会逼策略继续覆盖 SFT 的每个峰，对齐的收窄被抵消。用两个峰讲死：参考在「有用回答」和「有害但示范里见过」上都有质量。SFT 必须盖住有害峰；RLHF 的反向 KL 允许不采它，只要奖励不在那一侧给分。这和 `fund-kl-directions` 的三格表是同一套直觉，只是 $p$ 换成数据或 $\pi^*$、$q$ 换成 $\pi$。奖励若在有害峰上也高（RM 被骗），反向 KL 仍然挡「参考几乎为零的新胡话」，挡不住「参考里就有的拍马」，那要靠奖励和数据，不能怪 KL 方向。

## 两阶段不要混，蒸馏也按采样切

SFT 的 $p$ 是数据、$\pi$ 是模型，正向 covering；RLHF 的 $p^*$ 是「参考乘上 exp 奖励」、$\pi$ 去贴它，反向 seeking。同一套表在 `fund-kl-directions`：漏峰时正向 KL 爆、反向 KL 假装没看见。聊天对齐正好要「假装没看见」有害峰；这不是 bug。

蒸馏接在这张表上：教师轨迹或全词表 CE 仍是正向，学生必须覆盖教师所有峰，生成任务里容易把低概率尾巴学糊。OPD / MiniLLM 改成学生采样，目标变成 $D_{\mathrm{KL}}(\pi_S\|\pi_T)$，切到反向，见 `pt-kd-forward-vs-reverse`。方向仍然由采样分布决定，不由「这是蒸馏还是 RL」的名称决定。

DPO 从带 **反向** KL 的 RLHF 目标换元而来；把 SFT 的正向 KL 直接写进 DPO 间隔，最优策略的闭式就对不上。现场推导应先写 $\pi^*\propto\pi_{\mathrm{ref}}e^{r/\beta}$，再写出 $D_{\mathrm{KL}}(\pi\|\pi^*)$，不要从 CE 硬拐。PPO 实现里 KL 估在 rollout 上，天然是反向；若有人提议「改成对 SFT 数据做 CE 当正则」，那就把采样改回数据分布，变成又一次 SFT，和 on-policy 奖励项的期望都不在同一分布上。两阶段衔接我会说：先正向 covering 把格式和技能铺上，再反向 seeking 按奖励收窄。

白板用三行就够：SFT 期望在 $p_{\mathrm{data}}$ 上、正向、covering；RLHF 期望在 $\pi$ 上、反向、seeking；蒸馏看学生还是教师采样。方向反了，SFT 会漏示范，RLHF 会逼着留下有害峰。SFT 阶段你在逼模型把数据里出现过的说法都学会，所以会糊、会覆盖多峰；RLHF 阶段你在用当前策略采样去贴 $\pi^*\propto\pi_{\mathrm{ref}}e^{r/\beta}$，所以会收窄、会寻求高奖模式，并靠反向 KL 挡住参考支撑之外的胡话。面试把采样对象说清，公式左右就不会写反。

## 追问

- **正向 / 反向看公式左边还是看采样？** 看采样。token 从谁来，期望就在谁上。左右写反是白板事故，比记不住符号更致命。现场先写 $\mathbb{E}_{y\sim ?}$，问号填完再写 log 比。SFT 填数据，RLHF 填当前策略，不要都填成参考模型。
- **RLHF 的 KL 改成 CE 行吗？** CE 展开是正向 KL 加参考熵，期望跑到 $\pi_{\mathrm{ref}}$ 上，和 PPO rollout 对不上，见 `ant-kl-vs-ce`。那会逼策略继续覆盖参考的每个峰，对齐要的收窄被抵消。
- **SFT 已经 covering，为什么对齐还要 KL？** 因为 RL 主项会寻求高奖模式，没有反向 KL 就会离开参考 support。SFT 的正向 KL 管的是拟合示范，管不住黑奖。两阶段方向不同，不能互相替代。
- **探索场景还要坚持反向吗？** 不一定。稀有可验证正确路径若在参考长尾，mode-seeking 会把它们掐掉，见 `pt-kl-direction-and-exploration`。对齐选反向是因为更怕跑出支撑，不是一切任务都优于正向。奖励很干净时可以放宽 $\beta$，而不是把方向写反。SFT 正向、RLHF 反向，这张表先讲死再谈例外。对照见 `fund-kl-directions`。
