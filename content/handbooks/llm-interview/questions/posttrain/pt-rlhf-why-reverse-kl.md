---
id: pt-rlhf-why-reverse-kl
section: posttrain
order: 221
level: S
title: 对齐为什么用 $D_{\mathrm{KL}}(\pi_\theta\|\pi_{\mathrm{ref}})$，而不是反过来？
quick: "因为要罚的是策略跑到参考模型几乎不会说的地方，这正是反向 KL，期望在 $\\pi_\\theta$ 下取，和 rollout 的采样分布一致。正向 $D_{\\mathrm{KL}}(\\pi_{\\mathrm{ref}}\\|\\pi_\\theta)$ 会逼策略继续覆盖参考的所有峰，包括我们想丢掉的毒性模式，也对不上 DPO 的推导。"
tags:
  - KL
  - RLHF
  - DPO
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-21
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

因为对齐最怕的是策略跑到参考模型几乎不会说的地方，反向 KL 罚的正是这个，同时它允许策略丢掉参考里不想要的峰。另外它的期望在 $\pi_\theta$ 上取，和 PPO / GRPO 用当前策略做 rollout 正好对上。目标和实现两个理由都要讲，光答「因为 DPO 论文这么写」不够。白板定义见 `fund-kl-directions`。

先看公式：

$$
D_{\mathrm{KL}}(\pi_\theta\|\pi_{\mathrm{ref}})=\mathbb{E}_{y\sim\pi_\theta}\big[\log\pi_\theta(y)-\log\pi_{\mathrm{ref}}(y)\big].
$$

$\pi_\theta$ 在 $\pi_{\mathrm{ref}}\approx 0$ 的地方分配概率时，$\log(\pi_\theta/\pi_{\mathrm{ref}})$ 会爆炸，参考几乎不会说的续写代价极高，压住的正是胡话和钻奖励漏洞的行为。Reward hacking 经常表现为跑到参考低概率、proxy 高分的区域，反向 KL 正好打在这条路上；正向 KL 打的是「漏掉参考的峰」，对 hacking 几乎没有直接惩罚。另一面，$\pi_{\mathrm{ref}}$ 有而 $\pi_\theta$ 不去的峰几乎不进期望，所以反向 KL **允许遗忘**，SFT 数据里残留的有害或啰嗦模式可以丢掉。这是 mode-seeking，是我们想要的性质。只答「防 hacking」不提遗忘，只答对了一半。

用两个峰讲最清楚。假设参考在「有用回答」和「有害但 SFT 里见过」两种模式上都有概率，对齐希望 $\pi_\theta$ 只留有用峰。反向 KL 下，有害峰的样本不会从 $\pi_\theta$ 里抽出来，也就不进期望，丢了没关系。换成 $D_{\mathrm{KL}}(\pi_{\mathrm{ref}}\|\pi_\theta)$，期望改到 $\pi_{\mathrm{ref}}$ 上，只要参考某处概率为正，策略在那里接近 0 就会被重罚，于是 $\pi_\theta$ **必须继续覆盖参考的每一个高概率模式**，只好接着生成有害的那部分。对齐想做的是收窄，提高有用、无害的峰，丢掉毒性、拍马、拒答失败，正向 KL 会惩罚这些模式被丢掉。聊天模型里尤其明显，SFT 残留的过度承诺、泄露风格，会被正向正则逼着继续生成，只为了「覆盖参考」。白板上画一张三格表就够：完美拟合、只锁有用峰、摊均匀。只锁有用峰时反向 KL 较小、正向 KL 很大；摊均匀则反过来。这和 `fund-kl-directions` 那张表是同一套直觉，只是把 $p$ 换成 $\pi_{\mathrm{ref}}$、$q$ 换成 $\pi_\theta$。

再看目标函数。InstructGPT / PPO-RLHF 的目标可以写成最大化

$$
\mathbb{E}_{y\sim\pi_\theta}[r(x,y)]-\beta\,D_{\mathrm{KL}}(\pi_\theta\|\pi_{\mathrm{ref}}),
$$

奖励在当前策略上取，KL 也得在当前策略上取，两项的期望才在同一个分布上。PPO / GRPO 的 rollout 本来就从 $\pi_\theta$ 采样，反向 KL 的蒙特卡洛估计不需要额外采样；正向 KL 得另从 $\pi_{\mathrm{ref}}$ 采样，管道要多一条参考生成，和现有的 on-policy 循环不合。

这题常和蚂蚁那道「KL 能不能改成 CE」连着问。把交叉熵损失（CE）展开：

