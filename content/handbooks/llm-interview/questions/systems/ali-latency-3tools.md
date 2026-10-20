---
id: ali-latency-3tools
section: systems
order: 20
level: S
title: 场景题：Agent 链路含 3 个工具且高频请求，延迟如何优化？
quick: 并行可并行的工具、缓存高频路径、意图分流到轻量模板、缩小 prompt/工具集、投机/小模型草稿、超时降级与限流。先量测再改。
tags:
  - Alibaba
  - Agent
  - 性能
realInterview: true
status: published
format: markdown
provenance: legacy-handbook-v2
updatedAt: 2026-08-21
sources:
  - title: ↗ 淘天大模型 Agent 校招面经
    url: 'https://www.nowcoder.com/discuss/911218249889480704'
    type: legacy-reference
---

常见误区是：换更大模型，或把三条工具一律串进 ReAct、每步再「思考一下」。三条工具加高频请求，先画依赖图再改：能并行的并行，高频路径缓存或走固定 workflow，缩短输入提示，减少暴露的工具，投机或小模型打草稿，超时降级与限流。先量测 p95/p99、工具 RT、LLM RT、排队，再动架构。规划与调度见 `ali-modular-agent-plan`，prompt 裁剪见 `ali-prompt-optimize`。

## 先画依赖图，再谈并行

把三个工具画成 DAG：无数据依赖的只读查询并行；必须用上一步结果的（查单 → 算价 → 支付）保持串行。并行只适用于读路径；强一致写路径串行，并用请求 id 对齐一次快照，避免读到脏数据。客服常见组合是查订单、查物流、查售后政策：前两个互不依赖可并行，政策可按类目缓存。SLA 要写清：非关键工具超时可跳过，关键工具只能降级，不能静默丢。

并行省的是实际耗时时间，不直接减少 token 消耗。三轮串行 ReAct 会叠三次输入预填充（prefill），也就是处理输入并建立缓存；若工具结果还回灌成长上下文，后续轮次更慢。能一次规划出工具集合就不要逐步猜。投机解码、小模型草稿只加速 LLM 段，工具 RT 占主导时收益接近零。见 `sys-specdecode`、`sys-serving-metrics`。

## 高频路径绕开多轮 LLM

高频意图（「快递到哪了」）用小模型分类 + 缓存或固定 workflow，不必每单让大模型重选工具。首包分类走轻量模型，复杂再升级。压缩上下文与 工具字段和类型规范（schema），只暴露当前意图相关工具，减少 prefill。工具说明膨胀是隐性延迟：五十个 schema 全塞进去，首个 token 的等待时间（TTFT）就会增加。限流与隔离要按意图：高峰时保查物流，把闲聊和推荐降级，避免非关键请求占满队列，拖慢关键请求。

## 量测切到对的瓶颈

拆 p95/p99 到 LLM prefill/decode、各工具 RT、网关排队。若 p99 高在物流 RT 而不是 LLM，给物流设超时并降级「以承运商页面为准」，而不是换 70B。缓存要带失效：订单状态短 TTL，政策可长缓存。没有依赖图和分层延迟，优化顺序一定反。

## 追问

- **并行会不会读到脏数据？** 只读查询可并行并对齐快照；写路径、支付、改地址保持串行。见 `ali-hitl-risk`。
- **三条必须串行怎么办？** 砍 LLM 轮次和 prefill：一次规划、固定 workflow、压缩 schema，而不是再加并行。
- **小模型分流会不会分错？** 设置信阈值，低置信回大模型；用错误路由率而不是只看平均 RT。
- **投机解码何时值得？** 瓶颈在逐 token 生成（decode）、草稿与终稿分布接近时。工具 RT 主导就先做超时与缓存。
