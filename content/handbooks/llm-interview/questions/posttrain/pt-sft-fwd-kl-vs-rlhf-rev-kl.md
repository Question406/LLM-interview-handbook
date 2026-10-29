---
id: pt-sft-fwd-kl-vs-rlhf-rev-kl
section: posttrain
order: 220
level: S
title: SFT 在最小化哪种 KL？RLHF 又在最小化哪种？
quick: >-
  方向看谁在 sampling。SFT 的期望取在数据上，最小化正向
  $D_{\mathrm{KL}}(p_{\mathrm{data}}\|\pi)$，mode-covering；RLHF 在当前策略
  upsampling，最小化反向 $D_{\mathrm{KL}}(\pi\|\pi^*)$，mode-seeking。先 covering 铺技能，再
  seeking 按奖励收窄。
tags:
  - KL
  - SFT
  - RLHF
  - Post-Training
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-21T00:00:00.000Z
sources:
  - title: Direct Preference Optimization
    url: 'https://arxiv.org/abs/2305.18290'
    type: primary
  - title: Forward vs Reverse KL in LLM Training
    url: >-
      https://www.hassanhamad.com/blog/forward-vs-reverse-kl/forward-vs-reverse-kl.html
    type: secondary
---

SFT 等价于 $\min D_{\mathrm{KL}}(p_{\mathrm{data}}\|\pi)$，也就是 forward KL，mode-covering；RLHF 最小化的是 reverse KL，$D_{\mathrm{KL}}(\pi\|\pi^*)$，外加一项反向的 $D_{\mathrm{KL}}(\pi\|\pi_{\mathrm{ref}})$，mode-seeking。方向由谁 sampling 决定：数据固定、模型去覆盖，是正向；当前策略自己 sampling、去贴一个目标峰，是反向。这是后训练八股里最常被连问的一张对照表，答成「两个都在减小 KL」不够，两阶段方向一旦说成同一种，后面 distillation、DPO、GRPO 的公式都会写反。白板定义见 `fund-kl-directions`。

用两个峰最好讲。假设 reference model 在「有用回答」和「有害但示范里出现过」两处都有概率。SFT 必须把有害峰也盖住；RLHF 的 reverse KL 允许不去采它，只要奖励不在那一侧给分。所以流程是先 covering 铺技能，再 seeking 按奖励收窄，两阶段做的是两件事。

## SFT 为什么是正向

SFT 最大化 $\mathbb{E}_{y\sim p_{\mathrm{data}}}[\log\pi(y\mid x)]$。cross entropy 可以分解成

$$
H(p_{\mathrm{data}},\pi)=H(p_{\mathrm{data}})+D_{\mathrm{KL}}(p_{\mathrm{data}}\|\pi),
$$

$H(p_{\mathrm{data}})$ 和 $\pi$ 无关，所以 MLE 等价于最小化正向 $D_{\mathrm{KL}}(p_{\mathrm{data}}\|\pi)$。期望是在数据上取的：数据里出现过的模式，模型都得分一点概率，漏掉一个峰，$\log(p/\pi)$ 就会爆炸。于是 SFT 宁可让分布更分散，也不敢漏掉示范里的写法、格式，甚至偶发的毒性。

落到工程上，SFT 擅长把见过的都学会，不擅长主动丢掉示范里不想要的峰。只做 SFT 的对齐，有害或啰嗦的模式只要在数据里出现过，模型就被逼着覆盖。同一个问题有几种都对的写法时，概率会被摊开，生成起来「什么都能说一点、什么都不锋利」，这是 covering 的几何，不一定是温度没调好，也不只是数据没洗干净。清洗示范能减少坏峰，但改变不了方向：坏峰还在经验分布里，MLE 就得给它质量。所以「多做 SFT 代替 RLHF」方向上就接不上，SFT 里没有允许遗忘的那一项。

## RLHF 为什么是反向

带 KL 约束的 RLHF 目标（InstructGPT / DPO 同一族）是

$$
\max_\pi\ \mathbb{E}_{x\sim\mathcal{D},\,y\sim\pi}[r(x,y)]-\beta\,D_{\mathrm{KL}}\big(\pi(\cdot\mid x)\,\|\,\pi_{\mathrm{ref}}(\cdot\mid x)\big).
$$

