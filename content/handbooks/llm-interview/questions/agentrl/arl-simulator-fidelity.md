---
id: arl-simulator-fidelity
section: agentrl
order: 192
level: S
title: Agent RL 模拟器保真度不足时，训练出的策略为何会上线失效？如何测 fidelity gap？
quick: 模拟器若简化延迟、部分可观测性或失败模式，策略会过拟合假动力学。用同一策略在真环境/更高保真影子环境对比成功与动作分布差。
tags:
  - Simulator
  - Sim-to-Real
  - Agent RL
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-21
sources:
  - title: Domain Randomization for Sim-to-Real Transfer
    url: https://arxiv.org/abs/1703.06907
    type: primary
---

常见误区是：只把真实成功轨迹当 监督微调（SFT），从不在真实动力学上评估当前策略。模拟器里工具秒回、错误码只有两种、DOM 永远干净、时钟不走，策略会依赖工具总能及时成功的假设。上线后限流、半失败写操作、脏页面一出现，成功率塌掉。这不是「再多采点 sim 轨迹」能修的，是 $P_{\mathrm{sim}}(s'\mid s,a)\neq P_{\mathrm{real}}$。域随机化文献的教训是：训练分布必须覆盖真实会碰到的干扰，否则策略过拟合假物理。

## 常见失真，以及策略会学到什么捷径

- 延迟与超时被抹平：学不会「先查状态再决定是否重试」。
- 失败模式过少：没有部分成功、没有幂等冲突、没有验证码，探索看起来很安全，见 `arl-sparse-reward-exploration` 的安全子集。sim 里安全不等于线上安全。
- 观测过干净：真实是部分可观测，策略在 sim 里靠本不存在的字段做决策。
- 时间不推进：价格、会话、库存在 episode 内恒定，学不会 TTL 与截止。
- 副作用总成功：写接口从不冲突，策略不会查单，上线后双花。

过拟合假动力学时，sim 回报 $\hat V_{\mathrm{sim}}$ 可以很高，真实 $V_{\mathrm{real}}$ 很低。这和 `arl-checkpoint` 互补：那题保证恢复后 $s_t$ 对齐；本题保证训练时用的转移核不要太假。保真度看的是失败模式、延迟分布和部分可观测性像不像，不是页面像素像不像。像素很像但从不限流，仍然是假 MDP。

## 测 gap：冻策略，比 sim 与 real

固定 $\pi$，在 sim 与更高保真影子 / 真实 canary 上比：成功率、平均步数、错误码分布、状态估计误差、动作 KL（同一状态簇上 $\pi$ 是否走了 sim 捷径）。协议对齐 `cu-reproducible-benchmark-run`：frozen 轨用 mock 与镜像 digest，live 轨单独报，不要把 sim 分和 live 分加总。训练侧：域随机化（延迟、错误码、空结果）、真实日志混合、定期真环境 canary。sim 赢、real 输时先列失真清单，而不是加 shaping。动作分布差但成功率接近，往往是策略在 sim 里走了捷径（永远不处理 `429`），真实一限流就塌。

Canary 要按意图分层：只读任务过了，不代表写任务过了。保真度 gap 一旦确认，优先补真实失败模式进 sim，而不是把 real 轨迹再 SFT 一遍却继续在假动力学上 强化学习（RL）。保真度不够，策略优化的是假 MDP。用同一 $\pi$ 量 sim/real 差；上线前真环境 canary。只 SFT 真成功、RL 纯 sim，是最常见的组合翻车。

## 追问

- **只把真实轨迹当 SFT 够吗？** 不够。SFT 覆盖的是成功态；策略在 sim 里学到的恢复行为，真实动力学上可能不成立。要把真实失败模式写进 sim 的转移，而不只是多模仿几条成功演示。
- **域随机化会不会让 sim 更难、训不动？** 会。从窄噪声课程加起，并盯 real canary，而不是一上来把所有故障叠满。随机化的是延迟和错误码，不是把任务目标改掉。
- **和 OPE 的关系？** 真实日志可做 OPE 粗筛，但环境不可复现时 OPE 也偏。fidelity gap 仍要用交互式 real / 高保真影子来量。
- **错误码分布差、成功率却接近？** 仍是 gap。策略可能靠 sim 里不存在的重试捷径在刷分，换真实限流就会爆。
