---
id: ant-grpo-kl-vs-ppo
section: posttrain
order: 161
level: S
title: 蚂蚁：GRPO 的 KL 和 PPO 有何不同？K1/K2/K3 是什么？
quick: "两者约束的都是反向 $D_{\\mathrm{KL}}(\\pi_\\theta\\|\\pi_{\\mathrm{ref}})$，差在放的位置：PPO 常把 KL 减进奖励再进 GAE，GRPO 论文用无偏估计把它当 token 级惩罚直接加在损失上，也可以减弱或去掉。K1/K2/K3 是同一条反向 KL 的三个估计器，偏差和方差不同，不能混着报。"
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

PPO 和 GRPO 约束的是同一个反向 KL，$D_{\mathrm{KL}}(\pi_\theta\|\pi_{\mathrm{ref}})$，差别在 KL 放在哪：PPO 常把它减进奖励再送进 GAE，GRPO 把组相对优势当主信号，KL 变成可选的 token 级正则，直接加在损失上，甚至可以被动态采样和 clip 替代。K1/K2/K3 是估这同一条反向 KL 的三种估计器，不是三种散度，也不是三种算法。

这题容易把「KL 加在奖励里还是损失上」和「估的是哪个方向」混成一件事，所以先把方向钉住：期望在当前策略的采样轨迹（rollout）上取，属于 mode-seeking，见 `fund-kl-directions`。方向写反，或者拿交叉熵损失（CE）来替换，目标函数就解释不通了。

先说 PPO。典型写法是 $r_t\leftarrow r_t-\beta\,\widehat{\mathrm{KL}}_t$，或者对近似 KL 做自适应 $\beta$。KL 进入 TD 残差 $\delta_t=r_t+\gamma V(s_{t+1})-V(s_t)$ 之后，会被 GAE 沿轨迹平滑，价值网络也「看得见」这个惩罚，于是价值评估模型（critic）和 actor 一起被这根锚拉着。采样必须来自 $\pi_\theta$，方向才是反向；要是改成对监督微调（SFT）数据做惩罚，采样跑到参考上，就变成了正向 covering。

GRPO 的主信号是组相对优势 $\hat A_i=(r_i-\mathrm{mean}(r))/(\mathrm{std}+\varepsilon)$。KL 常直接加在损失上，不改 $r$，所以不参与组标准化。DeepSeekMath 用 $k_3$ 这类无偏估计做 token 级惩罚；后来 DAPO 讨论过弱化甚至去掉显式 KL，改靠 clip-higher、动态丢掉零方差组和 token-level PG 来管更新幅度。不管放哪，方向都是 $\pi_\theta$ 对冻结的 $\pi_{\mathrm{ref}}$，别写成 $D_{\mathrm{KL}}(\pi_{\mathrm{ref}}\|\pi_\theta)$。组大小 $n\gt 1$ 是优势能定义的前提，它和 KL 是两个独立的旋钮，见 `sys-rl-group-n`。

再说 K1/K2/K3。令 $\rho=\pi_{\mathrm{ref}}/\pi_\theta$，样本来自当前策略 $\pi_\theta$，按 Schulman 的口径：

$$
\begin{aligned}
k_1&=-\log\rho=\log(\pi_\theta/\pi_{\mathrm{ref}}),\\
k_2&=\tfrac12(\log\rho)^2,\\
k_3&=(\rho-1)-\log\rho.
\end{aligned}
$$

$k_1$ 就是 $\mathbb{E}_{\pi}[\log\pi-\log\pi_{\mathrm{ref}}]$，对反向 KL 无偏，但方差大。$k_3$ 多了一项 $\rho-1$，在 $\pi$ 上取期望时 $\mathbb{E}[\pi_{\mathrm{ref}}/\pi-1]=0$，所以和 $k_1$ 期望相同，通常更稳，GRPO 论文默认用它。$k_2$ 是平方近似，有偏，不能和 $k_3$ 混着报数。比如一个 run 前半段日志记 $k_2$、后半段换成 $k_3$，两段 KL 曲线就没法放在一起比。面试时写清楚「对谁采样、估哪个 KL」：同一组公式，样本要是改成来自 ref，估的就是另一侧了。

原帖还问了 PPO 的 KL 能不能改成交叉熵，答案是不能。CE 展开是正向 KL 加一项和 $\pi$ 无关的熵，采样也跑到 ref 上去了，见 `ant-kl-vs-ce`。另外 CISPO 的 clip 管的是 IS 权重，和这组估计器无关，见 `pt-cispo`。

## 追问

**为什么不能换成 CE？**
$H(\pi_{\mathrm{ref}},\pi)=H(\pi_{\mathrm{ref}})+D_{\mathrm{KL}}(\pi_{\mathrm{ref}}\|\pi)$，方向和采样都反了。策略会被逼着覆盖参考的每个峰，对齐想要的收窄就被抵消了。

**DAPO 为什么能弱化 KL？**
动态丢掉零方差组、token 级 PG 和 clip-higher 在管步长和样本质量，见 `pt-dapo`。这不代表 GRPO 天生不需要锚，实现里仍可能加 $k_3$。

**这和 CISPO 的 clip 是一回事吗？**
不是。CISPO clip 的是 detach 之后的 IS 权重，梯度仍走 $\log\pi$；K1/K3 估的是相对 $\pi_{\mathrm{ref}}$ 的偏离。

**组大小和 KL 先调哪个？**
先保证 $n\gt 1$、非零优势组足够，见 `sys-rl-group-n`。有效组够了，KL 还在爆或者熵塌了，再动 $\beta$。

**PPO 把 KL 放进奖励，会不会改变优势的符号？**
会。KL 大的 token 奖励被压低，GAE 会把「偏离 ref」往前面的 token 传，这是有意设计的。GRPO 把 KL 放在损失上，就不进 $\hat A$。
