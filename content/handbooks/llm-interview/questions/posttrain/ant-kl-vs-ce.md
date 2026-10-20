---
id: ant-kl-vs-ce
section: posttrain
order: 226
level: A
title: 蚂蚁一面：PPO 的 KL 能改成交叉熵吗？
quick: "不能。对参考分布的 CE 等于熵加正向 $D_{\\mathrm{KL}}(\\pi_{\\mathrm{ref}}\\|\\pi)$，而 PPO 要的是在 $\\pi$ 上采样的反向 $D_{\\mathrm{KL}}(\\pi\\|\\pi_{\\mathrm{ref}})$，换了就改了目标和方向。"
tags:
  - Ant Group
  - KL
  - Cross Entropy
  - PPO
realInterview: true
status: published
format: markdown
updatedAt: 2026-08-21
sources:
  - title: 蚂蚁大模型一面（被问懵版）
    url: https://www.nowcoder.com/feed/main/detail/1a1a229b1d9f4a5bbfcb6ea6c9857339
    type: candidate-first-hand
---

## 真题记录

- 公司：蚂蚁集团
- 岗位：大模型；一面
- 来源类型与可信度：牛客候选人原帖，B
- 原始措辞：**“PPO的kl散度可以改成交叉熵吗？”**（同场还有 GRPO vs PPO KL、K1/K2/K3）

这块容易觉得「KL 和交叉熵只差一个与策略无关的熵，换成 CE 梯度一样」。差的不是常数，是谁采样、哪一侧对数会爆炸。白板定义见 `fund-kl-directions`。PPO 的 drift 要的是反向 $D_{\mathrm{KL}}(\pi\|\pi_{\mathrm{ref}})$，token 从当前策略采样；对参考分布计算交叉熵损失（CE） 得到的是正向 $D_{\mathrm{KL}}(\pi_{\mathrm{ref}}\|\pi)$，token 从参考来。护栏会从「不许跑出参考支撑」变成「必须盖住 SFT 的每个峰」，对齐要的收窄被抵消。同场常连问 K1/K2/K3，那些估计器估的仍是反向，不能拿 CE 冒充。

## 先把 CE 拆开

交叉熵按第一项分布取样，这步必须写：

$$
\begin{aligned}
H(p,q)&=-\mathbb{E}_{x\sim p}[\log q(x)]\\
&=H(p)+D_{\mathrm{KL}}(p\|q).
\end{aligned}
$$

令 $p=\pi_{\mathrm{ref}}$、$q=\pi$，得到正向 $D_{\mathrm{KL}}(\pi_{\mathrm{ref}}\|\pi)$，期望在参考策略上取。$H(\pi_{\mathrm{ref}})$ 对 $\pi$ 的梯度为零，看起来像「只差常数」，但散度的左右已经反了。正向是 mode-covering：只要 $\pi_{\mathrm{ref}}(x)\gt 0$，哪怕是示范里的有害峰或啰嗦峰，若 $\pi(x)\approx 0$，则 $\log(\pi_{\mathrm{ref}}/\pi)$ 爆炸。策略不敢忘掉 监督微调（SFT） 里出现过的说法，宁可把质量摊糊。这和聊天对齐想做的事相反。

## PPO 要的是反向，连 采样轨迹（rollout） 分布都反了

PPO / GRPO 的惩罚是

$$
D_{\mathrm{KL}}(\pi\|\pi_{\mathrm{ref}})=\mathbb{E}_{x\sim\pi}\big[\log\pi(x)-\log\pi_{\mathrm{ref}}(x)\big].
$$

期望在当前策略上取，mode-seeking：参考有、策略不去的峰根本不进期望，可以丢掉；策略跑到 $\pi_{\mathrm{ref}}\approx 0$ 处，对数会出现数值异常，所以不敢发明参考几乎不会说的续写。两边连采样分布都反了，不是减掉 $H(\pi_{\mathrm{ref}})$ 就能换。硬换的后果有两层：目标从 seeking 变成 covering，有害峰被逼着留下；梯度尺度被那项常数熵和错误方向一起搅乱，clip fraction 与熵曲线都会失真。

分类任务的 CE 是对标签分布，和「策略相对参考的正则」不是同一件事。蒸馏 / SFT 本来就在做正向 CE，那是另一道目标，用来铺格式和技能，见 `pt-sft-fwd-kl-vs-rlhf-rev-kl`。可以说的例外只有：你明确要再做一次 SFT 或教师采样蒸馏，那就承认「换目标」，不要说「等价替换 KL」。K1/K3 估的仍是反向，见 `ant-grpo-kl-vs-ppo`。组采样 强化学习（RL） 的优势定义和这道题正交，但方向写反之后，GRPO 的 KL 项一样会变成 covering，见 `sys-rl-group-n`。

## 追问

- **看公式左边还是看采样？** 看采样。口诀在 `fund-kl-directions`：token 从谁来，期望就在谁上。现场先写 $\mathbb{E}_{x\sim ?}$，问号填完再写 log 比。
- **SFT 不就是 CE 吗？** 是，那是正向 covering，用来铺格式，不是 PPO drift 的换皮。两阶段方向本来就该不同。
- **有没有可说的例外？** 有意做 on-policy distillation 或再 SFT 时，可以说「换目标」；不要说「数学上等价」。
- **GRPO 的 $k_3$ 是 CE 吗？** 不是。$k_3=(\pi_{\mathrm{ref}}/\pi)-1-\log(\pi_{\mathrm{ref}}/\pi)$ 在 $\pi$ 上取样，仍估反向 KL。
- **换了 CE 会观察到什么？** 策略更「像 SFT」、有害或套话峰压不下去，KL 仪表和奖励对不上，因为你已经不在估原来那条散度。
