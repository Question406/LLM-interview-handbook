---
id: ant-grpo-kl-vs-ppo
section: posttrain
order: 161
level: S
title: 蚂蚁：GRPO 的 KL 和 PPO 有何不同？K1/K2/K3 是什么？
quick: "PPO 常把 $D_{\\mathrm{KL}}(\\pi_\\theta\\|\\pi_{\\mathrm{ref}})$ 加进奖励或当惩罚；GRPO 论文用无偏估计直接估计 token 级 KL，也可以减弱 / 去掉。K1/K2/K3 是同一条反向 KL 的不同估计器，偏差和方差不一样，符号不能混着用。"
tags:
  - Ant Group
  - GRPO
  - KL
realInterview: true
status: published
format: markdown
updatedAt: 2026-08-21
sources:
  - title: 蚂蚁大模型一面（被问懵版）
    url: https://www.nowcoder.com/feed/main/detail/1a1a229b1d9f4a5bbfcb6ea6c9857339
    type: candidate-first-hand
  - title: DeepSeekMath
    url: https://arxiv.org/abs/2402.03300
    type: primary-paper
---

## 真题记录

- 公司：蚂蚁集团
- 团队 / 岗位：大模型
- 届别 / 流程：一面
- 面试时间：原帖未披露
- 来源类型与可信度：牛客候选人原帖，B
- 原始措辞：**“GRPO的kl散度和PPO的kl散度区别？K1 K2 K3估计区别？”**；**“PPO的kl散度可以改成交叉熵吗？”**

这块容易把「KL 加在奖励里还是损失上」和「估的是哪个方向」混成一件事。PPO 与 GRPO 约束的都是反向 $D_{\mathrm{KL}}(\pi_\theta\|\pi_{\mathrm{ref}})$，期望在当前策略的 采样轨迹（rollout） 上取，属于 mode-seeking，见 `fund-kl-directions`。差别在工程位置：PPO 常先把 KL 减进 奖励分数（reward），再送进 GAE；GRPO 把组相对优势当主信号，KL 变成可选的 token 级正则，甚至可以被动态采样和 clip 替代。K1/K2/K3 是同一条反向 KL 的不同估计器，不是三种散度，也不是三种算法。方向写反或把 交叉熵损失（CE） 当替换，就无法正确解释目标函数。

## 加在奖励里，还是加在损失上

PPO 典型写法是 $r_t\leftarrow r_t-\beta\,\widehat{\mathrm{KL}}_t$，或对近似 KL 做自适应 $\beta$。KL 进入 TD 残差 $\delta_t=r_t+\gamma V(s_{t+1})-V(s_t)$ 之后，会被 GAE 沿轨迹平滑，价值网络会「看见」惩罚，于是 价值评估模型（critic） 和 actor 一起被这根锚拉动。采样必须来自 $\pi_\theta$，方向才是反向；若改成对 监督微调（SFT） 数据做惩罚，采样跑到参考上，就变成正向 covering。

GRPO 主项是组相对优势 $\hat A_i=(r_i-\mathrm{mean}(r))/(\mathrm{std}+\varepsilon)$。KL 常直接加在损失上，不改 $r$，因此不进组标准化。DeepSeekMath 用 $k_3$ 一类无偏估计做 token 级惩罚。后续 DAPO 讨论过弱化甚至去掉显式 KL，改靠 clip-higher、动态丢掉零方差组和 token-level PG 管更新幅度。方向仍然是 $\pi_\theta$ 对冻结 $\pi_{\mathrm{ref}}$，不要写成 $D_{\mathrm{KL}}(\pi_{\mathrm{ref}}\|\pi_\theta)$。组大小 $n\gt 1$ 是优势可定义的前提，和 KL 是两根旋钮，见 `sys-rl-group-n`。

## K1 / K2 / K3：偏差与方差

令 $\rho=\pi_{\mathrm{ref}}/\pi_\theta$，样本来自当前策略 $\pi_\theta$。Schulman 口径：

$$
\begin{aligned}
k_1&=-\log\rho=\log(\pi_\theta/\pi_{\mathrm{ref}}),\\
k_2&=\tfrac12(\log\rho)^2,\\
k_3&=(\rho-1)-\log\rho.
\end{aligned}
$$

$k_1$ 就是 $\mathbb{E}_{\pi}[\log\pi-\log\pi_{\mathrm{ref}}]$，对反向 KL 无偏，但方差大。$k_3$ 多一项 $\rho-1$，在 $\pi$ 上取期望时 $\mathbb{E}[\pi_{\mathrm{ref}}/\pi-1]=0$，所以与 $k_1$ 同期望、通常更稳，GRPO 论文默认它。$k_2$ 是平方近似，有偏，不能和 $k_3$ 混着报数。面试写清「对谁采样、估哪个 KL」：同一组公式，若样本改成来自 ref，估的就变成另一侧。不能把 KL 换成交叉熵，CE 展开是正向 KL 加一项与 $\pi$ 无关的熵，采样也跑到 ref 上，见 `ant-kl-vs-ce`。CISPO 的 clip 管的是 IS 权重，不是这组估计器，见 `pt-cispo`。

## 追问

- **为什么不能换成 CE？** $H(\pi_{\mathrm{ref}},\pi)=H(\pi_{\mathrm{ref}})+D_{\mathrm{KL}}(\pi_{\mathrm{ref}}\|\pi)$，方向和采样都反了，会逼策略覆盖参考的每个峰，对齐要的收窄被抵消。
- **DAPO 为什么能弱 KL？** 动态丢掉零方差组、token 级 PG 和 clip-higher 在管步长与样本质量，见 `pt-dapo`。不是「GRPO 先天不需要锚」，实现仍可能加 $k_3$。
- **和 CISPO 的 clip 是一回事吗？** 不是。CISPO clip 的是 detach 后的 IS 权重，梯度仍走 $\log\pi$；K1/K3 估的是对 $\pi_{\mathrm{ref}}$ 的偏离。
- **组大小和 KL 谁先调？** 先保证 $n\gt 1$ 且非零优势组够，见 `sys-rl-group-n`；有效组已经够、KL 爆炸或熵塌，再动 $\beta$。
- **PPO 把 KL 放进奖励会不会改变优势符号？** 会。KL 大的 token 奖励被压低，GAE 会把「偏离 ref」传回前面的 token，这是有意的；GRPO 把 KL 放损失上则不进 $\hat A$。
