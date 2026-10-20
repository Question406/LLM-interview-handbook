---
id: p3a-openai-design-cloud-ide
section: openai
order: 634
level: A
title: "OpenAI：Cloud IDE：终端流、VM 生命周期和隔离"
quick: "云 IDE 用控制平面管理环境的启动、挂起和回收，用数据平面承载终端和文件，并把持久卷和进程生命周期分开。"
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

## 题目

设计一个浏览器里的云端编程环境：用户可以打开终端、编辑和保存文件、运行代码。题卡还提到一个变体，改为通过 SSH 连接并由系统调度主机。

> 来源：一亩三分地 OpenAI 题卡摘要（2026-10-18 用 Chrome 读取），是网站对候选人报告的二手整理，没有逐条核对原帖；收录为面经题型不代表公司官方确认。规模数字、SLO 和故障情景是手册补的练习约定。

## 思路

先确认面试官问的是浏览器 IDE 还是 SSH 主机集群，两者的入口不同，但后端结构相近。

把系统分成两层：控制平面负责环境的启动、挂起和回收；数据平面承载终端流量和文件读写。多租户安全靠隔离沙箱、资源配额和短期会话授权。用户文件放在独立的持久卷上，和运行进程的生命周期分开，这样回收进程不会丢文件。

## 完整非编程练习（场景与参考回答）

### 具体题目与需求澄清

十万注册用户，峰值一万个同时运行的环境，每个环境 2 核 4GB。需要浏览器终端、文件保存、运行代码和闲置自动挂起。

开始回答时复述这些范围，问面试官是否需要 GPU、协作编辑或自定义镜像。

### 一套可展开的参考答案

**1. 架构与关键路径。**

1. 控制面 API 接收"打开环境"等请求。
2. 环境调度器选择 VM 或容器主机并启动沙箱。
3. 沙箱挂载用户的独立持久卷。
4. 终端通过鉴权过的 WebSocket 代理连到沙箱里的 PTY。

用户代码只在沙箱里执行，绝不放在 API 进程中。

**2. 数据模型和状态变化。** workspace 记录 owner、image digest、volume、`desired_state`、`actual_state`、host 和 lease。状态按 pending → starting → ready → suspending → stopped 变化。每个运行会话绑定一张短期凭证。

**3. 走一遍打开环境。** 用户点"打开"，控制面把 `desired_state` 设为 ready。调度器选一台有余量的主机，按 image digest 启动沙箱并挂载卷，主机汇报后 `actual_state` 变为 ready。控制面签发短期凭证，浏览器带着它建立 WebSocket，代理校验后接到 PTY。用户保存的文件直接写入持久卷；闲置超时后控制面把 `desired_state` 改为 stopped，主机停止进程但保留卷。

**4. 失败、重复与恢复。**

- 调度器重试 create 时使用稳定的 workspace id，避免建出两个环境。
- 主机失联时在别处重建环境，但只有在旧实例被 fence 之后才能以可写方式挂载卷，防止两边同时写坏文件。
- 终端断线默认不杀进程，重连时按会话策略恢复。

**5. 容量和验证指标。** 一万个环境按配额上限需要 2 万核、40TB 内存，所以必须有超售、弹性扩容和闲置回收策略。监控环境启动的 P50/P99、资源利用率和持久文件丢失率。

### 面试追问与参考回答

**SSH 变体要改什么？** 入口网关改成 SSH 认证并负责分配主机，终端通道从 WebSocket 变成 SSH 的 PTY 通道。控制面的生命周期管理、资源隔离和存储契约保持不变。

**怎样防止一个用户的代码影响同一台主机上的其他人？** 每个环境有 CPU、内存和磁盘配额，沙箱限制网络出口和系统调用，凭证只对自己的 workspace 有效。资源打满时被限流的是这个沙箱，而不是整台主机。
