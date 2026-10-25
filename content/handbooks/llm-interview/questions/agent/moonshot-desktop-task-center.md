---
id: moonshot-desktop-task-center
section: agent
order: 103
level: S
title: 月之暗面：设计桌面 Agent 任务中心时应有哪些关键对象？
quick: "以可恢复的 Task 为中心，建模目标和约束、步骤、每次运行尝试、输入证据、工具调用、产物版本、权限决策和 checkpoint，每个对象有稳定 ID、状态机和时间戳。重试开新 Attempt，恢复从 checkpoint 继续，编辑产物生成新版本。UI 只是这些状态的投影，让用户知道正在等谁、哪里失败、怎样恢复。"
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

我会先报对象和状态机，再谈 UI。桌面 Agent 会改文件、调工具、等用户确认，任务中心的核心实体是可恢复的 `Task` 和它可审计的运行图，做成一串聊天消息的列表撑不住。没有稳定的对象，重试会覆盖旧证据，恢复会丢副作用，产物护栏也无处可挂，见 `moonshot-desktop-result-guardrails`。

举个场景：Agent 在整理一个项目目录，跑到一半改了几个文件，然后停下来等用户确认要不要删除旧草稿，这时用户关了窗口。下次打开，任务中心要能说清：这个任务停在哪个 Step，已经改了哪些文件、各自对应哪次工具调用，现在在等用户确认什么。如果只有聊天记录，任务中心只能显示「思考中」，用户不知道发生过什么。

要显式建模的对象至少有：目标和用户约束、Plan / Step、每次 `Attempt`、输入 artifacts / evidence、模型调用、工具调用、权限决策、产物及其版本、checkpoint、日志和评价结果。每个实体有稳定 ID、创建者、输入输出引用、状态机和时间戳。`Task` 可以处于 queued、running、waiting-for-user、paused、failed、completed。权限决策要单独成对象，在输入提示（prompt）里写「请注意权限」不算数，见 `moonshot-desktop-local-file-permission`。多窗口时同一个 Task 可能被几个视图投影，状态源只能有一份，见 `moonshot-desktop-multiwindow-state`。多模态选区和本地目录授权也挂在同一个 Task 上，别散落在各窗口的临时 state 里。

这样拆，是因为重试、恢复、编辑三件事要分开处理。重试生成新的 Attempt，不覆盖旧证据和旧产物；恢复从 checkpoint 继续，重放必要的上下文，不用从头再聊一遍；用户编辑产物形成新版本，并让下游依赖失效。三件事都塞进「再发一条消息」，审计和回滚都会糊掉。写文件、外发、删除这些副作用，必须能从工具调用记录反查。

UI 显示运行图里有用的那部分：当前在等谁（模型、工具还是用户）、下一步会做什么、发生过哪些副作用、哪里能确认、取消或回滚。只放一个进度条不够。失败时把失败对象指到具体的 Step 或工具调用，别让整条 Task 变红。产物质量闸门挂在 Artifact 版本上，见 `moonshot-desktop-result-guardrails`。聊天丢了上下文，可以再问一句；桌面任务一旦写过盘，UI 就必须能指到那次工具调用和那份产物版本。评测看恢复成功率、误覆盖次数，以及用户能不能在三步内找到「刚才改了哪个文件」。

## 追问

**只用 session 消息为什么不够？**
消息没有状态机和副作用记录，重试会丢证据，恢复时也没法重放工具结果。

**checkpoint 存什么？**
存可执行状态：当前 Step、已确认的约束、产物版本句柄、权限 capability。整段聊天原文不用存。

**用户中途改目标怎么办？**
让旧 Plan 失效，开新的 Attempt，旧的图保留下来供审计。不要原地改正在跑的 Step。

**和产物护栏怎么接？**
护栏检查的是 Artifact 版本，任务中心负责展示检查结果并卡住发布，见 `moonshot-desktop-result-guardrails`。
