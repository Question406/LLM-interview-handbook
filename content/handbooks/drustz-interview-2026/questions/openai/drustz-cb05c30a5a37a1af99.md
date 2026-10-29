---
id: drustz-cb05c30a5a37a1af99
section: openai
order: 142
level: A
title: Design a System for Remote Devbox
quick: original-structured-preparation-guide · Design a System for Remote Devbox
companies:
  - openai
tags:
  - DrustZ
  - original-structured-preparation-guide
  - OpenAI · 题库与复习指南
realInterview: false
status: published
format: markdown
updatedAt: '2026-10-28'
sources:
  - title: DrustZ / Mingrui Zhang · pinned source
    url: >-
      https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/1acre3points_crawl/data/questions.json
    type: primary
  - title: 作者记录的原始来源
    url: >-
      https://www.1point3acres.com/interview/problems/7712035f-9c95-4803-8d87-0611bd9aca4c
    type: secondary
---
> DrustZ 整理的复习指南。公司与轮次信息沿用作者的来源记录。

# Design a System for Remote DevBox

## 证据边界

本地原始面经直接记录了“按需提供云端 remote devbox”；公开同题资料补充了临时/持久机器、浏览器/SSH/IDE tunnel、生命周期、组织配额与隔离。本题设计的是**远程开发机平台**，不是协同编辑器或 Colab notebook：编辑器本身、多人光标同步和代码智能补全均不在核心范围。以下是基于这些公开要求整理的原创方案，不是会员原文。

## 可读需求与请求流程

用户从模板创建 DevBox，可 start、stop、pause、resume、delete；选择 CPU、内存、磁盘和可选 GPU。stop 释放算力但保留工作盘，pause 还保存内存快照。组织管理员配置 RBAC、配额、网络策略和审计。目标是常用模板几十秒内冷启动、快照数秒恢复，运行中控制面故障不应杀死现有机器。

```text
POST /devboxes {template:"py", cpu:4, ram_gb:16, persistent:true}
→ 202 {box_id:"b7", desired_state:"RUNNING"}
GET /devboxes/b7 → {actual_state:"RUNNING", connect:{ssh_token:"..."}}

流程：API 鉴权/配额 → 写 desired state → reconciler 领 lease
→ scheduler 选节点 → node agent 启 microVM、挂工作盘、注入短期 secret
→ connection gateway 建立 SSH/IDE tunnel
```



## 解法与架构

控制面包含 API、元数据数据库、配额服务、调度器和幂等 reconciler；数据面包含计算节点、node agent、microVM 与连接网关。任意用户代码按不可信处理，优先 VM/microVM 硬件边界，而非共享内核容器。基础镜像是只读、内容寻址并在节点缓存；用户 home/repo 位于独立加密卷；secret 运行时注入且不得写入镜像或快照。调度采用 filter（资源、区域、GPU、租户隔离）再 score（镜像命中、碎片、负载）。

## 容量推导

假设总计 20 万台、峰值 20% 即 4 万台运行，每台平均 4 vCPU/16GB；需求约 16 万 vCPU、640TB RAM。若节点 64 vCPU/512GB，CPU 限制每节点 16 台，裸需约 2,500 节点；按 70% 可用率预留故障和突发约需 3,600 台。若 Monday burst 为每秒 100 次 create、完整冷启动 30 秒，至少需要约 3,000 个并行 provisioning slot 或足够 warm pool，实际瓶颈通常是算力、镜像拉取和卷挂载，不是元数据 DB。

## 边界与故障测试

验证重复 create 请求不会创建两台、配额在并发下不超卖、stop 与 pause 语义不同、旧事件不能覆盖新 desired state。节点失联时 lease 到期，持久盒在别处重建并重新挂卷；临时盒按约定失败。还要测试镜像损坏、卷 attach 超时、网关断线重连、控制面全挂时运行盒继续、快照中无 secret、租户网络逃逸、GPU 碎片、僵尸盒自动回收和审计日志不可抵赖。

### 来源与内容类型

- Content kind: `original-structured-preparation-guide`
- [原始来源](https://www.1point3acres.com/interview/problems/7712035f-9c95-4803-8d87-0611bd9aca4c)

---

来源：[DrustZ / Mingrui Zhang · 1acre3points_crawl/data/questions.json](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/1acre3points_crawl/data/questions.json)。作者整理资料；许可和第三方来源范围见阅读指南。
