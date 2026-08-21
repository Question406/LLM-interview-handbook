---
id: ali-agent-run-identity-recovery
section: systems
order: 102
level: S
title: 淘天 Agent：配置哈希、重试与断线重连的执行身份怎样设计？
quick: >-
  将不可变的配置身份与每次执行的 attempt ID 分离：配置哈希用于缓存和去重，attempt 用 UUID 表示一次真实运行；
  外部任务携带幂等键和状态查询句柄。断线后以持久事件和 provider 状态 reattach，显式 rerun 产生新 attempt 而非篡改旧结果。
tags:
  - Alibaba
  - Agent Runtime
  - Idempotency
  - Recovery
realInterview: true
status: published
format: markdown
updatedAt: 2026-08-19
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

淘天 Agent 开发一面这题，最容易把 content hash 当成一次执行的主键，或把网络重试和用户「重新运行」混成同一次副作用。面试要听的是身份分层：规范化配置得到稳定哈希，用来做缓存键；真正跑起来的是 `runId` / `attemptId`。相同哈希可以命中缓存、附着进行中的 build，或在显式 rerun 时开新 attempt，三者必须分支清楚。Jenkins 只是一个有副作用的 provider，换成 K8s Job 也是同一套身份。

## 配置哈希是缓存键，不是执行 ID

规范化后的同一份配置应生成稳定 content hash，但它是「期望输入」而不是一次运行的唯一标识。创建任务时生成 `runId`，每次运行生成 `attemptId`；提交 Jenkins 时传递 `attemptId` 或幂等键，并持久化 queue / build URL。这样客户端断线后能凭句柄查询，而不是再提交一份相同 YAML 就再打一次构建。哈希不稳定通常来自未规范化的时间戳、无序 map、绝对路径；先固定规范化规则，再谈去重。

## 同哈希再触发：查询、复用、显式 rerun

判断必须显式化：相同哈希且 execution 正在进行 → 先查询并 reattach，不要并行再开一条 Jenkins；同 hash 的成功结果是否复用，取决于输入、权限、工具和环境版本是否仍有效；失败或未知状态绝不假装成功。用户点「重新运行」时绕开 result cache，开新 `attemptId`，但仍对**同一个 attempt 的提交**做幂等，避免超时重试触发两次副作用。会话断开后客户端从 event log 恢复，服务端以 Jenkins API 核实 build 状态，而不是相信本地内存里的「进行中」。

## 断线恢复与副作用边界

持久事件流记录：已提交、queue id、build url、终态、产物指针。Reattach 是只读对齐；只有明确的新 attempt 才允许再触发有副作用的 job。部分成功（测过一半）不能改写成全成功。配置哈希相同但密钥轮换、镜像升级时，旧成功缓存要失效，否则会复用不可复现的绿。相关卡：`sys-agent-canary-rollback`、`byte-wrong-patch-rollback`。

## 追问

- **哈希固定吗？** 同一规范化输入应当固定；未规范化字段会让去重失效。
- **什么情况下同哈希再触发 Jenkins？** 显式 rerun、旧结果不可信（环境变了）、或从未成功提交过；进行中应 reattach。
- **幂等键放哪？** 放在对 Jenkins / 外部系统的提交上，键含 `attemptId`，不要只用 config hash。
- **未知状态怎么办？** 先查 provider；查不到就标 unknown 并告警，不要当成功缓存。
