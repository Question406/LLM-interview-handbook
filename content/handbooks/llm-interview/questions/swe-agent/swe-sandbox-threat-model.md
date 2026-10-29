---
id: swe-sandbox-threat-model
section: swe-agent
order: 5
level: S
title: 如何给代码 Agent 设计 Sandbox 威胁模型？
quick: >-
  容器本身算不上权限模型。我会按 run 隔离文件系统和身份，默认断网或只放行 egress allowlist，不挂 secrets，限制
  CPU、RAM、PID、磁盘和时间，再用 VM 或 gVisor 加一层纵深，并写清审计和销毁策略。
tags:
  - Sandbox
  - SWE Agent
  - Security
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-21T00:00:00.000Z
sources:
  - title: gVisor Architecture Guide
    url: 'https://gvisor.dev/docs/architecture_guide/intro/'
    type: primary
---

我的答案是每个 run 都要做到四条：没有秘密、默认无网、有配额、越权可审计。「我们用了 Docker」说不上是威胁模型，容器默认和宿主共享内核，而且测试能跑起来也说明不了隔离做到了。

先想清楚什么是不可信的。issue 文本、仓库、安装脚本、测试、模型生成的代码、tool output，都可能执行任意命令。比如 issue 里藏一段间接注入，让 Agent 去读 `~/.ssh` 或 `.env`，再借测试把内容发出去。要保护的是宿主机、其他 tenant、源码、凭证、内网和计费资源。

攻击面按 run 列。Agent 读 issue 可能被间接注入；`pip install` / `npm install` 可能跑恶意的 lifecycle script；测试可能扫内网、读云 metadata 或外传文件；生成的代码可能读 `~/.ssh`、`.env` 或者兄弟 workspace。横向移动、秘密外泄、fork bomb、把评测机当跳板，这些都比经典的容器逃逸更常见。gVisor 或轻量 VM 能加系统调用隔离，但兼容性和性能都有代价，这些要写进合同，光口头说「有沙箱」不够。多租户时 workspace 禁止共享可写 volume；评测产物默认销毁，需要留档的只留 patch 和脱敏 trace。

运行合同按默认拒绝来写。每个 attempt 用短寿命 workspace 和独立身份，最小挂载、只读基础镜像、不挂生产 secret，默认无网，或者只允许指定包源的 egress allowlist。CPU、RAM、PID、磁盘和运行时间都明确限住，超时就销毁回收。高风险动作，比如任意 egress、写仓库以外的路径、提权、访问 metadata IP，都走 policy gateway，默认拒绝并记审计。评测要装依赖就用预构建镜像，别让 Agent 在带凭证的网络里现场 `curl | sh`。真要调云 API，发 per-run、最小 scope、短 TTL 的凭证，禁止复用开发机的角色。

怎么证明有效？良性仓库能跑测试说明不了安全，要有对抗任务：读宿主机文件、打 metadata、扫内网、外传 `.env`、写共享 volume、耗尽 PID。记录策略命中（syscall、网络、路径）、被拒的命令、指定的 canary secret 有没有出现在出站流量或日志里、资源有没有打满。越权、横向移动、外泄和资源耗尽都被拦下来，而且能用 trace 回放，才算成功。上线前用 canary 文件和 metadata IP 做一次红队，能读到就算失败。审计日志至少留被拒命令、出站目标和配额耗尽。

容易被刷的地方是：只测良性仓库；图方便开 `--privileged`；把 CI 凭证挂进 sandbox；把拒绝率当安全，不测 utility。所以对抗任务要和良性 SWE 任务一起回归，防止为了 resolve rate 又把网和特权打开。沙箱策略的变更走评审，不允许为了某一类测不过就开特权。为了跑通某个仓库打开特权，等于没有威胁模型。

落地时我会把威胁模型写成一页表：不可信输入、保护资产、默认拒绝项、允许的例外、审计字段、销毁 TTL。没有这张表，面试里说的「隔离」只是个形容词。容器品牌可以换，上面那四条不能变。

## 追问

**为什么不能直接给 Agent 一个云角色？**
云角色的凭证可能让攻击者不用逃出容器就直接碰到重要资源。需要云 API 时，用短寿命、最小 scope 的 per-run 凭证。

**断网了怎么装依赖？**
预构建带锁文件的镜像，或者只放行 allowlist 里的包源镜像。

**测试本身需要出网怎么办？**
只对 mock 或 allowlist 放行，trace 里记下每一次 egress 命中，其他目标默认拒绝。

**这题和 trace 那题怎么分工？**
这题管 authorization rules 能不能拦住；`swe-trace-replay` 管越权或失败发生以后，你能不能归因。
