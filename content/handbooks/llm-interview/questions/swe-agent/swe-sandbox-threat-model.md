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
updatedAt: 2026-08-17
sources:
  - title: gVisor Architecture Guide
    url: https://gvisor.dev/docs/architecture_guide/intro/
    type: primary
---

威胁模型先列明不可信输入：issue、repo、依赖安装脚本、测试、生成代码和 tool output 都可能执行任意命令。保护对象包括宿主机、其他 tenant、源码、凭证、网络与计费资源。

每个 run 使用短寿命 workspace 和身份，最小挂载，默认无 credential、无生产网络；设置 egress allowlist、只读基础镜像、CPU/RAM/PID/磁盘/进程/时间配额，并清理 artifacts。容器隔离可配合 gVisor 或 VM，但要承认性能与兼容性代价。

高风险命令和外部写入需 policy gateway 与人工确认。Sandbox 的成功标准不只是“测试跑得起来”，还包括越权、横向移动、秘密外泄和资源耗尽是否被阻断并可审计。
