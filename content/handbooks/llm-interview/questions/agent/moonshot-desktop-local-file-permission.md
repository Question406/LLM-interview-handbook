---
id: moonshot-desktop-local-file-permission
section: agent
order: 101
level: S
title: 月之暗面：桌面 Agent 接入本地文件与目录，权限提示怎样设计？
quick: >-
  把「选择文件」和「授权 Agent
  做什么」分开：执行前用任务语言讲清资源范围、动作、副作用和有效期，用户可以缩小或拒绝。递归目录、外发、覆盖写和删除要升级确认，中途扩大范围弹增量授权。运行时由
  capability 校验，并留可撤销的审计记录，光靠 prompt 约束不了模型。
tags:
  - Moonshot AI
  - AI-Native
  - Agent Security
  - Local Files
realInterview: true
status: published
format: markdown
updatedAt: 2026-08-21T00:00:00.000Z
sources:
  - title: 月之暗面 Desktop 研发工程师面经（候选人原帖）
    url: >-
      https://www.nowcoder.com/feed/main/detail/09158c1da13b420bbe00ba1751177efb?urlSource=sitemap
    type: candidate-first-hand
---

## 真题记录

- 公司：月之暗面（Moonshot AI）
- 团队 / 岗位：研发工程师（AI-Native 方向）
- 届别 / 流程：原帖未披露；一面
- 面试时间：2026-07-23；帖子发布于 2026-07-30
- 来源类型与可信度：牛客候选人原帖，B（公司、岗位、轮次与面试日期明确，届别未披露）
- 原始措辞：**“桌面 AI 产品接入本地文件和目录时，前端如何设计权限提示？”**

我会把权限提示做成一次授权协商：在模型发起具体工具调用之前，让用户看懂这个 Agent 要碰哪些文件、做什么、有没有副作用、授权到什么时候。用户在系统选择器里选了文件，只说明选了哪些路径，选择文件 $\neq$ 授权 Agent 递归读取、上传云端或删除。首次选文件时弹一个「允许访问磁盘」就结束，是最常见的误区，复读一遍系统对话框也算不上授权 UX。拦住越权要靠运行时的 capability 校验，System Prompt 里写「请不要乱删」算不上权限系统。

文案要用任务语言。比如：「为了写周报，将读取你选中的 3 个 Markdown，不会上传，不会修改。」或者「报告 Agent 可读取此文件夹下 `.md`，至任务结束；不会上传；不会删除。」系统权限那套「允许访问文件」用户听不懂，他不知道 Agent 接下来会读几层目录、会不会上传。

提示里至少讲清四件事：谁（本会话的哪个 Agent、哪个任务），碰什么（路径、是否递归、文件类型），做什么（读、写、删、外发），多久（本次任务、一次性、直到撤销）。用户可以缩小范围、拒绝，或者改成一次性。风险按档位升级：单文件只读 $\lt$ 目录只读 $\lt$ 递归目录 $\lt$ 外发 / 上传 $\lt$ 覆盖写入 $\lt$ 删除。后面几档要二次确认，写和删要展示 dry-run 或 diff；用户「打开文件夹」时，不能顺手预授权删除。模型中途要扩大范围，就弹增量授权，别再来一次全盘允许。

前端提示要落到执行端的 capability 上。执行端用 allowlist 实施：路径前缀、操作动词、是否允许网络。模型请求超出授权就直接拒绝，并回写给任务中心，换一段 prompt 再试也绕不过去。每次访问记一条可回看的审计：时间、路径、动作、是否经过用户确认。任务中途可以撤销剩下的权限，重试或分支也不能悄悄扩大访问面。任务对象怎么建模见 `moonshot-desktop-task-center`；多窗口协作时，授权属于任务真相，不能每个窗口各记一份、互相覆盖，见 `moonshot-desktop-multiwindow-state`。

还有两类 access restrictions。多模态输入里，截图和网页另算资源，用户贴了一张图，不等于默认可读整个桌面，见 `moonshot-desktop-multimodal-context`。恶意文件的内容仍然可能做 prompt injection，权限再小，也要把工具描述和不可信文本隔开，见 `agent-prompt-injection`、`agent-skill-security`。通用的工具权限设计见 `agent-tool-permissions`。

## 追问

**系统文件选择器算不算权限提示？**
它只完成了「选了哪些路径」。动作、外发和时效还要另外展示，每次风险升级都要再确认。

**用户勾了「记住我的选择」，安全吗？**
只能记住同级或更低风险的授权。写、删和外发不能被「记住」后跨任务复用。

**Agent 重试时要不要再弹？**
在同一个 capability 内的可读重试可以静默；路径或动作升级了，必须重新授权。

**只靠 Prompt 为什么不行？**
模型会被文件内容和工具描述诱导。没有 OS 或主进程级的校验，越权一旦发生就追不回来。
