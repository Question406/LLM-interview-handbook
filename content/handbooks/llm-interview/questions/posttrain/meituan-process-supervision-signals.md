---
id: meituan-process-supervision-signals
section: posttrain
order: 107
level: S
title: 美团北斗：过程监督信号怎么设计，还能用在哪？
quick: >-
  把最终任务拆成能独立核验的中间状态、子结论、工具参数或安全约束，并标注 / 验证它们与最终 outcome 的相关性。过程监督也可用于
  verifier 训练、数据筛选、diagnostic eval、curriculum 和在线 failure recovery；不能把不可验证的 CoT 文本直接当正确过程。
tags:
  - Meituan
  - Beidou Program
  - Process Supervision
  - Reward Model
realInterview: true
status: published
format: markdown
updatedAt: 2026-08-21
sources:
  - title: 美团北斗大模型秋招算法岗面经（候选人原帖）
    url: https://www.nowcoder.com/feed/main/detail/5a350d0aa51a4919be606348f9eed3ee
    type: candidate-first-hand
---
## 真题记录

- 公司：美团
- 团队 / 岗位：北斗；大模型秋招算法岗
- 届别 / 流程：秋招；一面
- 面试时间：原帖未披露；帖子发布于 2026-05-24
- 来源类型与可信度：牛客候选人原帖，B（公司、人才计划、岗位和轮次明确；届别、面试日期未披露）
- 原始措辞：**“过程监督的信号具体是怎么设计的。过程监督的信号还能应用在哪些地方。”**

错法：让同一个模型给长 CoT 打漂亮分，并当成过程监督。信号必须能独立核验，并测过与最终 outcome 的相关性。不可验证的推理文本不是正确过程。这题有两问：怎么设计、还能用在哪。第二问往往拉开差距，过程信号不只是 RL 的 dense reward，还可以做筛选、诊断、课程和线上拦截。北斗业务里工具参数、库存状态、权限约束比「思维链好不好看」更适合当信号。

## 1. 从环境里找可复核的中间结果

数学和代码可检查中间断言、单测、类型；Agent 可检查 tool choice、argument grounding、状态转移、证据引用与权限约束。每个 signal $s_k$ 写成指示或分级分，并估计它与 $r^{\mathrm{out}}$ 的相关、false positive / negative、是否可被格式投机。合成时常

$$
r = r^{\mathrm{out}} + \lambda\sum_k w_k s_k,
$$

$\lambda$ 过大就会刷中间分。步骤不唯一或 oracle 不完整时，保留 outcome 为主，用多路径成功样本和人工审计校准，不要强迫模仿一条唯一 reasoning trace。规则 checker 优先于可学习 PRM。PRM 一旦可被提示词 hack，过程监督就退化成「看起来像」。

设计流程我会写成：先列环境可观察事件 → 写自动核验 → 在成功 / 失败轨迹上算相关 → 小 $\lambda$ 接入 → 消融。跳过相关性和消融，过程分只是多了一项会动的曲线。事件级打点再截断，比给整段加一个过程总分更少错误归因。

## 2. 除了 RL 奖励，信号还能用在哪

- **Verifier / PRM 训练标签**：中间对错比整段偏好更密，但标签质量决定上限；
- **Rejection sampling / 数据筛选**：丢掉过程全错的轨迹，或只蒸馏过程也对的，提高 SFT 密度；
- **RL 的 dense feedback**：减轻长轨迹 credit 太粗，尤其 GRPO 组内全失败时仍可能有相对排序；
- **Bad-case 归因与 diagnostic eval**：定位是工具选错还是最后一跳写错，比只报 0/1 有用；
- **Curriculum**：过程通过率当难度，而不是只看最终对错；
- **线上 early-stop / recovery**：过程违规就中断，避免把坏状态滚完。

每一处都要单独验收：用于筛选时看教师上限和覆盖率；用于线上拦截时看误杀。同一套 $s_k$ 在 RL 里当 shaping、在线上当硬闸，阈值往往不同，不要共用一个未经校准的分数。

## 3. 何时失败

中间步骤并不唯一时，强行过程监督会惩罚对的另一条路。Oracle 不完整会系统性误标。过程分与 outcome 脱节时，模型学会「每步像样、结论错」。必须做去掉某一 $s_k$ 的消融。过程 RM 在开放中间步骤上才有必要，且必须配人工审计；能规则就规则。过程监督不能替代 outcome，它是 shaping 和诊断，最终成功仍是主信号。

## 追问

- **过程 RM 和规则过程分怎么选？** 能规则就规则；开放中间步骤才上 RM，并配审计和对抗样本。
- **能替代 outcome 吗？** 不能。主信号仍是最终成功，否则优化目标换了。
- **和 outcome RM 的差别？** Outcome RM 打整段；过程监督对齐的是可定位的中间状态，便于归因和截断。
- **GRPO 里过程分怎么进组内标准化？** 先合成 $r$ 再标准化，或分层标准化，要固定一种并看 $\sigma$；不要有的样本有过程分、有的没有，否则组内不可比。
