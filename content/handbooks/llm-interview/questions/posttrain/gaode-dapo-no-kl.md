---
id: gaode-dapo-no-kl
section: posttrain
order: 212
level: A
title: 高德大模型：DAPO 为什么可以不额外加 KL 惩罚？GRPO 后期收益衰减怎么优化？
quick: >-
  DAPO 通过动态采样、token 级策略与对异常组的处理来控制更新，不一定再叠经典
  $\beta\mathrm{KL}$。后期衰减则查奖励饱和、KL/熵塌缩、数据过易与过拟合，用换难度、重采样、约束退火或换目标缓解。
tags:
  - Amap
  - Alibaba
  - DAPO
  - GRPO
  - 2025-2026
realInterview: true
status: published
format: markdown
updatedAt: 2026-08-21
sources:
  - title: 高德大模型算法岗二面面经（相关推荐收录于百度面经页）
    url: https://www.nowcoder.com/discuss/863890669662674944
    type: secondary
  - title: DAPO
    url: https://arxiv.org/abs/2503.14476
    type: primary
---

## 真题记录

- 公司：高德（阿里系）
- 原始措辞（相关面经）：**“DAPO 算法为什么不需要额外引入 KL 惩罚项”**；**“GRPO 训练自带 KL 约束，训练后期收益衰减明显，有哪些优化手段？”**

错法：把「DAPO 可以不额外加 KL」说成「永远不需要锚点」或「KL 在数学上多余」。DAPO 用动态采样、clip 形状和样本过滤本身在管更新幅度与样本质量；显式 $\beta D_{\mathrm{KL}}(\pi_\theta\|\pi_{\mathrm{ref}})$ 变成可选项，不是物理定律消失。落地以实现与消融为准。开放对齐、安全、格式锚仍可能需要 replay 或小 KL。论文机制不等于你的训练脚本默认关了 KL。

## 1. DAPO 用什么代替显式 drift KL

先分清两套约束。Clip 限制的是相对上一轮行为策略 $\pi_{\mathrm{old}}$ 的一步偏离，是 trust-region；经典 GRPO / PPO 再叠加的 $\beta\mathrm{KL}$ 限制的是相对冻结 SFT $\pi_{\mathrm{ref}}$ 的漂移，是 drift。DAPO 针对的失控主要来自样本质量和 clip 不对称，而不是先发明「可以不要锚」：

- **动态采样**：丢掉组内全对 / 全错（零优势）组，保证每批都有相对信号，减少无效大步和「看起来在训、梯度是 0」；
- **Clip-higher**：抬高 clip 上界，让正优势样本有上升空间，同时下界仍限制 $\rho$ 不要把坏样本概率压到数值崩；
- **Token 级损失解耦、过长惩罚**：减轻长回复在序列平均里主导梯度，以及长度 hacking。

这些已经在管「一步更新多大、哪些样本能进 batch」。再叠很大的 $\beta\mathrm{KL}$ 可能把探索掐死，尤其后期 $\pi_\theta$ 已离 SFT 较远、同样 $\beta$ 会把任务梯度抵消掉。面试应说「用采样与裁剪策略替代或减弱显式 KL」，并承认：分布外安全、指令遵循、通用能力仍可能需要 replay。把「无 KL」当成 DAPO 的定义是错的，核心卖点是采样与 clip 工程。

方法失败：动态采样后有效 batch 过小，更新频率崩；clip-higher 过大近似未 clip，高 $\hat{A}$ 样本把格式冲掉；关掉 KL 又没有 OOD holdout，域外先崩。

## 2. GRPO 后期收益衰减：先诊断再换算法

衰减不是单一病。并行看训练 reward、holdout 成功率、entropy、KL 到 ref、clip fraction、组内 $\sigma$、唯一解比例、回复长度：

- 题变简单，全对组变多，$\hat{A}\to 0$，有效信号枯竭；
- 熵塌、采样多样性没了，组内对照变弱，唯一解比例升高；
- $\beta$ 过大，政策被钉在旧锚上，任务分涨不动；
- verifier 泄漏或长度 hack，训练 reward 涨、holdout 不动。

只盯平滑后的训练 reward 会把过拟合和刷分当成「还在涨」。KL 约束本身也会造成「后期不动」：不是衰减，是被拴住。要分开：holdout 已饱和 vs 训练分还在抖但 holdout 掉。

## 3. 优化手段按诊断下药

提高难题占比、增大 $G$、动态过滤零方差组；退火 $\beta$ 或换 DAPO / GSPO；检查 parser 泄漏和测试用例是否被模型背下来；用过长惩罚而不是放任变长。换目标却不换题池，衰减依旧。课程要维持组内方差：太易过滤、太难先降档。失败时回滚 checkpoint，不要在已塌的熵上继续加大更新。

高德这类业务还要盯地理 / 结构化字段：规则奖励过窄会让政策只会刷一种模板，域外 POI 或新槽位崩掉，这和「后期衰减」经常是同一件事的 OOD 版本。

## 追问

- **Trust-region KL 和 drift KL 是同一个吗？** 不是。Clip 相对 $\pi_{\mathrm{old}}$；$\beta\mathrm{KL}$ 相对冻结 $\pi_{\mathrm{ref}}$。DAPO 减弱的通常是后者。
- **关掉 KL 会不会必崩？** 看任务是否可验证、是否有 clip 与动态采样、是否有 OOD 门禁。开放对齐上更危险。
- **后期唯一解比例升高说明什么？** 探索枯竭。先改难度和采样，再改学习率。硬推 lr 只会把塌缩刻死。
- **DAPO 动态采样会不会偏题？** 会，永远做不对的难题被丢掉，课程会越来越易。要给超难题单独池，而不是全局过滤掉。
