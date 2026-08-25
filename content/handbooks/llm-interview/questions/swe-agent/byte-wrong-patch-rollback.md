---
id: byte-wrong-patch-rollback
section: swe-agent
order: 190
level: A
title: 字节实习一面：错误 patch 怎么回滚、验证和再试？团队内部还要管哪些安全和审计？
quick: >-
  每次尝试基于明确基准 commit，失败就 `git checkout` / worktree
  丢弃，再带测试失败日志重规划。上线成内部工具时：命令白名单、路径沙箱、密钥扫描、全量审计日志。模型不能直接拿生产凭据。
tags:
  - ByteDance
  - Patch
  - Security
realInterview: true
status: published
format: markdown
updatedAt: 2026-08-21
sources:
  - title: 字节实习 agent开发一面
    url: https://www.nowcoder.com/feed/main/detail/075c06bf50a143a785c039f9951624f6
    type: candidate-first-hand
  - title: SWE-agent
    url: https://arxiv.org/abs/2405.15793
    type: primary-paper
---

## 真题记录

- 公司：字节跳动
- 岗位：Agent 开发实习；一面
- 来源类型与可信度：牛客候选人原帖，A
- 原始措辞：**“如果 Agent 在执行代码修改时生成了错误 patch，你怎么做回滚、验证和再尝试？”**；**“如果让你把这个本地 Coding Agent 做成团队内部工具，你会怎么处理权限、安全和审计？比如文件读写、命令执行、敏感信息泄露。”**

字节 Agent 开发一面这题，这块容易答成「让模型再生成一次」或「system prompt 里写不要改错文件」。我会讲 harness：每次尝试钉在明确基准 commit 上，失败就丢掉脏树，再带失败日志重规划。做成内部工具时，权限、沙箱和审计是运行时策略，不是 prompt。模型不能直接拿生产凭据。相关卡：`byte-tool-fail-retry`、`moonshot-desktop-local-file-permission`。

## 回滚与再试：脏树上禁止叠幻觉

patch 应用前记录 tree / commit。测试红了就 `git checkout --` 或丢掉 worktree，回到基准，禁止在半成功改动上叠下一次补丁。再试只把失败断言、相关 hunk 和最小复现命令送回模型，不要整仓再读一遍，那会把 token 和无关文件一起送进下一轮幻觉。验证闭环是：应用 → 定向测试 → 通过才允许下一张 patch；失败即回滚。并行尝试用独立 worktree，不要共享工作区。基准要不可变：同一 `attemptId` 对应同一起点，方便审计「哪一次尝试改坏了什么」。测绿之后才允许 `git add`；Agent 不得在未验证时直接 commit 到共享分支。

## 内部工具：沙箱、白名单、审计

可写目录限制在仓库与临时 workspace；禁读 `.env`、密钥文件和同机其他 repo。命令走策略引擎：白名单 `pytest` / `git` 子集，禁 `curl | sh`、禁任意网络、禁提权。密钥扫描放在 observation 出沙箱之前，命中则脱敏或拒绝回传模型。审计日志至少包含：谁、何时、对哪条 repo / commit、执行了什么命令、读写了哪些路径、测试结果、是否回滚。这是 harness 职责。鉴权按人 + 仓库 ACL，Agent 服务账号不能持有生产 deploy key。内部工具还要把「谁能对哪条 repo 发起尝试」做成审批或组权限，避免任意同事对核心库连打 patch。相关卡：`agent-tool-permissions`。

## 追问

- **回滚用 `git reset --hard` 可以吗？** 可以，但前提是工作区里没有用户未提交的合法改动；内部工具更稳妥的是 per-attempt worktree。
- **失败日志整页塞回去？** 不要。只抽失败栈和相关断言，见 `byte-token-cost-debug`，否则下一轮更贵也更噪。
- **Prompt 里写「禁止读 .env」够不够？** 不够。模型会忽略；要在运行时拦截路径和命令。
- **如何证明没有泄密？** 审计里可检索敏感文件访问；评测集注入 `.env` / 云密钥路径，断言 observation 不含明文。回滚日志要能复盘每一次 attempt 的起点 commit。
