---
id: stepfun-agent-tool-training
section: agentrl
order: 102
level: S
title: 阶跃星辰 Agent 算法：针对业务场景，怎样训练 Agent 调工具？
quick: >-
  先把任务、工具契约和可执行环境固定，再由 SFT 打好合法调用与 state grounding 基础；用 fresh rollout 的可验证成功、成本、步骤和
  安全信号训练 / 诊断。reward、数据配比与环境版本必须可复现，不能只展示最终成功率。
tags:
  - StepFun
  - Agent RL
  - Tool Use
  - Reward Design
realInterview: true
status: published
format: markdown
updatedAt: 2026-08-21
sources:
  - title: 阶跃星辰agent算法面经分享 攒人品中（候选人原帖）
    url: https://www.nowcoder.com/feed/main/detail/d01a17cf25344f4bb73eff2dbbaf6eee
    type: candidate-first-hand
---
## 真题记录

- 公司：阶跃星辰（StepFun）
- 团队 / 岗位：Agent 算法
- 届别 / 流程：原帖未披露；轮次未披露
- 面试时间：原帖未披露；帖子发布于 2026-03-30
- 来源类型与可信度：牛客候选人原帖，B
- 原始措辞：**“针对具体业务场景，怎么训练agent调用工具，奖励函数怎么设计和优化的”**

错法：只报最终成功率，却说不清 reward、数据配比和环境版本。阶跃这问要的是一条可复现的业务闭环，不是「上 GRPO」。先把任务、工具契约、可执行环境和成功 oracle 钉死，再谈 SFT / RL。日志字段怎么切见同面的 `stepfun-react-io-blocks`。

## 先写合同，再采轨迹

我会用一个具体业务（例如查单后退款）把 contract 写全：输入 state、可见工具与 JSON schema、权限、environment transition、成功 oracle、不可逆 action。没有 oracle 就不要做 RL，先把任务改到能自动判定。SFT 覆盖：工具发现、参数 grounding、使用 observation、失败 recovery、该停时终止。数据不能只有成功演示，否则不会修，见 `arl-trajectories`。随后在版本固定的 sandbox 里采 fresh trajectory，工具 / 页面 / 权限变了要重采，不能把旧日志当 on-policy，见 `arl-offpolicy-reuse`。业务场景要把不可逆动作单独标出来：退款、发券、改库存不能在探索里打到生产。

## 奖励：硬门 + 终局 + 可验证过程 + 成本

Reward 分解成四层，对应 `arl-reward`：

- Hard gate：schema 非法、越权、不确定副作用，直接失败，不用小负分抵消。
- Outcome：业务终态是否满足 oracle（退款成功、工单关闭）。
- 过程正确：只打可执行检查（订单号存在、原因码在枚举、工具结果被引用）。
- 成本 / 步数：在终局正确的前提下惩罚多余调用，避免刷步骤。

诊断按桶：tool selection、arguments、execution、observation use、plan、environment。每桶看 reward 分布、有效 group、KL、成功率与错误率。数据配比保留难例、失败例和长尾工具，避免简单任务和高频工具把策略拉向投机捷径。优化时先盯 gate 通过率和 oracle 相关；相关掉了先关 shaping。上线前用错误 tool / 错误参数注入，确认过程项会掉、等价 JSON 不会掉，避免训成 formatter。

合同和环境版本先于算法；SFT 打合法调用和恢复；RL 只用可验证成功、安全门和成本。配比要留长尾与失败，报告不能只有成功率。

## 追问

- **没有 sandbox 能训吗？** 很难做 RL。至少要 mock 可回放的状态机，否则 reward 不可复现。
- **奖励项怎么调权重？** 先门槛后加权：gate 不过 outcome 为零。调 $\lambda$ 前先看各项与 gold 成功的相关。
- **SFT 和 RL 谁先？** 先 SFT 到能碰到成功，再 RL。稀疏业务奖励上，随机探索几乎学不动，见 `arl-sparse-reward-exploration`。
- **线上工具变了怎么办？** 视为新环境版本。旧轨迹最多当过滤 BC，不要当当前策略的 PG 数据。
