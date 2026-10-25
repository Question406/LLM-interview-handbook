---
id: arl-hierarchical-policy
section: agentrl
order: 194
level: A
title: Agent 分层 Policy（Manager-Worker）怎样划分动作与 credit？
quick: "Manager 选子目标或技能，Worker 执行具体工具调用。子目标写成能验证的状态断言，达成或超时就结束这个 option，在边界上分别结算两层的奖励：子目标达成但任务失败记 Manager，子目标没达成再查 Worker 或目标是否可行。两层只用自由文本聊天，失败责任就分不清。"
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

Manager 选子目标或技能，Worker 执行具体的工具调用。子目标写成能验证的状态断言，断言满足或超时就结束这个 option，在 option 边界上分别给两层结算奖励。两层都用自由文本聊天的话，任务失败时分不清是谁的责任。

举个修 bug 的例子。Manager 发出子目标「让登录相关的单测变绿」，Worker 去改代码、跑测试。测试绿了，整个任务却还是失败，说明 Manager 拆错了或者漏了约束；测试一直不绿，要么 Worker 执行得差，要么这个子目标本来就做不到。要是 Manager 只说一句「你看着办」，Worker 回一段散文，失败后两边吃到同一个 $+1$ 或 $-1$，谁也学不到东西。

分层的意义是缩短有效的决策时长，并给出可审计的边界。Options 把技能写成 $o=(I,\pi_o,\beta)$，也就是发起条件、内部策略和终止函数。Agent 里 Manager 选 $o$ 或子目标，Worker 执行原子 tool-call。接口要是可验证的状态断言，比如「单测已绿」「表单字段已填」，否则 Manager 的奖励只是又一层没法执行的 shaping。如果把分层讲成「再加一个规划模型」，多半还没碰到 credit 边界。

## 动作怎么切，信用在哪一层结算

Manager 的动作空间是子目标 / skill / option，具体的 `patch_file` 参数归 Worker，Worker 管工具名和参数。终止函数 $\beta(s)$ 在断言满足或预算耗尽时触发，把这个 option 的回报结算给 Manager：

$$
R^{\mathrm{mgr}}=\mathbf{1}[\text{subgoal achieved}]-\lambda\cdot\mathbf{1}[T_{\mathrm{opt}}\gt B]
$$

Worker 用模仿学习加局部强化学习（RL），信号来自子目标达成、单测、artifact 验证器（verifier）；Manager 用稀疏的任务奖励。两层别同时对同一个文本处理单位（token）灌 team $+1$。失败归因就按开头那个例子：子目标达成但任务失败，记 Manager；子目标没达成，看是 Worker 执行差还是目标本身不可行，不可行的话该罚 Manager 的目标生成，别只罚工人。也可以冻住一层先训另一层，减少非平稳。Manager 的动作要短、离散、可计数，否则 option 边界会糊成又一段思维链（CoT，即分步推理过程），分层就名存实亡了。

## 接口要可验证，通信别变成第二个聊天室

两层之间的消息走 typed payload，别做成无结构对话，不然 credit 没有干预点。Worker 能用的工具集随当前 option 签发，option 结束就收回。评测看 option 平均长度、子目标可达率、冻结 Worker 只训 Manager 时任务还动不动、换了 Worker 后掉不掉点。子目标可达率低，先查目标是否可行，再查 Worker；两个都低，多半是接口没法验证，模型在用散文交差。

分层也能帮探索：Manager 在技能空间里探索，比 Worker 在原始工具参数上加温度更安全，见 `arl-sparse-reward-exploration`。局部 verifier 要和任务成功相关，否则工人刷绿了测试、任务照样失败，credit 又糊了。

## 追问

**和 `arl-multi-credit` 有什么区别？**
那题是多个 Agent 之间分 team 奖励分数（reward），多的是人和通信这一维；这题是同一个 Agent 的时间层次。冻一侧训另一侧、局部 verifier 对齐全局目标，这两招两边通用。

**子目标没法自动检查怎么办？**
那就别发奖励。改写成测试、文件树哈希、表单字段这类 oracle，否则 Worker 会刷「看起来像完成」的话。Manager 生成了没法检查的子目标，直接记 Manager 失败。

**两层一起更新为什么不稳？**
Worker 一变，Manager 面对的 option 动力学就跟着变。先冻 Worker 学调度，再交替更新。这和多智能体的非平稳是同一个机制，只是发生在时间层次上。

**option 很长还不终止怎么办？**
预算 $B$ 和 $\beta$ 都要有上限，超时记 Manager 失败，防止无限委派。平均 option 长度要是接近整条轨迹，分层就没缩短有效 horizon，设计还没成立。
