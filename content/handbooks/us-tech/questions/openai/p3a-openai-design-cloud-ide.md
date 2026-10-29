---
id: p3a-openai-design-cloud-ide
section: openai
order: 634
level: A
title: "OpenAI：Cloud IDE：终端流、VM 生命周期和隔离"
quick: "云 IDE 用控制面管理启动、挂起和回收，用数据面承载终端与文件，并让持久卷独立于进程。比如主机失联后换机恢复，必须先 fence 旧实例再可写挂卷；终端断线默认不杀进程，入口改成 SSH 时仍保留同一生命周期与隔离约定。"
companies:
  - openai
tags:
  - 场景参考答案
  - 1Point3Acres
  - Frontier-2026-10
  - Design
  - OpenAI
realInterview: true
status: published
format: markdown
updatedAt: 2026-10-18
sources:
  - title: "1Point3Acres · OpenAI · design-cloud-ide"
    url: https://www.1point3acres.com/interview/problems/company/openai/design-cloud-ide
    type: secondary
---

我会把环境生命周期与终端文件通道分开，再让用户文件放在独立持久卷里。比如闲置后可以停止运行进程、保留文件；主机故障时也能在别处恢复，但要先阻止旧实例继续写卷。

先确认入口是浏览器 IDE 还是 SSH 主机集群。这道练习按十万注册用户、峰值一万个同时运行环境、每个 2 核 4GB 设计，支持编辑保存、终端、运行代码和闲置挂起；还要确认 GPU、协作编辑和自定义镜像是否在范围内。控制面 API 接收打开环境请求，调度器选择 VM 或容器主机、启动沙箱、挂载用户卷；数据面用鉴权 WebSocket 代理连沙箱 PTY，用户代码始终只在沙箱运行。

workspace 保存 owner、image digest、volume、`desired_state`、`actual_state`、host 和 lease，状态依次为 pending、starting、ready、suspending、stopped，每个运行会话绑定短期凭证。用户点打开后，控制面把 `desired_state` 设为 ready，调度器选有余量的主机按镜像摘要启动并挂卷；主机汇报后 `actual_state` 变 ready，再签发凭证供浏览器连接 PTY。保存直接写持久卷，闲置超时把 `desired_state` 改 stopped，停止进程但保留卷。

create 重试用稳定 workspace id，避免重复建环境。主机失联后，先 fence 旧实例，再在别处可写挂卷；终端断线默认不杀进程，按会话策略重连。多租户要有隔离沙箱、资源配额和短期会话授权。按配额上限，一万个环境需要 2 万核、40TB 内存，要设计超售、弹性扩容和闲置回收，监控启动 P50/P99、资源利用率和持久文件丢失率。

## 追问

**SSH 变体改什么？**
入口改成 SSH 认证和主机分配，终端改用 SSH PTY。控制面生命周期、资源隔离和存储契约相同。

**如何避免一人的代码影响同机其他人？**
每个沙箱限制 CPU、内存、磁盘、网络出口和系统调用，凭证只授权自己的 workspace。资源打满时限制该沙箱，避免拖慢整台主机。

> 来源：一亩三分地 OpenAI 题卡摘要（2026-10-18 用 Chrome 读取），是网站对候选人报告的二手整理。规模数字、SLO 和故障情景是手册补的练习约定。
