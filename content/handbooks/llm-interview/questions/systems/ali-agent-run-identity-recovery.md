---
id: ali-agent-run-identity-recovery
section: systems
order: 102
level: S
title: 淘天 Agent：配置哈希、重试与断线重连的执行身份怎样设计？
quick: "我会把配置身份和每次真正跑起来的 attempt 拆开：配置哈希只当缓存和去重的键，attempt 用 UUID 标识这一次运行，外部任务带幂等键和查询句柄。断线了就按持久化事件和外部服务的状态重连原任务，用户点重新运行才开新 attempt，旧结果不去改。"
tags:
  - Alibaba
  - Agent Runtime
  - Idempotency
  - Recovery
realInterview: true
status: published
format: markdown
updatedAt: 2026-08-21
sources:
  - title: 阿里淘天Agent开发一面凉经分享 1h（候选人原帖）
    url: https://www.nowcoder.com/feed/main/detail/1c41860071f342d287177a5e5085c9c0?sourceSSR=post
    type: candidate-first-hand
---

## 真题记录

- 公司：阿里巴巴淘天
- 团队 / 岗位：Agent 开发
- 届别 / 流程：原帖未披露；一面，约 1 小时
- 面试时间：原帖未披露；帖子发布时间仅显示 04-23，年份未披露
- 来源类型与可信度：牛客候选人原帖，B（公司、岗位与轮次明确，届别和年份未披露）
- 原始措辞：**“同一份配置算出来的哈希是不是固定的？什么情况下会用同一个哈希再次触发 Jenkins？”**

同一份规范化配置算出来的哈希应该是固定的，但它只能当缓存键，一次执行的身份要另外用 `runId` / `attemptId` 表示。相同哈希可能有三种走法：命中缓存、重连正在进行的构建、用户显式 rerun 时开新 attempt，这三条路要分开处理。

最常见的错法有两种：把 content hash 当成一次执行的主键，或者把网络重试和用户点「重新运行」混成同一次副作用。举个例子，客户端提交构建后断线了，重连时又提交了一份一模一样的 YAML。如果系统只认哈希，它要么以为是同一次、直接复用一个还没跑完的结果，要么当成新请求又打一次 Jenkins，两种都不对。

所以哈希只表示「期望的输入」。创建任务时生成 `runId`，每次运行生成 `attemptId`；提交 Jenkins 时带上 `attemptId` 或幂等键，并把 queue / build URL 持久化下来。客户端断线后凭这个句柄去查，别再提交一份相同的 YAML 打一次构建。哈希不稳定通常是因为时间戳没规范化、map 无序、用了绝对路径，所以先把规范化规则定死，再谈去重。

同哈希再来一次请求时，我这样判断。execution 还在跑，就先查询、重连原任务，不并行再开一条 Jenkins。已经成功的结果能不能复用，看输入、权限、工具和环境版本是否仍然有效；失败或状态未知的，绝不当成功。用户点「重新运行」时绕开 result cache，开新的 `attemptId`，但对**同一个 attempt 的提交**仍然做幂等，免得超时重试打出两次副作用。会话断开后，客户端从 event log 恢复，服务端用 Jenkins API 核实 build 状态，本地内存里那句「进行中」不可信。

恢复靠一条持久事件流，记录已提交、queue id、build url、终态和产物指针。Reattach 只做只读对齐，只有明确的新 attempt 才允许再触发有副作用的 job。部分成功（比如测过一半）不能改写成全成功。还有一种情况是配置哈希没变，但密钥轮换了或者镜像升级了，这时旧的成功缓存要失效，否则会复用一个在当前环境下已经复现不了的成功结果。Jenkins 在这里只是一个有副作用的 provider，换成 K8s Job 也是同一套身份设计。

## 追问

**哈希是固定的吗？**
同一份规范化后的输入应该固定。没规范化的字段会让去重失效。

**什么情况下会用同一个哈希再触发 Jenkins？**
三种：用户显式 rerun；旧结果已经不可信，比如环境变了；或者之前从来没成功提交过。任务还在进行中就 reattach。

**幂等键放在哪？**
放在对 Jenkins 或外部系统的提交上，键里要包含 `attemptId`，别只用 config hash。

**状态未知怎么办？**
先查 provider。查不到就标 unknown 并告警，不能当成功写进缓存。

相关：`sys-agent-canary-rollback`、`byte-wrong-patch-rollback`
