---
id: byte-wrong-patch-rollback
section: swe-agent
order: 190
level: A
title: 字节实习一面：错误 patch 怎么回滚、验证和再试？团队内部还要管哪些安全和审计？
quick: "每次尝试都绑定一个明确的基准 commit，测试红了就 `git checkout` 或丢掉 worktree 回到基准，再只带失败日志重新规划。做成团队内部工具时，靠运行时的命令白名单、路径沙箱、密钥扫描和全量审计日志来管，模型不能直接拿到生产凭据。"
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

这两问的答案都在 harness 里：每次尝试绑定一个明确的基准 commit，失败就把脏树整个丢掉，再带着失败日志重新规划；做成内部工具时，权限、沙箱和审计都是运行时策略，写在输入提示（prompt）里管不住，模型也不能直接拿生产凭据。「让模型再生成一次」或者「system prompt 里写不要改错文件」都答不到点上。

举个例子：Agent 改了 `utils.py` 之后两个测试变红，它接着又改 `models.py` 想补救，结果第三次尝试是在前两次的半成品上叠出来的，最后谁也说不清是哪一步改坏的。回滚的意义就是让每次尝试都从同一个干净起点出发。

## 回滚到基准，再根据失败证据重试

patch 应用之前先记下 tree / commit。测试红了就 `git checkout --`，或者直接丢掉 worktree 回到基准，不允许在半成功的改动上叠下一次补丁。并行尝试各用独立的 worktree，不共享工作区。基准要不可变，同一个 `attemptId` 对应同一个起点，这样审计时能查到「哪一次尝试改坏了什么」。

验证闭环是：应用 → 跑定向测试 → 通过了才允许下一张 patch，失败就回滚。测绿之后才允许 `git add`，Agent 不能在没验证的情况下直接 commit 到共享分支。

再试的时候，只把失败断言、相关 hunk 和最小复现命令送回模型。整仓再读一遍会增加 token 消耗，还会把无关文件带进下一轮上下文。

## 内部工具：沙箱、白名单、审计

可写目录限制在仓库和临时 workspace 里，禁止读 `.env`、密钥文件和同一台机器上的其他 repo。命令走策略引擎，白名单只放 `pytest` 和 `git` 的一个子集，禁止 `curl | sh`、禁止任意网络、禁止提权。密钥扫描放在观测结果（observation）出沙箱之前，命中了就脱敏，或者干脆不回传给模型。

审计日志至少要记下：谁、什么时候、对哪个 repo / commit、执行了什么命令、读写了哪些路径、测试结果、有没有回滚。这些都是 harness 的职责。鉴权按「人 + 仓库 ACL」来，Agent 的服务账号不能持有生产 deploy key。「谁能对哪个 repo 发起尝试」也要做成审批或组权限，免得任何同事都能对核心库连续打 patch。

## 追问

**回滚用 `git reset --hard` 可以吗？**
可以，前提是工作区里没有用户还没提交的合法改动。内部工具更稳的做法是每次尝试一个 worktree。

**失败日志整页塞回去行不行？**
别这样。只抽失败栈和相关断言，否则下一轮更贵也更噪，见 `byte-token-cost-debug`。

**Prompt 里写「禁止读 .env」够不够？**
不够，模型会忽略它。要在运行时拦截路径和命令。

**怎么证明没有泄密？**
审计日志里能检索出对敏感文件的访问；评测集里故意注入 `.env` 和云密钥路径，断言 observation 里没有明文。回滚日志也要能复盘每一次 attempt 的起点 commit。

相关：`byte-tool-fail-retry`、`moonshot-desktop-local-file-permission`、`agent-tool-permissions`
