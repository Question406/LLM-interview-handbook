---
id: drustz-2030d5bbf6ef3f398f
section: mlsd
order: 166
level: A
title: 19 · Case：设计 agent 能力 benchmark · 4. 过程 vs 结果 ⭐⭐⭐（本题核心）
quick: 作者文档章节 · 19 · Case：设计 agent 能力 benchmark · 4. 过程 vs 结果 ⭐⭐⭐（本题核心）
companies: []
tags:
  - DrustZ
  - 作者文档章节
  - ML System Design · 全流程
realInterview: false
status: published
format: markdown
updatedAt: '2026-10-28'
sources:
  - title: DrustZ / Mingrui Zhang · pinned source
    url: >-
      https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/ml_sys_prep/19_case_agent_benchmark.md
    type: primary
---
## 4. 过程 vs 结果 ⭐⭐⭐（本题核心）

### 4.1 只看终态成功率会漏掉的四类情况

| 类型 | 具体形态 | 为什么危险 |
|---|---|---|
| **① 蒙对**（right answer, wrong reason） | 暴力枚举、直接构造目标 URL 跳过流程（WebArena 实测被 exploit）、读 `.git` 历史拿 gold patch（SWE-bench Pro 实测抓到） | 终态对，能力为零。换一个同类任务立刻崩，但 benchmark 给了满分 |
| **② 绕过约束达成目标** | 退款流程跳过身份验证，但退款单确实创建了 | **终态和正确行为完全不可区分**。这是最危险的一类 |
| **③ 代价不可见** | 达成目标但调了 80 次工具、烧了 40 美元、顺手删掉了别的文件（pass-to-pass 测试不覆盖的部分） | 在真实系统里这是事故，在 benchmark 里是满分 |
| **④ 过程对但结果错**（假阴性） | 全部步骤正确，最后一步撞上外部服务 5xx；或 verifier 的字符串匹配没匹上 | 被记成能力缺陷，实际是环境/评分器缺陷。会把改进方向带偏 |

①②③ 是**假阳性**，④ 是**假阴性**。只报一个终态成功率的 benchmark，这四类全部不可见。

### 4.2 一个我自己跑出来的实证 ⭐⭐⭐

在近期自建的 Decagon 备战项目里（`projects/decagon_finetune/levels/level5_process_reward/`），我把"过程 vs 结果"做成了一个可执行的对照实验。场景是退款的五步流程 `verify_identity → lookup_order → check_return_window → check_prior_refund → issue_refund`，额度上限 \&#36;500，共 153 条轨迹分五类：

| 轨迹类型 | 违规 | n | final_only | final + efficiency | process_reward |
|---|---|---|---|---|---|
| compliant | 否 | 70 | **1.000** | 0.750 | +12.0 |
| incomplete | 否 | 18 | 0.000 | −0.114 | +2.3 |
| skip_step | **是** | 26 | **1.000** | **0.800** | −17.0 |
| wrong_order | **是** | 24 | **1.000** | 0.750 | −16.0 |
| over_refund | **是** | 15 | **1.000** | 0.750 | −8.0 |

两个结论，第二个才是杀手锏：

1. **只看结果时，合规与三种违规完全平局**（全是 1.000）。这不是"区分度不够"，是**零区分度**——benchmark 对合规这件事完全失明。
2. **一旦叠加任何效率项，违规就严格胜出。** 每次工具调用扣 0.05 之后，`skip_step` 得 0.800，`compliant` 只有 0.750。跳过校验少调一次工具、同样拿到退款，**净赚**。

> **高分句**：现实中没有"纯粹只看结果"的评测——总会叠一个延迟项或成本项，因为没有哪个生产系统对延迟和成本无感。而"结果 + 效率"这个组合会主动把最高分发给绕过合规的 agent。这就是为什么过程约束必须是一个独立的**否决维度**，而不是总分里的一个加权项。

