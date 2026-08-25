---
id: moonshot-desktop-local-file-permission
section: agent
order: 101
level: S
title: 月之暗面：桌面 Agent 接入本地文件与目录，权限提示怎样设计？
quick: >-
  把“选择文件”与“授权给 Agent 做什么”分开：在执行前展示资源范围、动作、副作用和有效期；运行时由
  capability 校验，而非只靠提示词。对递归目录、外发和写删除操作要升级确认，并提供可撤销审计记录。
tags:
  - Moonshot AI
  - AI-Native
  - Agent Security
  - Local Files
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
- 届别 / 流程：原帖未披露；一面
- 面试时间：2026-07-23；帖子发布于 2026-07-30
- 来源类型与可信度：牛客候选人原帖，B（公司、岗位、轮次与面试日期明确，届别未披露）
- 原始措辞：**“桌面 AI 产品接入本地文件和目录时，前端如何设计权限提示？”**

这块容易直接答成：首次选文件时弹一个「允许访问磁盘」就结束。桌面 Agent 的权限提示是授权 UX，不是系统对话框复读。月之暗面一面要前端在模型发起具体工具调用前，讲清范围、动作、副作用和有效期。选择文件 $\neq$ 授权 Agent 递归读取、上传云端或删除。运行时必须用 capability 校验，System Prompt「请不要乱删」不是权限系统。通用工具权限见 `agent-tool-permissions`。

## 授权对象拆开：主体、资源、动作、时效

提示至少让用户看懂四件事：谁（本会话的哪个 Agent / 任务）、碰什么（路径、是否递归、文件类型）、做什么（读 / 写 / 删 / 外发）、多久（本次任务 / 一次性 / 直到撤销）。例如：「报告 Agent 可读取此文件夹下 `.md`，至任务结束；不会上传；不会删除」。用户能缩小范围、拒绝、改成一次性。

风险分级：单文件只读 $\lt$ 目录只读 $\lt$ 递归目录 $\lt$ 外发 / 上传 $\lt$ 覆盖写入 $\lt$ 删除。后几档二次确认，写删除显示 dry-run 或 diff。不要在「打开文件夹」时预授权删除。多窗口协作时授权属于任务真相，不能每个窗口各记一份互相覆盖，见 `moonshot-desktop-multiwindow-state`。

## 前端提示必须落到 capability，并可撤销

执行端用 allowlist 实施：路径前缀、操作动词、是否允许网络。模型请求超出授权直接拒，并回写给任务中心，而不是改 prompt 再试。每次访问记可回看审计：时间、路径、动作、是否经用户确认。任务中途可撤销余下权限，重试或分支不得悄悄扩大访问面。任务对象模型见 `moonshot-desktop-task-center`。

多模态里截图和网页另算资源，不能因为用户贴了一张图就默认可读整个桌面，见 `moonshot-desktop-multimodal-context`。恶意文件内容仍可能 prompt injection，权限再小也要隔离工具描述与不可信文本，见 `agent-prompt-injection`、`agent-skill-security`。最后我会补一句：提示是授权协商，校验在运行时，审计可撤销。前端文案要避免系统权限那套「允许访问文件」，用户听不懂 Agent 接下来会读几层目录、会不会上传。改用任务语言：「为了写周报，将读取你选中的 3 个 Markdown，不会上传，不会修改」。若模型中途要扩大范围，弹出的是增量授权，而不是再来一次全盘允许。Desktop 产品的信任建立在可预期的访问面上，提示失败等于权限模型失败。

## 追问

- **系统文件选择器算不算权限提示？** 只完成「选了哪些路径」。还必须展示动作、外发、时效，并在每次升级风险时再确认。
- **用户勾了「记住我的选择」安全吗？** 只能记住同级或更低风险；写删除和外发不得被「记住」跨任务复用。
- **Agent 重试时要不要再弹？** 同一 capability 内可读重试可静默；路径或动作升级必须再授权。
- **为什么不能只靠 Prompt？** 模型会被文件内容和工具描述诱导。没有 OS / 主进程级校验，越权一旦发生不可追回。
