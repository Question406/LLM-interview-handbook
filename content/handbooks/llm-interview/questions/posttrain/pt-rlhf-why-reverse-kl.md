---
id: pt-rlhf-why-reverse-kl
section: posttrain
order: 221
level: S
title: 对齐为什么用 $D_{\mathrm{KL}}(\pi_\theta\|\pi_{\mathrm{ref}})$，而不是反过来？
quick: >-
  要惩罚的是「策略跑到参考模型几乎不会说的地方」，这正是反向 KL：期望在 $\pi_\theta$
  下取。正向 $D_{\mathrm{KL}}(\pi_{\mathrm{ref}}\|\pi_\theta)$ 会逼策略继续覆盖参考的所有峰，包括我们想丢掉的毒性模式，也对不上
  DPO 的推导。
tags:
  - KL
  - RLHF
  - DPO
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-19
sources:
  - title: Direct Preference Optimization
    url: https://arxiv.org/abs/2305.18290
    type: primary
  - title: Training language models to follow instructions with human feedback
    url: https://arxiv.org/abs/2203.02155
    type: primary
  - title: A Guide to Reinforcement Learning Post-Training for LLMs
    url: https://huggingface.co/blog/karina-zadorozhny/guide-to-llm-post-training-algorithms
    type: secondary
---

别答「因为 DPO 论文这么写」。要先说惩罚的是哪一种偏离，再让公式对上采样分布。方向反了，护栏会变成「必须把 SFT 的每个峰都留下来」，对齐的收窄被抵消。白板定义见 `fund-kl-directions`。这题常和蚂蚁「KL 能不能改成 CE」连着问：CE 展开后是正向 KL 加参考熵，连期望都在 $\pi_{\mathrm{ref}}$ 上，和 PPO 的 rollout 对不上。先画清「谁采样」，再谈公式左右哪边，比背 $D_{\mathrm{KL}}(\pi\|\pi_{\mathrm{ref}})$ 的写法更不容易写反。

## 惩罚落在当前策略的质量上

记

$$
D_{\mathrm{KL}}(\pi_\theta\|\pi_{\mathrm{ref}})=\mathbb{E}_{y\sim\pi_\theta}\big[\log\pi_\theta(y)-\log\pi_{\mathrm{ref}}(y)\big].
$$

$\pi_\theta$ 在 $\pi_{\mathrm{ref}}\approx 0$ 处放质量，$\log(\pi_\theta/\pi_{\mathrm{ref}})$ 爆炸。这正是防胡话、防 reward hacking 的护栏：参考几乎不会说的续写，代价极高。反过来，$\pi_{\mathrm{ref}}$ 有、$\pi_\theta$ 不去的峰几乎不进期望，所以 **允许遗忘**——SFT 里残留的有害或啰嗦模式可以丢掉。这是 mode-seeking，不是 bug。Reward hacking 经常表现为跑到参考低概率、proxy 高分的区域；反向 KL 正好打在这条路上。正向 KL 打的是「漏掉参考的峰」，对 hacking 几乎不构成直接惩罚。

InstructGPT / PPO-RLHF 的目标可以写成最大化

$$
\mathbb{E}_{y\sim\pi_\theta}[r(x,y)]-\beta\,D_{\mathrm{KL}}(\pi_\theta\|\pi_{\mathrm{ref}}),
$$

奖励在当前策略上取，KL 也必须在当前策略上取，否则两项的期望都不在同一分布上。工程上这也对得上「用 $\pi_\theta$ 做 rollout」的管道。把 KL 从目标里拿掉只留 clip，长期仍可能离开参考；只留 KL 不 clip，单次更新仍可能过猛。对齐配方里两者分工不同，见 `pt-ppo-clip`。面试只强调「防 hacking」而不提遗忘，只答对了一半：反向 KL 同时允许丢掉参考里的有害峰，这才是对齐要的收窄。

## 正向 KL 为什么会抵消对齐

若写成 $D_{\mathrm{KL}}(\pi_{\mathrm{ref}}\|\pi_\theta)$，期望改到 $\pi_{\mathrm{ref}}$ 上。只要参考在某处概率为正，策略在该处接近 0 就会被重罚，于是 $\pi_\theta$ **必须继续覆盖参考的每一个高概率模式**。对齐想做的事恰恰是收窄：提高有用、无害的峰，丢掉毒性、拍马、拒答失败。正向 KL 把「丢掉」变成违法。聊天模型尤其明显：SFT 里残留的过度承诺、泄露风格，正向正则会逼模型继续生成，只为了「覆盖参考」。

采样也不对：正向要从 $\pi_{\mathrm{ref}}$ 抽 token 才能估期望，和 PPO / GRPO 的「当前策略 rollout」不一致。硬换成交叉熵更糟：

$$
H(\pi_{\mathrm{ref}},\pi_\theta)=H(\pi_{\mathrm{ref}})+D_{\mathrm{KL}}(\pi_{\mathrm{ref}}\|\pi_\theta),
$$

那是正向 KL 加一项与 $\pi_\theta$ 无关的熵，蚂蚁真题见 `ant-kl-vs-ce`。

## 和 DPO 的换元

DPO 从带该 **反向** KL 的 RLHF 目标出发。最优策略满足

$$
\pi_\theta(y\mid x)\propto\pi_{\mathrm{ref}}(y\mid x)\exp\big(r(x,y)/\beta\big),
$$

