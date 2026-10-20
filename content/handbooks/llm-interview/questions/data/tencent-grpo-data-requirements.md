---
id: tencent-grpo-data-requirements
section: data
order: 103
level: S
title: 腾讯 TEG：使用 GRPO 时，构造数据要符合什么要求？
quick: "同一个 prompt 要能生成可比较、可验证且得分有差异的多个回答。任务过易或过难，组内全对、全错，都难以提供学习信号。验证器要稳定并防止刷分，题目分布也要覆盖真实目标；先检查有效 group 比例，再增加样本量。"
tags:
  - Tencent
  - TEG
  - GRPO
  - RL Data
realInterview: true
status: published
format: markdown
updatedAt: 2026-08-21
sources:
  - title: 腾讯Teg大模型暑期算法面经（候选人原帖）
    url: https://www.nowcoder.com/feed/main/detail/cce12c13c4af401788cfe08bd76b94b9?urlSource=sitemap
    type: candidate-first-hand
---

## 真题记录

- 公司：腾讯
- 团队 / 岗位：TEG；大模型暑期算法
- 届别 / 流程：暑期实习；轮次未披露
- 面试时间：原帖未披露；帖子发布于 2026-05-18
- 来源类型与可信度：牛客候选人原帖，B
- 原始措辞：**“使用 GRPO 时，构造数据要符合什么要求”**

常见误区是：把 GRPO 数据讲成「再多采一些 SFT 题」。GRPO 的信号来自同一输入提示 下 $G$ 条 采样轨迹（rollout） 的相对优势；组内几乎全对或全错时，group-normalized advantage 接近零，加再多条也是空转。何时 GRPO 失效见 `tencent-teg-grpo-when-bad`，全同组零优势见 `byte-grpo-all-same-zero-adv`、`ali-grpo-advantage`。先报有效 group 比例，再报样本量。

## 题目要落在可探索带

每个 prompt 都要能生成可比较、可验证，并且 reward 有差异的多个回答。难度应落在当前 policy 的可探索区间：太易则全对，太难则全错。不要只堆 benchmark 最难题。选题与过滤同 `data-rlvr-select`：用 pass@$k$ 与 pass@$1$ 的差衡量「还有探索空间」。可执行 验证器（verifier） 优先于 LLM judge；judge / 奖励模型（RM） 必须抽样人审、看校准和对抗 case（`data-verifier`）。

reward 要稳定：等价解不被误杀，格式 / 长度投机有防护（`data-length-hacking`）。组内熵塌缩时，先查数据是否全变成模板，而不是先加大学习率（`data-entropy-collapse`）。

## 分布、去污与动态过滤

检查训练 / eval 去重、领域与长度分布、重复题模板。奖励直方图应看到中间质量，而不是两极。退化 group（方差 $\approx 0$）应动态过滤或重采样，不要静默当零梯度样本。必要时 curriculum：先中等难度，再放长尾。prompt 分布要覆盖真实目标任务，否则 holdout 涨、产品 query 不动。

失败模式：监督微调（SFT） 已会的题继续 GRPO → 空 group；verifier 不认等价答案 → 惩罚正确推理；评测题泄漏 → 假涨。SFT 示范正确轨迹，强化学习（RL） 要可打分难例，不要混成同一份 jsonl。

## 构造时就要为组方差负责

GRPO 的 advantage 是组内相对量：$\hat A_i=(r_i-\bar r)/\sigma_r$。构造数据等于在设计 $r$ 的可分性。同一输入提示 的 $G$ 条必须允许格式对、答案错、答案对但过程长、以及等价解。若 verifier 只认唯一字符串，等价正确会被打成负例，政策学会套模板而不是解题。数学 / 代码优先跑测试或符号等价；开放任务才上 judge，且 judge 要抽人审、看对抗套话。

prompt 侧：去掉重复模板（改几个数字仍是同一道题）、控制长度分布，避免长题占满上下文导致短题学不到。领域覆盖要对着产品 query，而不是对着公开榜单。动态过滤：训练中 pass 率已饱和的题降权或移出；全错题先回到 SFT 或降难度，而不是空转浪费 rollout。Curriculum 不是「从易到难一条路走完」，而是维持探索带：始终有一部分题的 pass@$1$ 在中间。

和「什么时候 GRPO 不好用」是同一面的前后问（`tencent-teg-grpo-when-bad`）：奖励不可靠、组内无方差、格式都没学会时，先别上 GRPO。数据要求就是把这三件事挡在进池之前。有效 group 比例应写进 dashboard，低于阈值就停，查 verifier 与配比，而不是把学习率加大。构造阶段就要拒绝「看起来很难但当前政策零通过」的题，把它们留给 SFT 或更强的 教师模型（teacher） 示范；也要拒绝「已经 95% 通过」的题，它们只会制造空组。等价解、格式变体、部分正确都应在 reward 设计里显式处理，否则组方差是假的，全是格式分在抖。

## 追问

- **有效 group 怎么定义？** 组内 reward 标准差显著大于噪声、且至少一条可学的相对排序。全 $0$ 或全 $1$ 都无效。
- **没有程序 verifier 能做吗？** 能用 RM / judge，但必须当校准对象，hack 风险回到 基于人类反馈的强化学习（RLHF）。优先使用规则、单测和 schema 校验。
- **和 PPO 数据差在哪？** 都要 on-policy 可打分；GRPO 更依赖组内方差，对「全对/全错」更敏感，因为没有 价值评估模型（critic） 平滑。
- **$G$ 越大越好吗？** $G$ 增大能提高组内估计，但 rollout 成本线性涨；先保证难度带，再加 $G$。
- **泄漏怎么防？** 题面指纹与评测 n-gram 重叠表；泄漏会让有效 group 看起来很健康，holdout 却是假的。
