---
id: swe-multi-worktree-patch-merge
section: swe-agent
order: 192
level: A
title: 多 worktree 并行改同一仓库时，Agent 如何合并 patch 并处理冲突？
quick: 每任务独立 worktree/分支；合并用变基或三路合并，冲突处保留意图元数据交裁决策略；禁止未隔离时并行写同一工作区。
tags:
  - Worktree
  - Patch Merge
  - SWE Agent
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-21
sources:
  - title: Git worktree documentation
    url: https://git-scm.com/docs/git-worktree
    type: primary
---

多个修复假设并行跑，却共用一个工作区，是 SWE Agent 最常见的文件系统事故：A 的半成品被 B 覆盖，测试绿的是混叠状态，提交却只带了其中一个 diff。错法：「我们用了线程」或「最后 git stash 一下」。Git worktree 的设计就是给同一仓库多个检出目录，每个绑定独立分支。Agent 应把每个假设放到自己的 worktree，而不是在同一 `cwd` 里抢写。合并用变基或三路合并，冲突处保留意图元数据交给裁决策略；禁止未隔离时并行写同一工作区。

## 隔离是前提，不是优化

每个 attempt：独立 worktree、独立分支、独立测试进程、独立临时目录。共享的只有只读对象库。禁止并行 `git checkout` 同一 worktree，也禁止两个 Agent 写同一未跟踪文件。假设探索可以宽（补丁 A / B / C），但文件系统状态必须分叉。记录：worktree 路径、基 SHA、分支、该假设跑过的测试证据。没有证据包，合并时只能看 diff 大小，会留下「看起来小但测没跑过」的补丁。磁盘配额按 worktree 计，避免并行把磁盘打满后所有假设一起失败。

## 合并顺序、冲突与回滚

合并顺序不按完成时间，按：测试通过 $\gt$ 依赖方向（先底层 API 再调用方）$\gt$ 冲突面更小。对每个候选做三路合并到集成分支；冲突文件不要静默取 union。冲突块附意图元数据：哪个假设、要修哪条失败测试、证据摘要。裁决可以是规则（允许列表路径不重叠则自动并）或再开子 Agent 只解决冲突文件，但子 Agent 仍在新 worktree 里验证。路径重叠且语义冲突时，保留测试更强的一侧，另一侧回滚，而不是手工拼到「两边测试各过一半」。集成后再跑并集测试；只跑各自子集，假绿会在合并后爆。

评测上能刷的是：串行假装并行；冲突时 `git checkout --ours`；合并后不跑测试；用同一 `node_modules` 跨 worktree。并行的是假设，不是工作区。Git worktree 文档强调的就是附加检出与分支绑定；你要加的是测试证据和冲突意图，而不是新的合并算法。现场能讲「两个 Agent 同时改同一文件时谁赢」，答案应是带证据的裁决加回滚，而不是时间戳。

回滚粒度是假设不是文件：整个 attempt 的 patch 可关，避免留下半套 API。日志能回答「集成分支上每一 hunk 来自哪个 worktree、当时哪些测试绿」。没有这张表，出事只能 reset 到很早的基线。并行度受磁盘与 CPU 配额约束：worktree 数 $w$ 满足 $w\cdot \mathrm{disk}_i \lt Q$，超了应排队而不是共享目录「省空间」。两个假设改同一符号时，先比测试证据强度，再比 diff 大小；证据不足的一侧整包回滚。

## 追问

- **为什么不能共用工作区加锁文件？** 锁防的是同时写，防不了半成品可见与未跟踪文件互踩；检出隔离更干净。
- **变基还是 merge？** 线性历史用 rebase 便于回滚单假设；已共享的集成分支用三路 merge，避免重写他人 SHA。
- **冲突能否按行自动并？** 路径不重叠可以；同一符号两侧都改必须带测试证据再裁，禁止文本 union。
- **子 Agent 解决冲突要不要新 worktree？** 要。否则又回到共享 `cwd` 的原问题。
