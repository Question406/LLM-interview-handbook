---
id: swe-trajectory-deterministic-replay
section: swe-agent
order: 194
level: A
title: 如何设计 Trajectory 的确定性 Replay（种子、工具 mock、环境快照）？
quick: >-
  确定性 replay 要固定三样东西：模型 sampling 的 seed、工具响应的录制夹具、仓库快照的 hash。replay 时禁用真网，逐步断言
  I/O 对得上。它负责让环境能还原，和在线 trace 调试互相补位。
tags:
  - Replay
  - Determinism
  - SWE Agent
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-21T00:00:00.000Z
sources:
  - title: SWE-bench
    url: 'https://arxiv.org/abs/2310.06770'
    type: primary
  - title: Playwright Trace Viewer
    url: 'https://playwright.dev/docs/trace-viewer'
    type: primary
---

要让 trajectory 能确定性地重放，我会固定三样东西：模型 sampling 的 seed、工具响应的录制夹具、仓库和工作区快照的 hash，replay 时默认断网，然后对每一步的 I/O 做断言。`swe-trace-replay` 回答的是失败时要记哪些字段才能归因；这题回答的是环境要怎样才能让逐步 I/O 对得上。

光把 chat 日志重放一遍是不够的。工具一打真网，时钟一跳，沙箱里多一个文件，轨迹马上分叉。比如某个工具的返回里带了当前时间，录制时是下午，重放时是晚上，模型看到的内容变了，下一步就走上了另一条路。所以日志字段再齐，环境也未必能复现。SWE-bench 能比较 patch，是因为容器和测试命令都冻住了；Playwright 这类 trace viewer 能逐步对齐，是因为副作用被录成了夹具。harness 改动之后能做回归，靠的就是这份环境合同，再看一遍模型文案没用。

先说冻什么。一次 attempt 要明确固定：模型 sampling seed（如果允许随机）、工具字段和类型规范（schema）的 hash、仓库 SHA 和工作区快照 hash、镜像 digest、依赖锁、时钟源、环境变量引用。工具响应走录制夹具，同样的请求字节对应同样的响应字节。replay 时禁止访问真网，这和 `swe-sandbox-threat-model` 的默认断网是一回事，既为了确定性，也为了安全。文件系统从快照恢复，别靠「大概在这个 commit」。`uuid`、`Date.now()`、DNS 这类非确定性来源全部注入或冻结。缺任何一个夹具，就只能做条件 replay（resampling 模型），不能说逐步一致。

然后是逐步断言。replay 对每一步检查工具请求、响应、工作区 hash 和测试命令的输出。写成式子就是 $h_t^{\mathrm{replay}}=h_t^{\mathrm{record}}$，第一个让等式不成立的 $t$ 就是分歧点 $t^*$。$t^*\lt T$ 时停下来归因，之后的失败不全算根因。确定性 replay 在 $t^*$ 就失败了，问题在 harness、环境或夹具，不该先怪模型；确定性 replay 能走完、换 seed 的条件 replay 才发散，那才是模型方差。所以现场我会先问「同一套夹具能不能走到同一个 $t^*$」，再决定改模型还是改 harness。

同一套夹具还能拿来做 harness 的回归测试：改了解析器或权限策略之后，旧轨迹应该仍然逐步对齐，否则就显式标记合同变更。我会把 replay 跑进 harness 的 CI，改工具解析或权限后，旧夹具必须全绿或者显式 bump 版本，不允许悄悄漂移。只是「看起来像」的 chat 重放进不了 CI。逐步对齐率 $\alpha \lt 1$ 时，先修时钟和网络夹具，再谈策略对比。

评测上容易刷的地方是：replay 时还在出网；只比最终 patch，不比逐步 I/O；快照里带着 secret 进了通用存储；时间敏感的测试漂了，被算成模型退步。还有一点：SWE-bench 的容器吸收了一部分环境方差，内部 Agent 如果允许安装脚本现场拉包，replay 就可能因为依赖变化出现差异。预构建镜像是确定性的前提，算不上评测优化。

最后，夹具要版本化，并且和 trace 的 request ID 对齐，不然 mock 对不上是哪一次调用。销毁策略和沙箱 TTL 一起写，replay 包里不放凭证明文。trace 规定要记哪些日志，replay 规定怎么恢复环境，两者配合才能稳定地复现和排查。落地最小集是 seed、mock 版本、snapshot hash、逐步 I/O 断言、断网。

## 追问

**和 `swe-trace-replay` 怎么分？**
那题讲记哪些字段；这题讲怎么让环境（seed、mock、snapshot）逐步对齐。

**和 `swe-sandbox-threat-model` 有什么关系？**
断网和隔离既是威胁模型的要求，也是 replay 成立的条件。真网一开，两条都破。

**为什么要比逐步 I/O，比最终 patch 不行吗？**
最终 patch 一样，中间可能走了不同的工具；harness 的 bug 往往出在中间步骤。

**模型必须用 greedy 吗？**
不必须。随机策略要把 seed 写进夹具；没写的话只能做分布对比，没法逐步对齐。
