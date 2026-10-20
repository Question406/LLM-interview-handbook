---
id: arl-hierarchical-policy
section: agentrl
order: 194
level: A
title: Agent 分层 Policy（Manager-Worker）怎样划分动作与 credit？
quick: "Manager 选择子目标或技能，Worker 执行具体工具调用。子目标要写成能验证的状态断言，在达成或超时时结束一个 option，再分别结算高层和低层的奖励。否则两层只互相聊天，很难判断失败责任。"
tags:
  - Hierarchical RL
  - Options
  - Agent
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-21
sources:
  - title: The Option-Critic Architecture
    url: https://arxiv.org/abs/1604.05079
    type: primary
---

常见误区是：两层都用自由文本聊天。Manager 说「你看着办」，Worker 回一段散文，任务失败后两边同时吃到同一个 $+1$ 或 $-1$。分层的意义是缩短有效决策时长，并给出可审计边界。Options 把技能写成 $o=(I,\pi_o,\beta)$：发起条件、内部策略、终止函数。Agent 里 Manager 选 $o$ 或子目标，Worker 执行原子 tool-call。接口必须是可验证状态断言（「单测已绿」「表单字段已填」），否则 Manager 的奖励是另一层不可执行 shaping。若把分层说成「再加一个规划模型」，多半还没碰到 credit 边界。

## 动作怎么切，信用在哪一层结算

Manager 动作空间：子目标 / skill / option，而不是具体 `patch_file` 参数。Worker：工具名与参数。终止 $\beta(s)$ 在断言满足或预算耗尽时触发，把当前 option 的回报结算给 Manager：

$$
R^{\mathrm{mgr}}=\mathbf{1}[\text{subgoal achieved}]-\lambda\cdot\mathbf{1}[T_{\mathrm{opt}}\gt B]
$$

Worker 用模仿 + 局部 强化学习（RL）（子目标达成、单测、artifact 验证器（verifier））；Manager 用稀疏任务奖励。不要两层同时对同一 文本处理单位（token） 灌 team $+1$。失败归因：子目标达成但任务失败 → Manager 拆错或漏约束；子目标未达成 → Worker 执行差，或子目标本身不可行（该罚 Manager 的目标生成，而不是只打工人）。这和 `arl-multi-credit` 同一逻辑：那题是多 **人** 之间分 team 奖励分数（reward）；本题是同一 Agent 的 **时间层次**。都可以冻一层先训另一层，减少非平稳。Manager 的动作应短、离散、可计数，否则 option 边界会糊成又一段 思维链（CoT，即分步推理过程），分层名存实亡。

## 接口可验证，通信不要变成第二套聊天室

子目标写成断言，能被 harness 检查。Manager 与 Worker 的消息走 typed payload，而不是无结构对话；否则 credit 没有干预点。Worker 允许的工具集随当前 option 签发，option 结束即收回。评测看：option 平均长度、子目标可达率、冻结 Worker 只训 Manager 时任务是否仍动、换 Worker 后是否掉点。子目标可达率低，先查目标是否不可行，再查 Worker；两者都低，多半是接口不可验证，模型在用散文交差。

分层也能服务探索：Manager 在技能空间探索，比 Worker 在原始工具参数上加温度更安全，见 `arl-sparse-reward-exploration`。局部 verifier 必须和任务成功相关，否则工人刷绿测试、任务仍失败，credit 会再次糊掉。分层切的是可验证子目标，不是多一层 Thought；credit 在 option 边界结算；两层同时自由文本等于没分层。

## 追问

- **和 `arl-multi-credit`？** 那题是多 Agent 的人与通信维。本题是 Manager-Worker 的时间层次。冻一侧、局部 verifier 对齐全局，两边通用。分层是把信用结算点钉在 option 边界，不是再雇一个聊天模型。
- **子目标不可执行检查怎么办？** 不要发奖励。改写成测试、文件树哈希、表单字段这类 oracle，否则 Worker 会刷「看起来像完成」的话。Manager 生成不可检查的子目标，应直接记为 Manager 失败。
- **两层一起更新为什么不稳？** Worker 一变，Manager 面对的 option 动力学就变。先冻 Worker 学调度，再交替。这和多智能体非平稳同一机制，只是发生在时间层次而不是不同人之间。
- **option 很长还不终止？** 预算 $B$ 与 $\beta$ 必须有上限，超时记 Manager 失败，避免无限委派。平均 option 长度若接近整条轨迹，分层没有把有效 horizon 缩短，设计就还没成立。
