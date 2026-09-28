---
id: moonshot-desktop-task-center
section: agent
order: 103
level: S
title: 月之暗面：设计桌面 Agent 任务中心时应有哪些关键对象？
quick: >-
  以可恢复的 Task 为中心，显式建模目标、计划/步骤、运行 attempt、输入证据、工具调用、产物、权限决策和
  checkpoint；每个对象都带稳定 ID、状态机、版本与时间线。UI 只是这些可审计状态的投影。
tags:
  - Moonshot AI
  - AI-Native
  - Agent Runtime
  - Task Center
realInterview: true
status: published
format: markdown
updatedAt: 2026-08-21
sources:
  - title: 月之暗面 Desktop 研发工程师面经（候选人原帖）
    url: https://www.nowcoder.com/feed/main/detail/09158c1da13b420bbe00ba1751177efb?urlSource=sitemap
    type: candidate-first-hand
---
## 真题记录

- 公司：月之暗面（Moonshot AI）
- 团队 / 岗位：研发工程师（AI-Native 方向）
- 届别 / 流程：原帖未披露；二面
- 面试时间：2026-07-23；帖子发布于 2026-07-30
- 来源类型与可信度：牛客候选人原帖，B（公司、岗位、轮次与面试日期明确，届别未披露）
- 原始措辞：**“如果让你设计桌面 Agent 的任务中心，会有哪些关键对象?”**

错法：把任务中心做成聊天记录列表。桌面 Agent 会改文件、调工具、等用户确认，核心实体不是一串消息，而是可恢复的 `Task` 及其可审计运行图。没有稳定对象，重试会覆盖旧证据、恢复会丢副作用、产物护栏也无处可挂，见 `moonshot-desktop-result-guardrails`。先报对象和状态机，再谈 UI。

## 关键对象：Task 及其运行图

至少显式建模：目标和用户约束、Plan / Step、每次 `Attempt`、输入 artifacts / evidence、模型调用、tool call、权限决策、产物及其版本、checkpoint、日志和评价结果。每个实体有稳定 ID、创建者、输入输出引用、状态机和时间戳。`Task` 可处于 queued、running、waiting-for-user、paused、failed、completed。权限决策要单独成对象，不能写进 prompt「请注意权限」，见 `moonshot-desktop-local-file-permission`。多窗口时同一 Task 可能被多个视图投影，状态源只能有一份，见 `moonshot-desktop-multiwindow-state`。

## 为什么这样拆：重试、恢复、编辑

三个常见问题必须分开处理。重试生成新 Attempt，不覆盖旧证据和旧产物。恢复从 checkpoint 继续，并重放必要上下文，别从头再聊一遍。用户编辑产物形成新版本，并使下游依赖失效。把这三件事都塞进「再发一条消息」，审计和回滚都会糊。副作用（写文件、外发、删除）必须能从 tool call 记录反查，否则任务中心只能显示「思考中」，用户不知道发生了什么。

## UI 只是可审计状态的投影

前端任务中心显示 execution graph 的有用切片：当前正在等谁（模型、工具、用户）、下一步会做什么、发生过哪些副作用、哪里能确认 / 取消 / 回滚。不要只显示进度条。失败时把失败对象指到具体 Step / tool call，别整条 Task 变红。产物质量闸门挂在 Artifact 版本上，见 `moonshot-desktop-result-guardrails`。评测看恢复成功率、误覆盖次数和用户能否在三步内找到「刚才改了哪个文件」。聊天可以丢上下文再问一句；桌面任务一旦写过盘，UI 必须能指向那次 tool call 和那份产物版本。多模态选区、本地目录授权也应挂在同一 Task 上，别散落在各窗口的临时 state。

## 追问

- **为什么不能只用 session 消息？** 消息没有状态机和副作用记录，重试会丢证据，恢复无法重放工具结果。
- **checkpoint 存什么？** 可执行状态：当前 Step、已确认约束、产物版本句柄、权限 capability，而不是整段聊天原文。
- **用户中途改目标怎么办？** 使旧 Plan 失效，开新 Attempt，保留旧图供审计，不要原地改正在跑的 Step。
- **和产物护栏怎么接？** 护栏检查的是 Artifact 版本，任务中心负责展示检查结果并卡住发布，见 `moonshot-desktop-result-guardrails`。
