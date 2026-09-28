---
id: swe-trajectory-deterministic-replay
section: swe-agent
order: 194
level: A
title: 如何设计 Trajectory 的确定性 Replay（种子、工具 mock、环境快照）？
quick: 记录模型采样种子、工具响应夹具与仓库快照哈希；replay 时禁用真网，断言逐步 I/O。与在线 trace 调试互补。
tags:
  - Replay
  - Determinism
  - SWE Agent
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-21
sources:
  - title: SWE-bench
    url: https://arxiv.org/abs/2310.06770
    type: primary
  - title: Playwright Trace Viewer
    url: https://playwright.dev/docs/trace-viewer
    type: primary
---

`swe-trace-replay` 回答「失败时要记哪些字段才能归因」；本题回答「环境怎样才能让逐步 I/O 对得上」。只把 chat 日志重放一遍，工具一打真网、时钟一跳、沙箱里多一个文件，轨迹立刻分叉。错法：把 trace 当 replay——字段齐全仍可能不可复现。确定性 replay 需要种子、工具夹具与仓库快照，并默认断网。SWE-bench 能比较 patch，是因为容器与测试命令被冻住；Playwright 一类 trace viewer 能逐步对齐，是因为副作用被录成夹具。Harness 变更的回归，靠的是这条环境合同，而不是再看一遍模型文案。

## 冻什么：seed、mock、snapshot

一次 attempt 钉死：模型 sampling seed（若允许随机）、工具 schema hash、仓库 SHA 与工作区快照 hash、镜像 digest、依赖锁、时钟源、环境变量引用。工具响应走录制夹具：同一请求字节对应同一响应字节；禁止 replay 时访问真网，这与 `swe-sandbox-threat-model` 的默认断网一致，既为确定性，也为安全。文件系统从快照恢复，而不是「大概在这个 commit」。非确定性源（`uuid`、`Date.now()`、DNS）全部注入或冻结。缺任一夹具，只能做条件 replay（重采样模型），不能声称逐步一致。

## 逐步断言与首个分歧

Replay 对每一步断言：工具请求、响应、工作区 hash、测试命令输出。逐步合同可写成 $h_t^{\mathrm{replay}}=h_t^{\mathrm{record}}$；第一个破坏等式的 $t$ 即分歧点 $t^*$，要求 $t^*\lt T$ 时停止并归因，其后不要全部算根因。若确定性 replay 在 $t^*$ 已失败，问题在 harness / 环境 / 夹具，不该先怪模型。若确定性 replay 能走完而条件 replay（改 seed）发散，才是模型方差。用同一夹具回归 harness：改解析器或权限策略后，旧轨迹应仍逐步对齐，或显式标记合同变更。评测上能刷的是：replay 时仍出网；只比对最终 patch 不对逐步 I/O；快照含 secret 进通用存储；把时间敏感测试的漂移算模型退步。

trace 是日志合同，replay 是环境合同。两者缺一，失败不可运营。落地最小集：seed、mock 版本、snapshot hash、逐步 I/O 断言、断网。现场先问「同夹具能否走到同一 $t^*$」，再决定改模型还是改 harness。SWE-bench 的容器消化了部分环境方差；你的内部 Agent 若允许安装脚本现场拉包，replay 必然漂。预构建镜像不是评测优化，是确定性前提。

夹具要版本化并与 trace 的 request ID 对齐，否则 mock 对不上那一次调用。销毁策略与沙箱 TTL 一起写：replay 包不含凭证明文。能确定性重放的轨迹，才能当 harness 的回归测试；只能「看起来像」的 chat 重放，不够进 CI。若逐步对齐率 $\alpha \lt 1$，先修时钟与网络夹具，再谈策略对比。把 replay 跑进 harness 的 CI：改工具解析或权限后，旧夹具必须全绿或显式 bump 版本，禁止 silently drift。

## 追问

- **和 `swe-trace-replay` 怎么分？** 那题是记哪些字段；本题是让环境（seed / mock / snapshot）逐步可对齐。
- **和 `swe-sandbox-threat-model`？** 断网与隔离既是威胁模型，也是 replay 能成立的条件；真网一开，两条都破。
- **为什么要比对逐步 I/O 而不是最终 patch？** 最终 patch 相同可能中途走了不同工具；harness bug 会出现在中间步。
- **模型必须 greedy 吗？** 不必须，但随机策略要把 seed 写入夹具；否则只能做分布对比，不能逐步对齐。
