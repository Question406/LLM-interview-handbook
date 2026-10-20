---
id: anthropic-computer-rl
section: anthropic
order: 28
level: S
title: Anthropic：computer use 上动作级和轨迹级反馈差在哪？确认框为什么不能训进策略？
quick: >-
  动作级给每一步 click/type 打分，密但噪，截图还滞后。轨迹级只在任务结束给成功，稀但对齐产品。确认框是宿主权限，不是模型动作。拿「点过确认」当奖励，策略会学会绕过或刷同意。
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

Computer use 公开之后，研究岗会从 `anthropic-computer-use` 的确认框追到训练：截图上的策略用什么信号更新。Anthropic 的研究文写的是：在计算器、文本编辑器这类离线软件上看截图、数像素、点下去，再泛化。要把 强化学习（RL） 信用分配和产品权限拆开讲。

## 动作级：密、噪、滞后

一步记 $(o_t, a_t)$：$o_t$ 是截图（外加最近动作文本），$a_t$ 是 `left_click`、`type`、`key` 等。动作级反馈给每个 $t$ 一个 $r_t$：点中了标注框、执行器返回成功、像素差超过阈值。模仿学习是它的监督版：人类轨迹上逐步行为克隆。

问题：

1. **观察是翻拍。** 官方自己说截图拼起来像连环画，会错过一闪的提示。用「点击后那一帧」当奖励，可能奖到加载圈。
2. **坐标误差连续。** 点偏 8 个像素任务失败，点偏 2 个像素成功。逐步 0/1 会把几乎对的动作当全错，梯度尖。
3. **奖励可被刷。** 「点击让页面发生变化」会强化乱点。Cookie 墙、确认框、广告关闭都能制造变化。
4. **和注入同通道。** $o_t$ 里的字是不可信数据，见 `anthropic-mm-harm`。若 $r_t$ 来自页面上的「任务完成」横幅，对手写一句横幅就能塑造策略。

动作级反馈适合像素计数、点击计算器按键等可核验的局部 GUI 技能。不适合单独当「会不会转账」的对齐信号。

## 轨迹级：稀、对齐任务，但归功难

轨迹 $\tau=(o_1,a_1,\ldots,o_T,a_T)$。任务成功由 **外部脚本** 判：文件是否在桌面、订单是否写入库，类似 `anthropic-agent-eval` 里 WebArena / OSWorld 的功能检查。奖励形状：

$$r_t=0\ (t \lt T),\quad r_T=\mathbf{1}[\mathrm{success}]$$

或 OSWorld 那种 $[0,1]$ 完成度。这和对话 基于人类反馈的强化学习（RLHF） 把整段回答打一个偏好是同一类：结果对，中间路径可以不同。优点：不绑定某一条点击序列，允许模型绕路、自我纠正（研究文观察到会重试）。缺点：几十步才一个 bit，REINFORCE 方差大。工程上会用 GAE / 价值网络，或对关键子目标打过程奖励，但过程奖励一加就回到「谁定义子目标」——子目标若来自页面文字，又是注入。

和 `anthropic-rlaif` / `anthropic-constitutional-ai` 的关系：CAI 条款优化的是 $p_\theta(y\mid x)$ 的语言倾向；computer use 的 $a_t$ 有外部副作用。你可以用 AI 反馈比较两条轨迹的「是否鲁莽」，那仍是轨迹级偏好，不是逐步点击标签。不要说「有 constitution 所以不用结果奖励」。

训练数据分布：官方强调训练时不给上网，减少把「真实互联网注入」吃进梯度。上线后再面对网页，泛化靠的是 GUI 技能而不是背站点。这和评测污染是对偶，见 `anthropic-agent-eval`。

## 确认框必须留在产品层

敏感动作（支付、同意条款、删文件）在宿主执行前停住，见 `anthropic-computer-use`。分类器在截图上疑似注入时，会把模型拽成先问人——文档写明这层可关，对无人值守不合适。所以它是 **serving 护栏**，不是策略网络的一个离散动作。

若把「弹出确认、用户点了是」写进可学习动作空间，RL 会学坏：

- 最大化 $r_T$ 的策略会少问确认（问了用户可能拒绝，回报变 0）；
- 若问确认有额外惩罚，策略更会绕过；
- 若「用户同意」来自页面上的假按钮，等于让环境签发授权。

正确切法：模型只提议 $a_t$；`SENSITIVE` 集合由产品定义；人的 yes 写审计日志，**不作为 $a_t$ 的一部分回放进训练**，除非你在做独立的「何时该升级问人」分类器，而且那条分类器的标签不能被任务成功绑架。

```python
def exec_or_hold(a_t, user):
    if a_t["action"] in SENSITIVE:
        return "held" if not user.confirm(a_t) else computer.exec(a_t)
    return computer.exec(a_t)
# held 对策略是合法观察，不是可跳过的内部动作
```

常见误区是：用任务成功率当唯一 RL 目标、确认当可跳过工具；对逐步点击做 RL 却用页面是否变化当奖；把分类器当权限系统。

## 追问

- **逐步行为克隆还要不要？** 要。像素计数、拖拽这类技能用演示更稳。RL 放在会操作的策略之上，对结果。
- **一批多个动作怎么归功？** 一回合多个 `tool_use` 必须逐步执行、逐步确认。奖励若打在整批结束，中间一次误点无法定位——这是动作级信号唯一有用的地方：执行器错误码。
- **和 ASL 的关系？** 能力从「说」变成「点」，误操作代价跳一档，见 `anthropic-safety-levels`。护栏预算应放在执行路径，不是再加一条条款。
- **人在环的轨迹能当金标吗？** 能当行为克隆，慎当 RL 正例：人点确认是授权，不是「这种点击都该自动」。过滤掉确认后的动作再训，否则学会催人点是。
