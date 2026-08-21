---
id: byte-sft-vs-grpo-objective
section: posttrain
order: 200
level: S
title: 字节大模型算法：SFT 和 GRPO 在优化目标上有何区别？
quick: >-
  SFT 最大化参考回答的 token 似然（教师强制）；GRPO 用组内相对优势优化采样轨迹的期望奖励，并常带 KL
  / clip 约束。前者学“像示范”，后者学“在可验证奖励下更好”。
tags:
  - ByteDance
  - SFT
  - GRPO
  - 2025-2026
realInterview: true
status: published
format: markdown
updatedAt: 2026-08-19
sources:
  - title: 字节跳动 大模型算法一面（候选人原帖）
    url: https://www.nowcoder.com/feed/main/detail/ca5776ee23b147c38ff918104cf9e707
    type: candidate-first-hand
---

## 真题记录

- 公司：字节跳动
- 岗位：大模型算法
- 届别 / 流程：公开一面回忆（2025–2026 校招/实习周期内常见问法）
- 来源类型与可信度：牛客候选人原帖，B（公司与岗位明确，具体日期未披露）
- 原始措辞：**“SFT 和 GRPO 在优化目标的区别”**

陷阱是答「一个监督、一个强化学习」就停。面试要的是目标函数和假设：SFT 最大化固定示范的 token 似然，假设示范近似要模仿的行为；GRPO 最大化组内相对奖励下的期望回报，假设奖励可自动比较。一个学「像 $y^\star$」，一个学「在可验证 $r$ 下更好」。示范差时 SFT 锁死错误；奖励可 hack 时 GRPO 刷分。两者失败模式正好对偶。

## 1. SFT：教师强制下的前向 KL

给定 prompt $x$ 与示范 $y^\star$，

$$
\mathcal{L}_{\mathrm{SFT}}(\theta)=-\sum_t\log\pi_\theta(y_t^\star\mid x,y_{\lt t}^\star).
$$

这是在数据分布上最小化经验前向 KL $D_{\mathrm{KL}}(p_{\mathrm{data}}\|\pi_\theta)$：示范有质量时，格式、推理风格和常见正确答案会被克隆。它**不**看见任务奖励，也不会探索 $y^\star$ 以外的高奖励路径。Teacher forcing 意味着训练时条件是金标准前缀，推理时是自生成前缀，这就是曝光偏差；推理类长链上尤其明显。

失败模式：示范错、示范窄、示范全是长模板时，模型把错误和模板一起锁死；holdout 正确率不动，只会复述训练里的思维链；「看起来像 CoT 但结论错」只要不在 $y^\star$ 里，CE 就不会系统惩罚。继续加同类 SFT 数据，往往把长度和套话先验刻得更深，而不是提高可验证成功率。

## 2. GRPO：组相对优势下的 clipped 策略梯度

对同一 $x$ 采 $\{y^{(i)}\}_{i=1}^G$，用可验证奖励 $r^{(i)}$ 做

$$
\hat{A}^{(i)}=\frac{r^{(i)}-\mu}{\sigma+\epsilon},
$$

再优化 PPO 式 surrogate $\min(\rho\hat{A},\mathrm{clip}(\rho)\hat{A})$，常再加相对 $\pi_{\mathrm{ref}}$ 的 KL。目标是提高高奖励轨迹概率、压低低奖励轨迹，而不是复述某一条固定 $y^\star$。$\rho=\pi_\theta/\pi_{\mathrm{old}}$ 要求近似 on-policy；组全对 / 全错时 $\hat{A}=0$，这一批空转。Clip 限制的是相对行为策略的一步偏离，与 SFT 的 CE 没有任何等价关系。

失败模式：奖励稀疏或可 hack、verifier 与业务不一致时，会变长、套格式、钻 checker；没有示范约束时可读性掉；组方差为零时看似在训、实则无任务梯度。GRPO 优化的是 $\mathbb{E}[r]$ 的相对版本，不是似然，因此「训练 loss 变小」不能当 SFT 那种拟合指标来读。

## 3. 怎么接：先似然后期望，门禁写清楚

实务上常先 SFT 建立格式与基本能力，使 rollout 解析噪声低、组内能出现对错混合；再切 on-policy RL 挤可验证指标。反过来，示范质量差时继续 SFT 只会过拟合；奖励不可靠时上 GRPO 只会 hacking。可执行门禁：格式通过率已高、有自动 verifier、同题多采样仍有方差（$\mathrm{pass@}k-\mathrm{pass@}1$ 明显大于 0）。缺任何一条，优化目标在纸上成立、在线上没有方向。

两者也可以混合：SFT replay 防止 RL 冲掉通用能力；拒绝采样把 RL 发现的高奖励轨迹冻回 CE。那是工程课程，不要说成「目标变成了一个」。面试若被问「能不能把奖励加权进 SFT」，回答那是加权行为克隆，仍不探索示范外轨迹。

## 追问

- **SFT 是不是反向 KL？** 标准 CE/SFT 是前向 KL（覆盖数据模式）；RLHF 里相对 $\pi_{\mathrm{ref}}$ 的惩罚才常是 $\pi_\theta$ 对 ref 的反向 KL。不要把两个 KL 方向混在这道题里。
- **GRPO 还要不要示范？** 要冷启动和锚点，但不把示范当唯一最优。没有 $y^\star$ 也能 RL（R1-Zero），但更脏。
- **目标能否写成同一条期望？** 可以很勉强地说都是 $\mathbb{E}[\log\pi]$，但 SFT 的期望在数据上、系数为 1，GRPO 的系数是 $\hat{A}$ 且数据来自当前政策。这正是区别，不要用这句话把它们说成一样。
