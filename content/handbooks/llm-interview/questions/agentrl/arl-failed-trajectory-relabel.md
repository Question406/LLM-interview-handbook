---
id: arl-failed-trajectory-relabel
section: agentrl
order: 193
level: A
title: 失败轨迹如何重标注后还能用于训练？
quick: >-
  能用。可以用 Hindsight
  把实际达到的状态设成新目标，也可以标出正确前缀和首次出错的动作分开训练。工具超时等环境故障要和模型错误分开，重标后保留失败类型，新标签要用终态断言校验通过才入库。
tags:
  - Relabeling
  - HER
  - Agent Data
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-21T00:00:00.000Z
sources:
  - title: Hindsight Experience Replay
    url: 'https://arxiv.org/abs/1707.01495'
    type: primary
---

能用，但要先切开再标。一种是 HER 式的目标替换：episode 没达到原目标 $g$，但达到了 $g'$，就把这条轨迹重标成「目标本来就是 $g'$」，拿到正信号。另一种是找出 first-error，把正确的前缀和第一个出错的动作分开用。工具超时这类环境故障要和模型的错误分开，重标后保留失败类型，并且要校验新标签真的成立。

比如一个修 bug 的 Agent 没能让目标测试变绿，却让另一个测试从红变绿了。以「让那个测试变绿」为目标，这就是一条成功轨迹。另一条轨迹前几步都对，某一步工具参数填错，后面一路错下去，那前面几步可以留作正上下文，出错那一步当 rejected。

常见的误区有两种：把整条失败轨迹当 SFT 的负例，或者把工具超时、权限变更当成模型选错了。失败轨迹是有结构的，有可修复的前缀、first-error 和不可恢复的外因。它和 `arl-hindsight` 的区别在于，那题事后重估中间步的贡献，这题改的是目标标签和错误切片。`arl-trajectories` 解释了为什么需要 near-miss，这题讲怎么标，以及哪些失败压根不该算到模型头上。

## 两种 relabel，外因样本不算模型的错

目标替换适合目标空间明确的任务，比如到达某个 URL、某个文件树、某个测试由红变绿，原来的 $R=0$ 在 $g'$ 下变成 $1$。开放对话没有可检验的「已达状态」，别硬套。错误点切片是标出 first-error，前缀留作正上下文，错误动作当 rejected，后面如果有 recovery，recovery suffix 当正目标。这是在做修复型的 SFT / preference，和把失败整条克隆是两回事。同一条轨迹可以同时有 HER 目标标签和 first-error 切片，但别混成一个标量：HER 教「达到过什么」，切片教「从哪一步开始错」。

工具超时、限流、环境崩溃、权限被管理员收回，这些外因样本降权或剔除，或者标成 `env_fault` 只用于鲁棒评测，不给 $\pi$ 负梯度。失败类型标签要一直留着，`param_error` / `wrong_tool` / `gave_up` / `env_fault`，否则 relabel 比例没法审计，数据又缩回成只有成功样本。

新标签要自动校验：在新目标 $g'$ 下重放或检查终态断言，真成功才入库。

$$
\tilde r(\tau,g')=\mathbf{1}[\phi(s_T)=g']
$$

$g'$ 要来自可执行的 $\phi(s)$，不能让 LLM judge 随口说「这也算完成」。错误的 relabel 会教模型追求错目标，比如把「停在半成品目录」当成任务成功。

## 报告什么，以及和探索题怎么接

要报 relabel 比例、校验通过率，以及对真实原任务 $g$ 的迁移增益。只在 $g'$ 上变好、原任务不动，说明在刷假目标。稀疏奖励下 HER 是探索工具箱里的一块，见 `arl-sparse-reward-exploration`，它能加密信号，但替代不了课程和可验证的子目标。失败轨迹进训练前还要过 data quality checks，没有 first-error 标签的整条失败，优先丢掉，别硬标。和 `arl-trajectories` 放在一起看：只用成功轨迹会缺恢复能力，乱 relabel 会发明出错误的成功。

## 追问

**和 `arl-hindsight` 是一回事吗？**
两回事。那题用完整的未来重估中间步的 credit，这题改目标标签或做 first-error 切片。两者都能加密信号，被 hack 的地方不同。面试时说成一回事，会显得没分清「换目标」和「改贡献」。

**工具超时能 relabel 成「该先查询状态」吗？**
可以当程序性正例，前提是终态断言支持「未知副作用 → 查单」，别标成「不该调用这个工具」。这类样本进 recovery 桶，并保留 `env_fault` 标签，免得和参数错误混在一起算 relabel 增益。

**开放客服对话能用 HER 吗？**
很难。没有可执行的 $g'$，改用错误点切片和课程。强行让 LLM 编一个 $g'$，校验过不了就不该入库。

**校验失败的 relabel 怎么办？**
丢掉。入库会污染 $g$ 上的成功定义。宁可 relabel 比例低，也别用没校验的样本把稀疏奖励「变密」。
