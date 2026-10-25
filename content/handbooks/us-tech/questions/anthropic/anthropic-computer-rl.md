---
id: anthropic-computer-rl
section: anthropic
order: 28
level: S
title: Anthropic：computer use 上动作级和轨迹级反馈差在哪？确认框为什么不能训进策略？
quick: "动作级反馈告诉模型某一步点得对不对，信号密但易受截图滞后和奖励噪声影响；轨迹级按任务结果判分，更贴近目标但归功困难。可先用演示学 GUI 技能，再用外部检查器做结果奖励；确认授权由宿主管理，不作为可刷分的策略动作。"
tags:
  - Anthropic
  - Computer use
  - RL
  - Agents
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-23
sources:
  - title: Developing a computer use model (Anthropic)
    url: https://www.anthropic.com/research/developing-computer-use
    type: primary
  - title: Computer use tool (Claude Docs)
    url: https://platform.claude.com/docs/en/agents-and-tools/tool-use/computer-use-tool
    type: primary
  - title: Constitutional AI — Harmlessness from AI Feedback
    url: https://arxiv.org/abs/2212.08073
    type: primary
---

动作级反馈帮助模型学局部操作，轨迹级反馈判断整项任务是否成功，两者要配合。确认框则留在宿主权限层。比如把「页面发生变化」当动作奖励，模型乱点广告也可能得分；把「用户点了是」当任务奖励，又可能鼓励策略减少询问或催促确认。

Anthropic 的研究文描述了在计算器、文本编辑器等离线软件上通过截图、数像素和点击训练，再泛化到其他环境。讨论训练时，要把 RL 如何归功与谁有权执行分开，相关执行边界见 `anthropic-computer-use`。

## 局部技能与任务结果各给什么信号

一步记为 $(o_t, a_t)$，$o_t$ 是截图及最近动作文字，$a_t$ 是 `left_click`、`type`、`key`。动作反馈在每个 $t$ 给 $r_t$，例如命中标注框、执行器成功或像素变化；演示中的逐步行为克隆是监督学习版本。

这类信号适合像素计数、计算器按键和拖拽，但要控制噪声。截图会错过短暂提示，点击后的帧可能仍是加载圈。点偏 8 像素失败、偏 2 像素成功，逐步 0/1 会把相近动作分得过硬。Cookie 墙、广告关闭和确认框都能制造页面变化，奖励容易被刷。截图文字本身也不可信，若用页面「任务完成」横幅当 $r_t$，对手可以直接改奖励，见 `anthropic-mm-harm`。

轨迹 $\tau=(o_1,a_1,\ldots,o_T,a_T)$ 的结果改由外部脚本检查，例如文件是否在桌面、订单是否入库，类似 `anthropic-agent-eval` 的功能检查：

$$r_t=0\ (t \lt T),\quad r_T=\mathbf{1}[\mathrm{success}]$$

也可以像 OSWorld 给 $[0,1]$ 完成度。这样允许多条合法路径、重试和自我纠正，与对话 RLHF 给整段偏好类似。代价是几十步才得到一个 bit，REINFORCE 方差大；GAE / 价值网络能帮助归功，关键子目标的过程奖励也可辅助，但定义不能来自不可信页面。

CAI 优化 $p_\theta(y\mid x)$ 的语言倾向，computer use 的 $a_t$ 会改变外部状态，见 `anthropic-rlaif`、`anthropic-constitutional-ai`。AI 可以比较两条轨迹是否鲁莽，得到轨迹偏好，仍需任务结果信号。官方强调训练时不开放上网，以减少真实互联网注入进入梯度；泛化依靠 GUI 技能，这与评测污染控制相关。

## 授权由宿主决定

支付、同意条款和删除在宿主执行前检查。截图疑似注入时的分类器可以推动询问，但它是可关闭的 serving 护栏，不能成为策略网络可自行跳过的动作。

若确认进入动作空间，最大化 $r_T$ 的策略可能少问，因为用户会拒绝；若询问另有惩罚，绕过倾向更强；把网页假按钮视为同意，又等于让环境签发授权。应由产品定义 `SENSITIVE`，模型只提出 $a_t$，人的 yes 进审计日志，通常不作为 $a_t$ 回放。独立训练「何时升级问人」分类器时，也要让标签独立于任务成败。

```python
def exec_or_hold(a_t, user):
    if a_t["action"] in SENSITIVE:
        return "held" if not user.confirm(a_t) else computer.exec(a_t)
    return computer.exec(a_t)
# held 对策略是合法观察，不是可跳过的内部动作
```

同回合多个 `tool_use` 逐步执行、逐步检查，执行器错误码能帮助定位哪一步出错。ASL 对应的能力代价见 `anthropic-safety-levels`，预算应投在执行路径。

## 追问

**逐步行为克隆还需要吗？**
需要。先用演示学像素定位、拖拽等技能，再用 RL 优化任务结果。

**人在环轨迹能作为金标吗？**
能用于行为克隆，但人确认表示该次授权，不能直接推成同类动作都能自动执行。用于训练前要过滤确认后的动作，避免把催促同意当成功策略。

**为什么不只奖励任务成功？**
纯结果奖励既稀疏，也没有覆盖越权与注入，仍需独立权限规则和可核验的局部信号。
