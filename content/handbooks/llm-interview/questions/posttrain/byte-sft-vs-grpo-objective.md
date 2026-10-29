---
id: byte-sft-vs-grpo-objective
section: posttrain
order: 200
level: S
title: 字节大模型算法：SFT 和 GRPO 在优化目标上有何区别？
quick: >-
  SFT 在固定示范上最大化 token 似然，学的是「像示范」；GRPO 对同一题采一组回答，用组内相对优势最大化可验证奖励下的期望回报，常带 KL /
  clip 约束，学的是「在奖励下更好」。实务上先用 SFT 把格式立住，组内出现对错混合了再切 GRPO。
tags:
  - ByteDance
  - SFT
  - GRPO
  - 2025-2026
realInterview: true
status: published
format: markdown
updatedAt: 2026-08-21T00:00:00.000Z
sources:
  - title: 字节跳动 大模型算法一面（候选人原帖）
    url: 'https://www.nowcoder.com/feed/main/detail/ca5776ee23b147c38ff918104cf9e707'
    type: candidate-first-hand
---

## 真题记录

- 公司：字节跳动
- 岗位：大模型算法
- 届别 / 流程：公开一面回忆（2025-2026 校招/实习周期内常见问法）
- 来源类型与可信度：牛客候选人原帖，B（公司与岗位明确，具体日期未披露）
- 原始措辞：**“SFT 和 GRPO 在优化目标的区别”**

SFT 最大化固定示范的 token 似然，前提是示范大致就是想模仿的行为；GRPO 最大化组内相对奖励下的期望回报，前提是奖励能自动比较。一个学「像 $y^\star$」，一个学「在可验证的 $r$ 下更好」。答到「一个监督、一个 RL」就停，面试官会觉得没讲到目标函数。

先看 SFT。给定 prompt$x$ 和示范 $y^\star$，

$$
\mathcal{L}_{\mathrm{SFT}}(\theta)=-\sum_t\log\pi_\theta(y_t^\star\mid x,y_{\lt t}^\star).
$$

这等价于在数据分布上最小化经验前向 KL $D_{\mathrm{KL}}(p_{\mathrm{data}}\|\pi_\theta)$。示范质量好的时候，格式、推理风格和常见的正确答案都会被克隆下来。可它看不见任务奖励，也不会去探索 $y^\star$ 以外的高奖励路径。另外 teacher forcing 训练时条件是金标准前缀，推理时却是模型自己生成的前缀，这就是 exposure bias，推理类的长推理过程上特别明显。

SFT 坏起来是这样的：示范错、示范窄，或者全是长模板，模型就把错误和模板一起锁死，holdout 正确率不动，只会复述训练里的 chain of thought。比如一条「看起来像 CoT、结论却错」的输出，只要它不在 $y^\star$ 里，cross entropy loss（CE）就不会系统地惩罚它。这时候继续堆同类 SFT 数据，往往只是把长度和套话的先验刻得更深，可验证的成功率提不上去。

GRPO 是另一套。对同一个 $x$ 采 $\{y^{(i)}\}_{i=1}^G$，用可验证奖励 $r^{(i)}$ 算

$$
\hat{A}^{(i)}=\frac{r^{(i)}-\mu}{\sigma+\epsilon},
$$

再优化 PPO 式的 surrogate $\min(\rho\hat{A},\mathrm{clip}(\rho)\hat{A})$，通常还加一项相对 $\pi_{\mathrm{ref}}$ 的 KL。它做的是把高奖励轨迹的概率抬高、低奖励的压低，用不着复述某一条固定的 $y^\star$。$\rho=\pi_\theta/\pi_{\mathrm{old}}$ 要求近似 on-policy；组内全对或全错时 $\hat{A}=0$，这一批就空转。Clip 限制的是相对行为策略的一步偏离，和 SFT 的 CE 没有任何等价关系。

GRPO 坏起来又是另一种样子：奖励稀疏或能被 hack、验证器（verifier）和业务对不上，模型就变长、套格式、钻 checker；没有示范约束，可读性往下掉；组方差为零时看着在训，其实没有任务梯度。它优化的是 $\mathbb{E}[r]$ 的相对版本，跟似然无关，所以「训练 loss 变小」不能像 SFT 那样当拟合指标读。

两者怎么接？实务上通常先 SFT，把格式和基本能力建起来，让 sampling 轨迹（rollout）的解析噪声低、组内能出现对错混合；再切到 on-policy RL 提可验证任务的成功率。示范质量差还继续 SFT，只会 overfitting；奖励不可靠就上 GRPO，只会 hacking。acceptance checks 可以写成三条：格式通过率已经很高、有自动 verifier、同题多 sampling 仍有方差（$\mathrm{pass@}k-\mathrm{pass@}1$ 明显大于 0）。缺任何一条，优化目标在纸面上成立，到线上却没有方向。

两者也能混着用：SFT replay 防止 RL 冲掉通用能力，rejection sampling 把 RL 发现的高奖励轨迹再冻回 CE。那是工程上的课程安排，别说成「两个目标变成了一个」。

## 追问

**SFT 是不是 reverse KL？**
不是。标准 CE/SFT 是前向 KL，覆盖数据的模式；RLHF 里相对 $\pi_{\mathrm{ref}}$ 的惩罚才常是 $\pi_\theta$ 对 ref 的 reverse KL。这道题里别把两个 KL 方向混在一起。

**GRPO 还要不要示范？**
要冷启动和 reference examples，只是不把示范当成唯一最优。没有 $y^\star$ 也能做 RL，R1-Zero 就是例子，只是更脏。

**两个目标能不能写成同一条期望？**
很勉强地可以说都是 $\mathbb{E}[\log\pi]$，可 SFT 的期望在数据上、系数是 1，GRPO 的系数是 $\hat{A}$，数据来自当前策略。区别就在这儿，别用这句话把它们说成一样。

**能不能把奖励加权进 SFT？**
能做，那就是加权行为克隆，仍然不会探索示范以外的轨迹。
