---
id: ant-kl-vs-ce
section: posttrain
order: 226
level: A
title: 蚂蚁一面：PPO 的 KL 能改成 cross entropy 吗？
quick: >-
  不能。对参考分布算 CE 等于熵加正向 $D_{\mathrm{KL}}(\pi_{\mathrm{ref}}\|\pi)$，token 从参考里采；PPO
  要的是在 $\pi$ upsampling 的反向
  $D_{\mathrm{KL}}(\pi\|\pi_{\mathrm{ref}})$。换了就同时改了目标和方向，护栏会从「别跑出参考支撑」变成「必须盖住参考的每个峰」。
tags:
  - Ant Group
  - KL
  - Cross Entropy
  - PPO
realInterview: true
status: published
format: markdown
updatedAt: 2026-08-21T00:00:00.000Z
sources:
  - title: 蚂蚁大模型一面（被问懵版）
    url: 'https://www.nowcoder.com/feed/main/detail/1a1a229b1d9f4a5bbfcb6ea6c9857339'
    type: candidate-first-hand
---

## 真题记录

- 公司：蚂蚁集团
- 岗位：大模型；一面
- 来源类型与可信度：牛客候选人原帖，B
- 原始措辞：**“PPO 的 kl 散度可以改成 cross entropy 吗？”**（同场还有 GRPO vs PPO KL、K1/K2/K3）

不能换。对参考分布算 cross entropy loss（CE），得到的是正向 $D_{\mathrm{KL}}(\pi_{\mathrm{ref}}\|\pi)$，token 从参考里来；PPO 管漂移要的是反向 $D_{\mathrm{KL}}(\pi\|\pi_{\mathrm{ref}})$，token 从当前策略 sampling。两者差的不只是一个常数，谁来 sampling、哪一侧的对数会爆炸都变了。

很多人的直觉是「KL 和 cross entropy 只差一个和策略无关的熵，换成 CE 梯度一样」。所以我会先把 CE 拆开，这一步一定要写，cross entropy 按第一项分布取样：

$$
\begin{aligned}
H(p,q)&=-\mathbb{E}_{x\sim p}[\log q(x)]\\
&=H(p)+D_{\mathrm{KL}}(p\|q).
\end{aligned}
$$

令 $p=\pi_{\mathrm{ref}}$、$q=\pi$，得到正向 $D_{\mathrm{KL}}(\pi_{\mathrm{ref}}\|\pi)$，期望在 reference policy 上取。$H(\pi_{\mathrm{ref}})$ 对 $\pi$ 的梯度是零，看起来确实「只差常数」，可散度的左右已经反了。正向是 mode-covering：只要 $\pi_{\mathrm{ref}}(x)\gt 0$，哪怕那是示范里的有害峰或啰嗦峰，一旦 $\pi(x)\approx 0$，$\log(\pi_{\mathrm{ref}}/\pi)$ 就会爆炸。比如 SFT 数据里有一类车轱辘话式的客套开头，forward KL 下策略不敢忘掉这种说法，宁可把质量摊糊，这和聊天对齐想做的事正好相反。

PPO / GRPO 的惩罚是

$$
D_{\mathrm{KL}}(\pi\|\pi_{\mathrm{ref}})=\mathbb{E}_{x\sim\pi}\big[\log\pi(x)-\log\pi_{\mathrm{ref}}(x)\big].
$$

期望在当前策略上取，是 mode-seeking：参考里有、策略不去的峰根本不进期望，可以丢掉；策略跑到 $\pi_{\mathrm{ref}}\approx 0$ 的地方，对数会出现数值异常，所以它不敢发明参考几乎不会说的续写。两边连 sampling 轨迹（rollout）的分布都反了，减掉 $H(\pi_{\mathrm{ref}})$ 也换不回来。硬换的后果有两层：目标从 seeking 变成 covering，有害峰被逼着留下；梯度尺度被那项常数熵和错误方向一起搅乱，clip fraction 和熵曲线都会失真。白板定义见 `fund-kl-directions`。

还有一个容易混的地方。分类任务的 CE 是对标签分布算的，和「策略相对参考的正则」是两回事。distillation 和 SFT 本来就在做正向 CE，那是另一个目标，用来铺格式和技能，见 `pt-sft-fwd-kl-vs-rlhf-rev-kl`。能说得通的例外只有一种：你明确要再做一次 SFT 或教师 sampling distillation，那就承认这是换目标，别说成「等价替换 KL」。同场常连着问 K1/K2/K3，那些估计器估的仍是 reverse KL，拿 CE 冒充不了，见 `ant-grpo-kl-vs-ppo`。组 sampling RL 的优势定义和这题无关，但方向写反之后，GRPO 的 KL 项一样会变成 covering，见 `sys-rl-group-n`。

## 追问

**判断方向，看公式左边还是看 sampling？**
看 sampling。口诀在 `fund-kl-directions`：token 从谁那里来，期望就在谁上。现场先写 $\mathbb{E}_{x\sim ?}$，把问号填上，再写 log 比。

**SFT 不就是 CE 吗？**
是，那是正向 covering，用来铺格式，和 PPO 里管漂移的 KL 不是一个东西。两个阶段的方向本来就该不同。

**有没有能说得通的例外？**
有。有意做 on-policy distillation 或者再做一轮 SFT 时，可以说「换目标」，别说「数学上等价」。

**GRPO 的 $k_3$ 是 CE 吗？**
不是。$k_3=(\pi_{\mathrm{ref}}/\pi)-1-\log(\pi_{\mathrm{ref}}/\pi)$ 在 $\pi$ 上取样，估的仍是 reverse KL。

**真换成 CE 了，会观察到什么？**
策略更像 SFT，有害或套话的峰压不下去，KL 仪表和奖励对不上，因为估的已经不是原来那条散度了。