闭式最优策略是 $\pi^*(y\mid x)\propto\pi_{\mathrm{ref}}(y\mid x)\,e^{r(x,y)/\beta}$。这里的目标 $p^*$ 就是「参考乘上 exp 奖励」。对正在优化的 $\pi$ 来说，这等于最小化 $D_{\mathrm{KL}}(\pi\|\pi^*)$，期望在当前策略上取，所以是反向、mode-seeking。它可以丢掉 $\pi_{\mathrm{ref}}$ 里不想要的峰（脏话、胡话），但跑不到 $\pi_{\mathrm{ref}}\approx 0$ 的区域去黑奖励。外加的 $\beta D_{\mathrm{KL}}(\pi\|\pi_{\mathrm{ref}})$ 本身也是反向的，惩罚策略发明 reference model 不会说的续写，见 `pt-rlhf-why-reverse-kl`。

主项 $\max\mathbb{E}_\pi[r]$ 本来就是从自己的分布里 sampling、往高奖励的峰挤；KL 项只是把能去的峰限制在参考的 support 附近。两段都和 forward KL 无关。要是把 RLHF 说成「再做一次 SFT 式的 KL」，方向就反了：正向会逼策略继续覆盖 SFT 的每个峰，对齐要的收窄被抵消。这和 `fund-kl-directions` 的三格表是同一套直觉，只是 $p$ 换成数据或 $\pi^*$，$q$ 换成 $\pi$。漏峰时 forward KL 爆炸、reverse KL 假装没看见，聊天对齐恰好需要对有害峰「假装没看见」，这是设计，不算 bug。也有它管不到的地方：reward model（RM）被骗、在有害峰上也给高分时，reverse KL 挡得住「参考几乎为零的新胡话」，挡不住「参考里本来就有的拍马」，这要靠奖励和数据，怪不到 KL 方向头上。

## distillation、DPO、PPO 也按 sampling 来切

distillation 接在这张表上。用教师轨迹或全 vocabulary 算 cross entropy loss（CE），仍然是正向，学生得覆盖教师所有的峰，生成任务里可能把概率分到较多低概率候选上。OPD / MiniLLM 改成学生 sampling，目标变成 $D_{\mathrm{KL}}(\pi_S\|\pi_T)$，就切到了反向，见 `pt-kd-forward-vs-reverse`。决定方向的始终是 sampling 分布，跟它叫 distillation 还是叫 RL 无关。

DPO 是从带 reverse KL 的 RLHF 目标换元得来的，把 SFT 的 forward KL 直接写进 DPO 的间隔，最优策略的闭式就对不上。现场推导先写 $\pi^*\propto\pi_{\mathrm{ref}}e^{r/\beta}$，再写出 $D_{\mathrm{KL}}(\pi\|\pi^*)$，别从 CE 硬拐过去。PPO 实现里 KL 是在 sampling 轨迹（rollout）上估的，天然是反向。有人提议「改成对 SFT 数据做 CE 当正则」，那就等于把 sampling 改回数据分布，又做了一次 SFT，和 on-policy 的奖励项也不在同一个分布上取期望。

白板上三行就够：SFT 期望在 $p_{\mathrm{data}}$ 上，正向，covering；RLHF 期望在 $\pi$ 上，反向，seeking；distillation 看是学生 sampling 还是教师 sampling。方向弄反了，SFT 会漏示范，RLHF 会被逼着留下有害峰。

## 追问

**正向、反向是看公式左边，还是看 sampling？**
看 sampling，token 从谁那来，期望就取在谁上。现场先写 $\mathbb{E}_{y\sim ?}$，把问号填完再写 log 比：SFT 填数据，RLHF 填当前策略，别都填成 reference model。左右写反是白板事故，比记不住符号还致命。

**RLHF 里的 KL 换成 CE 行不行？**
不行。CE 展开是 forward KL 加参考熵，期望跑到 $\pi_{\mathrm{ref}}$ 上，和 PPO 的 rollout 对不上，见 `ant-kl-vs-ce`。它会逼策略继续覆盖参考的每个峰，对齐要的收窄就没了。

**SFT 已经是 covering 了，对齐为什么还要 KL？**
因为 RL 的主项会去追高奖励的模式，没有 reverse KL 就会离开参考的 support。SFT 的 forward KL 管的是拟合示范，管不住黑奖励，两阶段方向不同，互相替代不了。

**探索场景还要坚持反向吗？**
不一定。稀有但可验证正确的路径如果在参考的长尾里，mode-seeking 会把它们掐掉，见 `pt-kl-direction-and-exploration`。对齐选反向，是因为更怕跑出 support，并不意味着所有任务都比正向好。奖励很干净时可以放宽 $\beta$，方向别写反。先把「SFT 正向、RLHF 反向」讲清楚，再谈例外，对照见 `fund-kl-directions`。
