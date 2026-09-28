---
id: arl-failed-trajectory-relabel
section: agentrl
order: 193
level: A
title: 失败轨迹如何重标注后还能用于训练？
quick: Hindsight 把达到的状态当作目标、或标注“可修复前缀 + 错误点”；不要把环境故障标成模型错误。重标注必须保留失败类型标签。
tags:
  - Relabeling
  - HER
  - Agent Data
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-21
sources:
  - title: Hindsight Experience Replay
    url: https://arxiv.org/abs/1707.01495
    type: primary
---

错法：整条失败当负 SFT，或反过来把工具超时、权限变更当成模型选错。失败轨迹有结构：可修复前缀、first-error、不可恢复外因。HER 的做法是：episode 没达到原目标 $g$，但达到了 $g'$，把轨迹 relabel 成「目标本就是 $g'$」从而获得正信号。这和 `arl-hindsight` 不同：那题事后重估中间步的贡献；本题改的是目标标签 / 错误切片。`arl-trajectories` 解释了为什么需要 near-miss；本题讲怎么标，以及哪些失败根本不该当成模型自己的错。

## 两种可用 relabel，外因样本不要当模型错

- **目标替换（HER）：** 适合目标空间明确的任务（到达某 URL、某文件树、某测试由红变绿）。原 $R=0$ 在 $g'$ 下变成 $1$。开放对话没有可检验的「已达状态」，不要硬套。
- **错误点切片：** 标 first-error；prefix 可留作正上下文；错误动作当 rejected；若后续有 recovery，recovery suffix 当正目标。这是修复 SFT / preference，不是把失败整条克隆。

外因（工具超时、限流、环境崩溃、权限被管理员收回）降权或剔除，或标 `env_fault` 只用于鲁棒评测，不要当 $\pi$ 的负梯度。失败类型标签必须保留：`param_error` / `wrong_tool` / `gave_up` / `env_fault`，否则 relabel 比例无法审计，数据又缩回成功-only。同一条轨迹可以同时有 HER 目标标签和 first-error 切片，但不要混成一个标量：HER 教「达到过什么」，切片教「哪一步开始错」。

$$
\tilde r(\tau,g')=\mathbf{1}[\phi(s_T)=g']
$$

自动校验：在新目标 $g'$ 下重放或检查终态断言，真成功才入库。错误 relabel 会教模型追求错目标（把「停在半成品目录」当任务成功）。$g'$ 必须来自可执行 $\phi(s)$，不能让 LLM judge 随口说「这也算完成」。

## 报告什么，以及和探索题怎么接

报告 relabel 比例、校验通过率、对真实原任务 $g$ 的迁移增益。只在 $g'$ 上变好、原任务不动，说明在刷假目标。稀疏奖励下 HER 是探索工具箱的一块，见 `arl-sparse-reward-exploration`；它加密信号，但不能替代课程和可验证子目标。失败轨迹进训练前还要过质量门：无 first-error 标签的整条失败，优先丢掉而不是硬标。和 `arl-trajectories` 一起讲：成功-only 缺恢复；乱 relabel 会发明错误成功。失败要切片或换目标，不要整条当正/当负；外因不是模型错；relabel 必须可重放校验。

## 追问

- **和 `arl-hindsight`？** 那题用完整未来重估中间步 credit。本题改目标标签或 first-error 切片。都可以加密信号，hack 表面不同。现场若把两者说成一回事，会显得没分清「换目标」和「改贡献」。
- **工具超时能否 relabel 成「该查询状态」？** 可以当程序性正例，前提是终态断言支持「未知副作用 → 查单」。不要标成「不该调用该工具」。这类样本应进 recovery 桶，并保留 `env_fault` 标签，避免和参数错误混在一起算 relabel 增益。
- **开放客服对话能用 HER 吗？** 很难。没有可执行 $g'$，应改用错误点切片和课程。若强行让 LLM 编一个 $g'$，校验过不了就不该入库。
- **校验失败的 relabel 怎么办？** 丢弃。入库会污染 $g$ 上的成功定义。宁可 relabel 比例低，也不要用未校验样本把稀疏奖励「变密」。