第三个容易被忽略的区分：**`incomplete`（没做完，也没违规）不能和 `skip_step`（做错了）同等处理。** 如果 benchmark 把两者都记成"失败"，被优化的 agent 会学成"宁可什么都不做"——那是另一种失败模式。所以判分要三分类：

```text
success       终态达成 且 无硬约束违规
incomplete    终态未达成 且 无违规      ← 扣分
violation     任何硬约束被破坏           ← 无论终态如何，整题判负
```



### 4.3 过程评分的四种实现（按可靠性排序）

| 方式 | 怎么做 | 可靠性 | 可被 game 吗 | 维护成本 |
|---|---|---|---|---|
| **必经点断言** | 任务定义里声明 `must_call` / `must_not_call` / 顺序约束 / 参数约束，从 trace 程序化检查 | 高（确定性） | 中：agent 会"调了但不看返回值" | 每任务几行 |
| **中间状态比对** | 关键步之后对环境快照做断言 | 高 | 低 | 需要环境支持细粒度快照 |
| **反事实探针** | 改一个前提（订单已过退款窗口），看行为是否随之改变 | **最高，专治"蒙对"** | 极难 | 要成对造题 |
| **rubric / LLM judge 读 trace** | 判"是否核实了身份"这类语义条件 | 低–中 | 容易 | 最低 |

**反事实探针值得单独展开**，它是本节最有区分度的设计：

它绕开了"路径不唯一"这个根本困难——不检查 agent 走了哪条路，只检查它的**行为是否对关键前提敏感**。造一对任务，除了"订单是否在退款窗口内"这一个变量外全部相同：

- 真正执行了 `check_return_window` 的 agent：A 退款，B 拒绝。
- 跳过校验直接退款的 agent：A、B 都退款——A 判对、B 判错，**终态指标上它照样能拿到这一对里一半的分；但在配对差分上它得 0，因为它的行为对关键前提完全不敏感。**

> **高分句**：单个样本的绝对分数没法区分"会做"和"蒙对"，**成对任务的行为差分**才是能力证据。

这和我在 Anthropic take-home 里做的 **137 对扰动测试套件**是同一个思想：不看单样本绝对分，看扰动前后的行为差分，并且**按扰动类型分层报检出率**——因为总的检出率会掩盖"对某一类扰动完全无感"这种致命缺口。同一套方法直接可以搬到 agent benchmark 上。

### 4.4 过程分为什么不能当主分

三条理由，面试里要主动说，否则会被追问打回：

1. **路径不唯一**：任何"必须按这个顺序调这几个工具"的评分都会惩罚更优的解法。**所以断言要写成约束（`verify_identity` 必须在 `issue_refund` 之前完成）而不是脚本（第 1 步必须是 `verify_identity`）。**
2. **过程分自己会被 game**：`must_call` 里有 `verify_identity`，agent 就学会调用它然后忽略返回值。防御是把断言绑定到**数据流**上——`issue_refund` 的 `order_id` 必须来自上一步 `lookup_order` 的返回值，而不是凭空生成；再配上反事实探针交叉验证。
3. **过程分需要人来定义**，因此覆盖不全。硬约束能穷举（政策条款是有限的），"好的解题路径"不能。

**最终结构：结果作 gate，过程作否决项与诊断维度，两者不做加权求和。**

推荐的每题输出（而不是一个标量）：

```text
verdict:        success | incomplete | violation | infra_failure
violations:     [skipped_verify_identity, over_limit_refund, ...]
cost:           steps, tool_calls, input/output tokens, $, wall_clock
robustness:     injected_fault_recovered: true/false
counterfactual: paired_task_id, behavior_changed: true/false
```



> **高分句**：过程分不是给成功的 agent 加分用的，是给"看起来成功"的 agent 减分用的。

---

---

来源：[DrustZ / Mingrui Zhang · ml_sys_prep/19_case_agent_benchmark.md](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/ml_sys_prep/19_case_agent_benchmark.md)。作者整理资料；许可和第三方来源范围见阅读指南。
