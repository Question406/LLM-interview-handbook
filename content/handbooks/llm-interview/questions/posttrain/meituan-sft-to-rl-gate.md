---
id: meituan-sft-to-rl-gate
section: posttrain
order: 121
level: S
title: 美团大模型：已有 Reasoning SFT 数据，为何还要 RL？何时才切 RL？
quick: >-
  SFT 只能拟合已有思维链示范，难主动探索更高奖励解法与抑制刷格式。切 RL 的门禁通常是：格式 / 基础正确率达标、有稳定
  verifier、难度集仍有提升空间，且 SFT 指标平台期后 online 采样仍能拉开奖励方差。
tags:
  - Meituan
  - SFT
  - RL
  - Reasoning
  - 2025-2026
realInterview: true
status: published
format: markdown
updatedAt: 2026-08-21
sources:
  - title: 美团大模型算法岗完整面经（一面+二面）
    url: https://www.nowcoder.com/feed/main/detail/b264abf14d4d4c44bc022c9ea1dce981
    type: candidate-first-hand
---

## 真题记录

- 公司：美团
- 团队 / 岗位：大模型算法
- 届别 / 流程：原帖未披露；一面 + 二面均追问
- 面试时间：原帖未披露
- 来源类型与可信度：牛客候选人原帖，B（公司、岗位与原话明确，届别未披露）
- 原始措辞：**“已经构建推理类 Reasoning 训练数据，为什么还需要接入 RL？仅依靠 SFT 能否满足？”**；**“SFT 达到怎样的效果指标后才适合接入 RL？”**

这块容易答「数据已经有思维链，继续 SFT 就行」或「有数据就可以立刻 GRPO」。SFT 是行为克隆，RL 才在 fresh rollout 上优化期望奖励。切不切看门禁，不看你有没有推理数据集这个事实。一面问为什么还要 RL，二面问何时切：两问都要把失败模式说成可检查的指标，不要只报训练 loss。仅靠 SFT 能满足格式与中等难度复述，满足不了需要搜索的难推理和「看起来像 CoT 但结论错」的系统惩罚。

## 1. SFT 为什么不够：似然看不见奖励

SFT 拟合示范分布里的格式、推理风格和常见正确答案：

$$
\mathcal{L}_{\mathrm{SFT}}=-\sum_t\log\pi_\theta(y_t^\star\mid x,y_{\lt t}^\star).
$$

它不能主动探索示范外的更高奖励路径。只要错误 CoT 不在 $y^\star$ 里，CE 就不会系统压它；只要正确但少见的路径不在示范里，CE 也不会抬它。继续加 SFT 更容易背模板、拉长思维链刷格式，holdout 可验证成功率平台。Teacher forcing 还有曝光偏差：训练条件是金标准前缀，推理是自生成前缀，长链上错误会累积，SFT 指标好看不代表 rollout 能做对。

因此「已经构建 Reasoning 数据」只说明你有一条行为克隆的路，不说明期望回报已被优化。数据再多，覆盖的是示范支持集，不是当前政策能搜到的状态集。

## 2. RL 补的是 $\mathbb{E}[r]$，门禁失败时不要上

组采样 RL 在当前 $\pi_\theta$ 上采 $\{y^{(i)}\}$，用可执行 $r^{(i)}$ 得 $\hat{A}^{(i)}$，提高高奖励轨迹概率。它能奖励「对但示范里少见」的路径，并把结构合法性、缺字段、冲突字段做成多维 reward。不是替代 SFT，而是在 SFT 平台上继续挖期望回报。失败：verifier 不稳或格式未锁时，$\hat{A}$ 的符号是噪声，RL 会 hacking 或零梯度。没有自动 checker 时，不要把「接入 RL」当成正确下一步，应走偏好或先把 verifier 做出来。

## 3. 可量化门禁，用指标而不是感觉

1. 格式合法率 / schema 通过率已高，解析器不再是主噪声；同一轨迹重打分一致；
2. 有自动 verifier，与人工一致性可接受，能分桶看失败类型；
3. 保留集仍有清晰错误桶，同题多采样能出现对错混合，否则组内 $\hat{A}=0$；正向信号是 $\mathrm{pass@}k-\mathrm{pass@}1$ 仍明显大于 0，说明搜索空间里还有可 amplify 的成功轨迹；
4. rollout 基建、版本同步和成本预算就绪。

SFT 正确率已经 90% 仍可能要 RL：剩余错误可被 verifier 分出、且 pass@k 更高。若已经全对，GRPO 零优势，应换更难题而不是硬切。门禁失败时强行 RL 只会 reward hacking 或空转。SFT 终止不要只看 CE：holdout 业务成功、格式稳定、有效组比例才是切点。RL 之后可以用拒绝采样把高分轨迹压回 SFT，那是后处理，不是否定 RL。

## 追问

- **没有 verifier 怎么办？** 先别上 RLVR。走 DPO / 人工偏好，或先把 checker 做出来。
- **SFT 正确率 90% 还要 RL 吗？** 看 pass@k 缺口和错误是否可验证；全对则换题，不要空转。
- **RL 后要不要再 SFT？** 可以蒸馏稳定政策，但那是回收，不是「其实 SFT 就够」。
- **门禁里熵怎么看？** 熵过低则组内多样性不足，切 RL 会零方差；先升温或补数据，再切。
