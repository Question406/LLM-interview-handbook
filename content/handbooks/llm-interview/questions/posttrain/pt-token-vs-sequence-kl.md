---
id: pt-token-vs-sequence-kl
section: posttrain
order: 227
level: A
title: KL 按 token 平均还是按整段序列加总？两种写法差在哪？
quick: >-
  序列 KL 是轨迹联合分布上的 $D_{\mathrm{KL}}(\pi\|\pi_{\mathrm{ref}})$，自回归下等于逐步 KL
  的和。按长度平均会减小长短回答之间的惩罚差异；直接加总会让长回答更挨罚。我会说清 reduction，并和 GSPO
  的序列级 ratio 分开：一个是正则，一个是重要性权重。
tags:
  - KL
  - PPO
  - GSPO
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-21
sources:
  - title: DeepSeekMath
    url: https://arxiv.org/abs/2402.03300
    type: primary
  - title: 阿里国际大模型算法一面
    url: https://www.nowcoder.com/feed/main/detail/27a27fc44b8a4613ae790ba27add8850
    type: candidate-first-hand
---

阿里面经会追「token 级还是序列级 KL」。监控里的「平均 token KL」和轨迹联合 KL 不能拿来比数；这件事也别和 GSPO 的序列级 importance ratio 混成一句「都做成 sequence 级」。一个是对 $\pi_{\mathrm{ref}}$ 的漂移正则，一个是对 $\pi_{\mathrm{old}}$ 的重要性权重。reduction 一改，长度偏置就改：求和罚长文，平均放过长空话。自回归下两者在数学上不是两种散度，而是同一种联合 KL 的不同归约；问「哪种更正确」不如说「你怕变长还是怕短样本被主导」。监控必须写明 reduction，否则两条曲线不能比，自适应 $\beta$ 也会钉错工作点。

## 自回归下，序列 KL 等于逐步 KL 之和

自回归 $\pi(y\mid x)=\prod_t\pi(y_t\mid x,y_{\lt t})$，轨迹联合散度可展开为

$$
D_{\mathrm{KL}}\big(\pi(\cdot\mid x)\,\|\,\pi_{\mathrm{ref}}(\cdot\mid x)\big)=\mathbb{E}_{y\sim\pi}\sum_t D_{\mathrm{KL}}\big(\pi(\cdot\mid x,y_{\lt t})\,\|\,\pi_{\mathrm{ref}}(\cdot\mid x,y_{\lt t})\big).
$$

理论上「序列 KL」就是逐步 KL 的和，不是另一种散度。实现差异来自 **reduction**：对 $t$ 求和、对 $t$ 平均、再按 batch / 有效 token 平均。mask 必须只盖生成段：把输入提示算进 KL，会把「读懂问题」当偏离来罚，token-mean 还会被长 prompt 进一步稀释。定义上求和才对得上联合 $D_{\mathrm{KL}}$；工程上平均更稳、更好和 lr、$\beta$ 一起调。现场先写展开式，再谈 reduction，左右不会写反。

## 三种 reduction 的长度含义

**求和**：长轨迹 KL 更大，模型有缩短动机，空话更贵，长度 hacking 更贵。短而偏的回答惩罚相对小，可能漏掉「短但已经离开参考」的失败。**对 $t$ 平均**：长度惩罚被抹平，长空话可能漏网，短而偏的回答反而更显眼。逐步偏离被长度除掉，空话变得便宜。**再按 batch / 有效 token 平均**：与 SFT 按 token 平均的交叉熵损失一致，便于和 lr、$\beta$ 一起调，但会掩盖「少数超长样本贡献了大部分漂移」。

选哪一种取决于你怕什么：怕变长刷分，偏求和或另加长度惩罚；怕短样本被长样本主导，偏平均。汇报里不要把 mean token KL 和 sum KL 画在同一坐标轴上假装可比。Controller 若钉的是 mean，目标带和求和不是同一工作点。长度要单独画：奖励与长度一起升，先当 length hacking，再决定改 reduction 还是改奖励。

## 和 GSPO 的序列级 ratio 分开

GSPO 把 **importance ratio / clip** 提到序列级，解决的是长序列 token ratio 连乘爆炸、MoE 路由下逐步 $\rho_t$ 不稳，不是把 drift KL 改成另一种定义。正则看 $\pi$ vs $\pi_{\mathrm{ref}}$，clip 看 $\pi$ vs $\pi_{\mathrm{old}}$。两边都可以「sequence 级」，对象不同。现场先写两个对比分布，再谈粒度。阿里面试若连问「token 还是序列」，先确认问的是 KL 还是 ratio：答错对象，后续公式就无法回答实际问题。序列级 KL 求和与序列级 $\rho$ 可以同时存在，但不要说成同一个改动。

## 追问

- **哪一种「更正确」？** 定义上求和才是联合 KL；工程上平均更稳。说清 reduction，不站队。怕变长就求和或加长度项，怕短样本被主导就平均。
- **平均会不会让长文 hacking？** 会。逐步偏离被长度除掉，空话便宜。要配长度惩罚或求和 KL，并单独画长度曲线。
- **和 token 级 PPO ratio 是一回事吗？** 不是。ratio 是重要性采样，KL 是正则。GSPO 改的是前者。对象分别是 $\pi_{\mathrm{old}}$ 与 $\pi_{\mathrm{ref}}$。
- **监控该看哪个？** 同时看 sum 与 mean，再看长度分组统计。只看一个会被 reduction 骗。自适应 $\beta$ 必须和监控用同一 reduction，否则控制的目标范围就会不一致。