$$
H(\pi_{\mathrm{ref}},\pi_\theta)=H(\pi_{\mathrm{ref}})+D_{\mathrm{KL}}(\pi_{\mathrm{ref}}\|\pi_\theta),
$$

它是正向 KL 加一项与 $\pi_\theta$ 无关的熵，期望也在 $\pi_{\mathrm{ref}}$ 上，和 PPO 用当前策略 rollout 的方式不一致，真题见 `ant-kl-vs-ce`。所以先画清「谁在采样」，再谈公式左右哪边，比背 $D_{\mathrm{KL}}(\pi\|\pi_{\mathrm{ref}})$ 的写法更不容易写反。

DPO 也是从带**反向** KL 的 RLHF 目标推出来的。最优策略满足

$$
\pi_\theta(y\mid x)\propto\pi_{\mathrm{ref}}(y\mid x)\exp\big(r(x,y)/\beta\big),
$$

于是隐式奖励 $r=\beta\log(\pi_\theta/\pi_{\mathrm{ref}})+Z(x)$，代入偏好的 Bradley-Terry 模型后 $Z$ 消掉，就得到 $\sigma$ 间隔里的 $\beta\log(\pi_\theta/\pi_{\mathrm{ref}})$。KL 方向写反，最优策略的闭式就不再是「参考乘上 exp 奖励」，后面整段换元都对不上，见 `pt-dpo-derive`。面试时只能背 DPO 损失、说不清这一步比例关系，方向问题其实没答完。

实现上，token 级 KL 常用 $\log\pi_\theta-\log\pi_{\mathrm{ref}}$ 在响应 mask 上平均，和 DPO 的 $\beta\log(\pi_\theta/\pi_{\mathrm{ref}})$ 是同一种对数概率比。写进奖励里还是单独减，数学上等价到常数，单独一项更好监控。mask 只能盖生成段，把输入提示算进 KL，会把「读懂问题」当成偏离来罚，格式和对齐都会被带偏，这和 `sys-rl-response-mask` 是同一类账本问题。单独一项还能做 token 级诊断：哪些位置贡献了大部分 KL，往往就是 hacking 或格式崩溃开始的地方。按意图分组看 KL，也比看全局均值更接近事故现场。KL 突然涨在某类安全拒答或某类工具名上，多半是数据混合比变了，和 $\beta$ 关系不大。拒答变多时 KL 升高也不一定是 drift，参考本身很少拒答时，对齐成功也会表现为 KL 上升；拒答类 KL 涨、解题类 KL 稳，多半是安全数据比例变了，不该全局加大 $\beta$。

最后承认它的代价。同一个方向放到探索里会变成缺点：稀有的可验证正确路径如果落在 $\pi_{\mathrm{ref}}$ 的长尾，反向 KL 可能把它们当离群点掐掉，见 `pt-kl-direction-and-exploration`。对齐选反向，是因为我们**更怕跑出参考的支撑**，它并没有在所有任务上都优于正向。面试官追问「那探索怎么办」时，承认这个冲突，转到那张卡，别临时改口换方向。

## 追问

**$\beta$ 在罚什么？**
罚当前策略相对参考的 token 级偏离，和「跟 SFT 的 CE」不是一回事。$\beta$ 大就更贴参考、更稳、更难探索。监控要同时看 KL、熵和 gold 指标，别只把 $\beta$ 调到 KL 曲线好看。gold 掉、KL 很小，说明贴着参考但参考本身不够好，该换数据，再加大 $\beta$ 没用。

**能同时加一个正向项吗？**
可以做成 f-divergence 或 JS，用来保留一定覆盖；但那是另一个目标，要重新推导，口头说「再加一个 CE」不行，见 `fund-js-vs-kl`。加了正向项就要从参考分布再采样，工程管道也得变。

**reference 用 SFT 还是 base？**
通常用 SFT 策略当 $\pi_{\mathrm{ref}}$，让 KL 锚在已经有指令格式的分布上。用 base 会把格式本身当偏离来罚，cold start 的收益被 KL 吃掉。reference 太强（接近已经对齐的模型）会把探索空间压没，太弱则护栏形同虚设。

**和 PPO clip 重复吗？**
不重复。clip 相对 $\pi_{\mathrm{old}}$ 限制单次更新，KL 相对 $\pi_{\mathrm{ref}}$ 限制长期漂移，两者常常同时在。拿掉 KL 只留 clip，长期仍可能离开参考；只留 KL 不 clip，单次更新仍可能过猛，见 `pt-ppo-clip`。clip 为 0 时 KL 仍可能在工作，见 `sys-rl-fw-clip-zero`。关掉其中一个，要说清剩下那个还在约束哪一种偏离。
