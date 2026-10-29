---
id: meituan-sft-to-rl-gate
section: posttrain
order: 121
level: S
title: 美团大模型：已有 Reasoning SFT 数据，为何还要 RL？何时才切 RL？
quick: >-
  SFT 只会拟合已有的 chain of thought 示范，没法主动探索奖励更高的解法，也压不住刷格式，所以有了推理数据还要 RL。切 RL 看
  acceptance checks：格式和基础正确率达标、有稳定的验证器（verifier）、难题集还有提升空间，并且 SFT 进入平台期后在线
  sampling 仍能产生奖励有差异的轨迹。
tags:
  - Meituan
  - SFT
  - RL
  - Reasoning
  - 2025-2026
realInterview: true
status: published
format: markdown
updatedAt: 2026-08-21T00:00:00.000Z
sources:
  - title: 美团大模型算法岗完整面经（一面+二面）
    url: 'https://www.nowcoder.com/feed/main/detail/b264abf14d4d4c44bc022c9ea1dce981'
    type: candidate-first-hand
---

## 真题记录

- 公司：美团
- 团队 / 岗位：大模型算法
- 届别 / 流程：原帖未披露；一面 + 二面均追问
- 面试时间：原帖未披露
- 来源类型与可信度：牛客候选人原帖，B（公司、岗位与原话明确，届别未披露）
- 原始措辞：**“已经构建推理类 Reasoning 训练数据，为什么还需要接入 RL？仅依靠 SFT 能否满足？”**；**“SFT 达到怎样的效果指标后才适合接入 RL？”**

光靠 SFT 能把格式和中等难度的复述做好，需要搜索的难推理、以及「看起来像 CoT 但结论错」的系统惩罚，它做不到，所以还要 RL。SFT 是行为克隆，RL 是在用当前策略新 sampling 的轨迹上优化期望奖励。至于什么时候切，看 acceptance checks 指标，跟你手里有没有推理数据集无关。一面问为什么要 RL，二面问何时切，两问都要把失败模式说成能检查的指标，只报训练损失（loss）不够。

先说 SFT 为什么不够。它拟合的是示范分布里的格式、推理风格和常见正确答案：

$$
\mathcal{L}_{\mathrm{SFT}}=-\sum_t\log\pi_\theta(y_t^\star\mid x,y_{\lt t}^\star).
$$

似然看不见奖励，也就不会主动探索示范以外奖励更高的路径。一条错误的 CoT 只要不在 $y^\star$ 里，cross entropy loss（CE）就不会系统地压它；一条正确但少见的路径只要不在示范里，CE 也不会抬它。继续加 SFT，更可能是背模板、拉长 chain of thought 刷格式，holdout 上可验证的成功率卡在平台。Teacher forcing 还有 exposure bias：训练时条件是金标准前缀，推理时是自生成前缀，长推理过程上错误会一路累积，SFT 指标好看，不代表 sampling 轨迹（rollout）能做对。

所以「已经构建了 Reasoning 数据」只说明你有一条行为克隆的路，期望回报还没被优化过。数据再多，覆盖的也只是示范的支持集，当前策略能搜到的那些状态它管不到。

RL 补的就是 $\mathbb{E}[r]$。组 sampling RL 在当前 $\pi_\theta$ 上采 $\{y^{(i)}\}$，用可执行的 $r^{(i)}$ 算出 $\hat{A}^{(i)}$，把高奖励轨迹的概率抬高。它能奖励「对但示范里少见」的路径，还能把结构合法性、缺字段、冲突字段做成多维奖励分数（reward）。它是在 SFT 的平台上继续挖期望回报，替代不了 SFT。前提是 verifier 稳、格式已经锁住，否则 $\hat{A}$ 的符号就是噪声，RL 要么 hacking，要么零梯度。没有自动 checker 时，「接入 RL」就不是正确的下一步，应该走偏好，或者先把 verifier 做出来。

acceptance checks 我会写成能量化的几条。先看格式：格式合法率、字段和类型规范（schema）通过率已经很高，解析器不再是主要噪声，同一条轨迹重打分一致。再看验证：有自动 verifier，和人工的一致性可以接受，能分组统计失败类型。然后看还有没有提升空间：保留集上还有清晰的错误桶，同一道题多次 sampling 能出现对错混合，否则组内 $\hat{A}=0$；正面的信号是 $\mathrm{pass@}k-\mathrm{pass@}1$ 仍明显大于 0，说明搜索空间里还有能通过训练提高生成概率的成功轨迹。最后，rollout 基建、版本同步和成本预算都准备好了。

举个例子，SFT 正确率已经到 90%，也可能还要 RL：只要剩下的错误能被 verifier 分出来，而且 pass@k 更高。要是已经全对，GRPO 就是零优势，该换更难的题，别硬切。acceptance checks 没过就强上 RL，只会钻奖励规则的空子或者空转。SFT 什么时候停也别只看 CE，holdout 业务成功、格式稳定、有效组比例才是切点。RL 之后可以用 rejection sampling 把高分轨迹压回 SFT，那是后处理，并不说明 RL 白做了。

## 追问

**没有 verifier 怎么办？**
先别上 RLVR。走 DPO/ 人工偏好，或者先把 checker 做出来。

**SFT 正确率 90% 还要 RL 吗？**
看 pass@k 的缺口和错误能不能验证；已经全对就换题，别空转。

**RL 之后要不要再 SFT？**
可以 distillation 稳定下来的策略，那是回收成果，并不说明「其实 SFT 就够」。

**acceptance checks 里熵怎么看？**
熵太低说明组内多样性不够，这时切 RL 会零方差。先升温或补数据，再切。