于是隐式奖励 $r=\beta\log(\pi_\theta/\pi_{\mathrm{ref}})+Z(x)$。偏好的 Bradley–Terry 模型代入后，$Z$ 消掉，得到 $\sigma$ 间隔里的 $\beta\log(\pi_\theta/\pi_{\mathrm{ref}})$。把 KL 方向写反，最优策略的闭式不再是「参考乘上 exp 奖励」，后面整段换元都对不上，见 `pt-dpo-derive`。现场若只能背 DPO loss、说不清这一步比例关系，方向问题其实没答完。

同一方向在探索场景里会变成缺点：稀有可验证正确路径若落在 $\pi_{\mathrm{ref}}$ 长尾，reverse KL 可能把它们当离群点掐掉，见 `pt-kl-direction-and-exploration`。对齐选反向是因为我们 **更怕跑出参考支撑**，不是因为反向在一切任务上都优于正向。

## 用两个峰把方向讲死

假设参考在「有用回答」和「有害但 SFT 里见过」两个峰上都有质量。对齐希望 $\pi_\theta$ 只留有用峰。反向 KL 允许不覆盖有害峰——那些样本不从 $\pi_\theta$ 里抽出来，就不进期望。正向 KL 会因为漏掉有害峰而被罚，策略只好继续生成它们。这就是「收窄 vs 覆盖」在对齐里的具体含义。白板上一张三格表就够：完美拟合、只锁有用峰、摊均匀。只锁有用峰时反向 KL 较小、正向 KL 很大；摊均匀则反过来。和 `fund-kl-directions` 那张表同一套直觉，只是把 $p$ 换成 $\pi_{\mathrm{ref}}$、$q$ 换成 $\pi_\theta$。面试官若追问「那探索怎么办」，承认反向 KL 与长尾成功路径冲突，转到 `pt-kl-direction-and-exploration`，不要临时把方向改口。

工程上还有一条：PPO / GRPO 的 rollout 本来就从 $\pi_\theta$ 采样，反向 KL 的蒙特卡洛估计是零额外采样；正向 KL 要另从 $\pi_{\mathrm{ref}}$ 采样，管道要加一条参考生成，和现有 on-policy 循环不合。所以「为什么用反向」同时有 **目标** 和 **实现** 两个理由，缺一个都答不完。实现上 token 级 KL 常用 $\log\pi_\theta-\log\pi_{\mathrm{ref}}$ 在响应 mask 上平均，和 DPO 的 $\beta\log(\pi_\theta/\pi_{\mathrm{ref}})$ 是同一块积木。Mask 必须只盖生成段：把 prompt 算进 KL，会把「读懂问题」当偏离来罚，格式和对齐都会被带偏。这和 `sys-rl-response-mask` 是同一类账本问题。

$\beta\log(\pi_\theta/\pi_{\mathrm{ref}})$ 既是 DPO 的隐式奖励，也是 PPO 里 KL 惩罚的被积函数。现场若被追问「写在奖励里还是单独减」，答：数学上等价到常数，实现上单独项更好监控；方向不能反。单独项还可以做 token 级诊断：哪些位置贡献了大部分 KL，往往就是 hacking 或格式崩溃开始的地方。把它和 response mask 一起看，能直接接到「prompt 段有没有被误罚」。KL 突然涨在某类安全拒答或某类工具名上，往往是数据混合比变了，而不是 $\beta$ 坏了。按意图分桶看 KL，比看一个全局均值更接近事故现场。拒答变多时 KL 升高，不一定是 drift，可能是参考本身很少拒答，要对着安全评测一起读。参考很少拒答时，对齐成功也会表现为 KL 上升，不能单凭 KL 大就回滚。拒答类 KL 涨、解题类 KL 稳，多半是安全数据比例变了，不该全局加大 $\beta$。

## 追问

- **$\beta$ 是在惩罚什么？** 当前策略相对参考的 token 级偏离，不是「和 SFT 的 CE」。$\beta$ 大则更贴参考、更稳、更难探索。监控应同时看 KL、熵和 gold 指标，而不是只把 $\beta$ 调到 KL 曲线好看。Gold 掉、KL 很小，说明贴着参考但参考本身不够好，该换数据而不是再加大 $\beta$。
- **能同时加正向项吗？** 可以做成 f-divergence 或 JS，用来保留一定覆盖；那是另一条目标，要重新推导，不能口头说「再加一个 CE」。见 `fund-js-vs-kl`。加了正向项就要从参考分布再采样，工程管道也会变。
- **Reference 用 SFT 还是 base？** 常用 SFT 策略当 $\pi_{\mathrm{ref}}$，让 KL 锚定在已经有指令格式的分布上。用 base 会把格式本身当偏离来罚，cold start 的收益会被 KL 吃掉。Reference 太强（接近已经对齐的模型）会把探索空间压没，太弱则护栏形同虚设。
- **和 PPO clip 重复吗？** 不重复。Clip 相对 $\pi_{\mathrm{old}}$ 限制单次更新；KL 相对 $\pi_{\mathrm{ref}}$ 限制长期漂移。两者常同时在。Clip 为 0 时 KL 仍可能在工作，见 `sys-rl-fw-clip-zero`。把其中一个关掉，要明确剩下那个还在约束哪一种偏离。
