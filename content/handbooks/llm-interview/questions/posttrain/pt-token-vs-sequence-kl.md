---
id: pt-token-vs-sequence-kl
section: posttrain
order: 227
level: A
title: KL 按 token 平均还是按整段序列加总？两种写法差在哪？
quick: >-
  autoregressive 下，序列 KL $D_{\mathrm{KL}}(\pi\|\pi_{\mathrm{ref}})$ 就等于逐步 KL
  之和，两种写法差的是 reduction：直接加总，长回答挨罚更多；按长度平均，长短回答的惩罚差被抹平。答题时说清 reduction，并和 GSPO
  的序列级 ratio 分开，一个是正则，一个是重要性权重。
tags:
  - KL
  - PPO
  - GSPO
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-21T00:00:00.000Z
sources:
  - title: DeepSeekMath
    url: 'https://arxiv.org/abs/2402.03300'
    type: primary
  - title: 阿里国际大模型算法一面
    url: 'https://www.nowcoder.com/feed/main/detail/27a27fc44b8a4613ae790ba27add8850'
    type: candidate-first-hand
---

autoregressive 模型里，序列 KL 就是逐步 KL 之和，两种写法是同一个联合 KL 的不同归约（reduction），差别落在长度偏置上：求和会罚长文，平均会放过长空话。所以问「哪种更正确」不如问「你更怕回答变长，还是怕短样本被长样本主导」。阿里面经里会追问这个，我还会顺手把它和 GSPO 的序列级 importance ratio 分开，那是另一件事。

先写展开式。autoregressive 下 $\pi(y\mid x)=\prod_t\pi(y_t\mid x,y_{\lt t})$，轨迹联合散度可以展开成

$$
D_{\mathrm{KL}}\big(\pi(\cdot\mid x)\,\|\,\pi_{\mathrm{ref}}(\cdot\mid x)\big)=\mathbb{E}_{y\sim\pi}\sum_t D_{\mathrm{KL}}\big(\pi(\cdot\mid x,y_{\lt t})\,\|\,\pi_{\mathrm{ref}}(\cdot\mid x,y_{\lt t})\big).
$$

理论上「序列 KL」就是逐步 KL 的和。实现上的差异全在 reduction：对 $t$ 求和、对 $t$ 平均，还是再按 batch / 有效 token 平均。定义上求和才对得上联合 $D_{\mathrm{KL}}$；工程上平均更稳，也更好和 lr、$\beta$ 一起调。现场先把展开式写出来再谈 reduction，左右就不会写反。mask 只能盖生成段，把 prompt 也算进 KL，会把「读懂问题」当成偏离来罚，token-mean 还会被长 prompt 进一步稀释。

## 三种 reduction 各罚什么

举个例子，一条短回答和一条长得多的回答，每步偏离参考的程度差不多。求和时长的那条 KL 大得多，模型有动机缩短，空话变贵，长度 hacking 也变贵；代价是短而偏的回答惩罚相对小，「短但已经离开参考」的失败可能漏掉。对 $t$ 平均时，两条惩罚差不多，长度惩罚被抹平，逐步偏离被长度除掉，长空话变得便宜，短而偏的回答更显眼。再按 batch / 有效 token 平均，和 SFT 按 token 平均的 cross entropy loss 一致，方便和 lr、$\beta$ 一起调，但会掩盖「少数超长样本贡献了大部分漂移」。

怎么选看你怕什么：怕变长刷分，就偏求和，或者另加长度惩罚；怕短样本被长样本主导，就偏平均。监控上一定要写明 reduction，mean token KL 和 sum KL 别画在同一个坐标轴上假装可比。自适应 $\beta$ 的 controller 如果钉的是 mean，它的目标带和求和就不是同一个工作点。长度要单独画，奖励和长度一起涨，先当 length hacking 处理，再决定改 reduction 还是改奖励。

## 和 GSPO 的序列级 ratio 分开

GSPO 把 importance ratio 和 clip 提到了序列级，解决的是长序列 token ratio 连乘爆炸、MoE 路由下逐步 $\rho_t$ 不稳的问题，它没有改 drift KL 的定义。KL 正则比的是 $\pi$ 和 $\pi_{\mathrm{ref}}$，clip 比的是 $\pi$ 和 $\pi_{\mathrm{old}}$，两边都可以做成 sequence 级，但对象不同。所以面试官连问「token 还是序列」时，先确认问的是 KL 还是 ratio，对象答错，后面的公式就对不上题。序列级 KL 求和和序列级 $\rho$ 可以同时存在，只是别说成同一个改动。

## 追问

**哪一种更正确？**
定义上求和才是联合 KL，工程上平均更稳。说清 reduction 就行，不用站队：怕变长就求和或加长度项，怕短样本被主导就平均。

**平均会不会让长文 hacking？**
会。逐步偏离被长度除掉，空话就便宜了。要配长度惩罚或改用求和 KL，并单独画长度曲线。

**这和 token 级 PPO ratio 是一回事吗？**
不是。ratio 是 importance sampling，KL 是正则，GSPO 改的是前者；两者的对象分别是 $\pi_{\mathrm{old}}$ 和 $\pi_{\mathrm{ref}}$。

**监控该看哪个？**
sum 和 mean 都看，再按长度分组统计，只看一个会被 reduction 骗。自适应 $\beta$ 必须和监控用同一种 reduction，否则控制的目标范围对不上。
