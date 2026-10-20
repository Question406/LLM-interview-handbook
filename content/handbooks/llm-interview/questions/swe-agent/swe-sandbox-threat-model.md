---
id: swe-sandbox-threat-model
section: swe-agent
order: 5
level: S
title: 如何给代码 Agent 设计 Sandbox 威胁模型？
quick: 容器不是权限模型。按 run 隔离文件系统和身份，默认断网或 egress allowlist，不挂载 secrets，限制 CPU/RAM/PID/磁盘/时间；再用 VM 或 gVisor 增加纵深，并记录审计与销毁策略。
tags:
  - Sandbox
  - SWE Agent
  - Security
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-21
sources:
  - title: gVisor Architecture Guide
    url: https://gvisor.dev/docs/architecture_guide/intro/
    type: primary
---

「我们用了 Docker」不是威胁模型。Issue 文本、仓库、安装脚本、测试、模型生成的代码和 tool output，都是不可信输入，都可以执行任意命令。保护对象是宿主机、其他 tenant、源码、凭证、内网和计费资源。面试官要听的是：每个 run 的身份、网络、密钥和配额分别是什么，越权失败时能不能审计。容器默认共享内核，成功标准也不是「测试跑得起来」。

## 资产与攻击面

按 run 列出不可信输入和可信边界。Agent 读 issue 可能被间接注入；`pip install` / `npm install` 可能跑恶意 lifecycle script；测试可能扫内网、读云 metadata 或外传文件；生成代码可能读 `~/.ssh`、`.env` 或兄弟 workspace。横向移动、秘密外泄、fork bomb、把评测机当跳板，都比经典容器逃逸更常见。gVisor 或轻量 VM 增加系统调用隔离，但要承认兼容性与性能代价，并写进合同，而不是口头说「有沙箱」。多租户时 workspace 禁止共享可写 volume；评测产物默认销毁，需要留档的只留 patch 与脱敏 trace。

## 默认拒绝的运行合同

每个 attempt 用短寿命 workspace 和独立身份：最小挂载、只读基础镜像、不挂生产 secret、默认无网或 egress allowlist（只允许指定包源）。明确限制 CPU、RAM、PID、磁盘和运行时间，超时销毁并回收。高风险动作（任意 egress、写仓库以外路径、提权、访问 metadata IP）走 policy gateway，默认拒绝并记审计。评测需要装依赖时，用预构建镜像，而不是让 Agent 在有凭证的网络里现场 `curl | sh`。需要云 API 时发 per-run、最小 scope、短 TTL 的凭证，禁止复用开发机角色。

## 怎么测、什么算成功

安全评测不是良性仓库能否跑测。要有对抗任务：读宿主机文件、打 metadata、扫内网、外传 `.env`、写共享 volume、耗尽 PID。记录：策略命中（syscall / 网络 / 路径）、被拒命令、指定 canary secret 是否出现在出站流量或日志、资源是否打满。成功标准是越权、横向移动、外泄和资源耗尽被阻断且可用 trace 回放。评测上能刷的是：只测良性仓库、打开 `--privileged` 图方便、把 CI 凭证挂进 sandbox、把拒绝率当安全而不测 utility。沙箱是权限模型加配额加审计，不是容器品牌。落地时把威胁模型写成一页表：不可信输入、保护资产、默认拒绝项、允许例外、审计字段、销毁 TTL。没有这张表，面试里的「隔离」只是形容词。对抗任务应和良性 SWE 任务一起回归，防止为了 resolve rate 把网和特权重新打开。

上线前用 canary 文件和 metadata IP 做一次红队：能读到就失败。审计日志至少保留被拒命令、出站目标和配额耗尽。沙箱策略变更走评审，禁止为了某一类测不过就开特权。

面试官要听的一句话是：每个 run 没有秘密、默认无网、有配额、越权可审计。容器品牌可以变，这四条不能变。为了跑通某一仓库而打开特权，等于没有威胁模型。

## 追问

- **为什么不能给 Agent 云角色？** 云角色凭证可能让攻击者直接访问重要资源，不必先逃出容器；需要云 API 时用短寿命、最小 scope 的 per-run 凭证。
- **断网如何装依赖？** 预构建带锁文件的镜像，或只放行 allowlist 的包源镜像。
- **和 trace 题怎么分工？** 本题是权限边界能否拦住；`swe-trace-replay` 是越权或失败发生后你能不能归因。
- **测试需要出网怎么办？** 只对 mock 或 allowlist 放行，并在 trace 里记下每一次 egress 命中，默认拒绝其它目标。
