---
id: fund-biasvariance
section: fundamentals
order: 10
level: A
title: Bias–Variance Tradeoff 在 RL 中有哪些具体例子？
quick: >-
  RL 里很多稳定训练的手段都是主动接受一点 bias 换更低 variance。MC return 不依赖 value function，bootstrap
  偏差低但方差高；TD / GAE 用 value 估计降方差，同时引入偏差。重要性权重裁剪、奖励 normalization 和组内
  normalization 也一样，每一项都要说得出牺牲了目标的哪一块。
tags:
  - RL
  - Statistics
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-21T00:00:00.000Z
sources:
  - title: High-Dimensional Continuous Control Using Generalized Advantage Estimation
    url: 'https://arxiv.org/abs/1506.02438'
    type: primary
  - title: Proximal Policy Optimization Algorithms
    url: 'https://arxiv.org/abs/1707.06347'
    type: secondary
---
RL 里很多稳定训练的方法，都是主动接受一点 bias 去换更低的 variance。unbiased estimate 如果方差高到梯度没法用，工程上并不更好；反过来，normalization 和 clipping 做过头，训练是稳了，却可能悄悄改了你在优化的长度或难度加权。所以这题别停在监督学习那条 U 形曲线上，要落到回报、优势和重要性权重的具体计算：MC 无偏但方差大，TD / GAE 用 value 降方差、引入偏差；clip、奖励 standardization、组内减均值，都在用目标的扭曲换可训练的梯度。

举个例子，长 chain of thought 上一条幸运的高分轨迹，用 MC 回报算优势，整条链上每个 token 都拿到一大份功劳，一个 batch 里就被它主导了；换成 GAE，用 $V$ 截断，这条轨迹的影响被压下来，但如果 $V$ 总是低估长链的中间步，这些步的优势就被系统性抬高。

## Return 与优势：MC 无偏，TD / GAE 有偏

Monte Carlo return $G_t$ 不做 bootstrap，对给定策略在无限 sampling 下无偏，但轨迹噪声、长 horizon 和稀疏奖励都会让方差极大。TD / bootstrap 用 $V(s_{t+k})$ 截断：

$$
\hat{A}_t^{(\gamma,\lambda)}=\sum_{k=0}^{\infty}(\gamma\lambda)^k\delta_{t+k},\quad \delta_t=r_t+\gamma V(s_{t+1})-V(s_t).
$$

$\lambda=1$ 靠近 MC（低 bias、高 var），$\lambda\to 0$ 靠近一步 TD（高 bias、低 var），GAE 就是把这条轴做成可调旋钮。Value 函数一旦错了，偏差会系统性地抬高或压低某类状态的优势。方差是下来了，可优化的已经不是原来的 policy gradient。

LLM RL 里的组内 normalization 也一样。GRPO 对同一 prompt 下的一组分数减均值，这个 baseline 降低了方差；但一组全对或全错时优势变成 0、梯度消失，等于把「这道题的绝对难度」从目标里抹掉了，用改目标换来了组内可比。

「要不要 critic」也落在这条轴上。拟合得差的 $V$ 会让 GAE 的 $\delta_t$ 系统性地歪；不用 $V$ 的 MC，在长 CoT 上一条轨迹的回报方差可以大到 PPO 学不动。现场最好能指出：降低 $\lambda$、加价值评估模型（critic）、组内减均值、clip 权重，都是往「更稳、更偏」那一端走；加大组大小、用更准的 $V$、少 clip，是在同一条轴上往回挪。

## 重要性权重、clip、normalization：稳住梯度，代价是目标变了

Off-policy，或者 PPO 复用 sampling 轨迹（rollout）时，重要性比 $\rho_t=\pi_\theta/\pi_{\mathrm{old}}$ 可以无偏地校正分布，但 $\rho$ 的长尾会让方差爆炸。Clip / truncate 把权重限制在 $[1-\varepsilon,1+\varepsilon]$ 这类区间里，梯度能用了，被 clip 掉的那些 token 上目标却变平了，更新也就偏离了原来的 on-policy 目标。PPO 是明确接受这一点，来换 trust-region 式的稳定。Clip fraction 很高时，大量 token 已经不提供真实的 policy gradient，有效目标偏得更多。

Reward normalization、advantage standardization、长度 normalization 也是这个道理。按 batch standardization 奖励，能稳住 LR 和 KL 的相对尺度，但 batch 组成一变，同一条轨迹的分数含义就变了：一条高分回答放进「全是高分的 batch」里优势变小，目标变成了相对这个 batch 的排序，跨实验的 reward 曲线绝对值也没法比。按长度除奖励，会削弱「长而对」相对「短而对」的权重，根据符号不同，可能鼓励早停，也可能鼓励注水。KL 系数过大，模型几乎不更新，方差极低，偏差全偏到 $\pi_{\mathrm{ref}}$ 上。

每一项都要能回答：「我牺牲了哪一部分无偏性，换来了哪一种可训练性？」只说「为了稳定」不够，说不出牺牲了什么，就只是在堆 trick。

## 怎么选

选择看奖励噪声和 horizon。规则可验证、轨迹短（比如数学填空）的任务，方差本来就小，可以更靠近 MC、用大 $\lambda$、少 clip。reward model（RM）噪声大、回复很长的任务，就必须 bootstrap、clip、组内中心化，再用 held-out 金标检查目标有没有偏到长度或套话上。

监控要两边对着看：梯度范数和 KL 说明还能不能训（方差这一侧）；金标、长度、多样性是不是跟着 proxy 一起动（偏差这一侧）。Proxy 很稳、金标不动，就说明 bias 已经占了主导。

没有哪个 $\lambda$ 或 $\varepsilon$ 普遍最优。我会画一条轴：左端无偏但训不动，右端极稳但优化的是另一个问题，然后说清楚这套配方落在哪、为什么。LLM 的方差还有一个来源，是同一 prompt 下的多种合理写法，组太小会把随机性当成优势。加大组是在降方差，几乎不改目标，往往比把 $\lambda$ 拧到 0 更干净。

## 追问

**无偏是不是总更好？**
不是。方差过大时有效更新接近噪声，工程上能用的 biased estimate 常常赢。先问能不能训，再问偏了什么，训不动的无偏梯度没有决策价值。

**GAE 的 $\lambda$ 在干什么？**
在 TD 和 MC 之间插值：降 $\lambda$ 降方差、加 bootstrap 偏差，见 `baidu-gae-lambda`。$\lambda=1$ 只是更接近 MC，谈不上更「正确」，长 chain of thought 上通常也不会把 $\lambda$ 钉在 1。

**Group normalization 的 bias 是什么？**
它消掉了不同 prompt 之间的绝对回报差，全对组拿零优势。稳住的是组内排序，丢掉的是「这题还该不该再加强」。

**Clip 算 variance reduction 吗？**
它主要是限制过大的权重，近似 trust-region。它降低的是危险更新，同时也改了目标，不能写成无偏的方差公式。Clip fraction 高，说明有效目标已经偏得很厉害。
