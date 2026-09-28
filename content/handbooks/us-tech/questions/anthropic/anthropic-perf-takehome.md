---
id: anthropic-perf-takehome
section: anthropic
order: 26
level: A
title: Anthropic：开源的性能 take-home，是一台 VLIW SIMD 机器
quick: >-
  官方仓库 anthropics/original_performance_takehome 是旧版限时作业，不是现在仍在发的那一版。
  目标是把一个标量核改成更少的周期。一条指令是多个引擎的槽，写在周期结束才生效。多核在这版里是关掉的。
tags:
  - Anthropic
  - Coding
  - Performance
realInterview: false
status: published
format: markdown
updatedAt: 2026-09-24
sources:
  - title: anthropics/original_performance_takehome
    url: https://github.com/anthropics/original_performance_takehome
    type: primary
  - title: Machine class in problem.py
    url: https://github.com/anthropics/original_performance_takehome/blob/main/problem.py
    type: primary
---

## 题怎么来的

这不是某一次 onsite 的泄漏脚本。Anthropic 把早先的性能 take-home 放在 GitHub 上。README 写明：最初是 4 小时；Claude Opus 4 超过多数人之后改成 2 小时，起点已经是 18532 个周期，大约比仓库里这份慢起点快 7.97 倍；Opus 4.5 之后限时作业又换了底座。仓库是「新指令和调试工具，加上最慢的那份起点」。现在招聘发的不是这一份。`realInterview: false`。

验收是 `python tests/submission_tests.py` 打出的周期数。`tests/` 必须和 `origin/main` 一致，`git diff origin/main tests/` 应为空。

## 机器

一条指令是一个字典，键是引擎，值是该引擎本周期要执行的槽。示例是 `valu` 里两条算术，同时 `load` 一条。每个引擎有 `SLOT_LIMITS`。效果在周期结束才写回：本周期所有槽先读旧值，再一起写。所以同一周期里用「自己刚写的地址」当输入，读到的是旧值。

内存和 scratch 都是 32 位字。scratch 兼寄存器、常量和手管的缓存。SIMD 的 `vload` / `vstore` 只能搬连续的 `VLEN` 个元素，不能 gather 任意下标。标量要先 `vbroadcast` 再进 `valu`。

仓库自带的 `KernelBuilder.build` 默认一个 bundle 只放一个槽。标量核是对的、很慢。加速是把独立的 load、alu、valu、flow 填进同一条指令，并让连续地址走向量槽。

## 不要改的开关

`problem.py` 里有多核。README 专门写了一种错误优化：模型发现多核没加速，就去改 `N_CORES = 1`。这版多核是故意关掉的。周期下降若来自改模拟器或改测试，提交测试不会认。

调试用 `flow` 的 `pause` 和 `debug` 引擎。提交用的模拟器忽略 debug。`pause` 要和参考核的 yield 对齐，否则本地对照会错位；提交端不看这些 pause。

## 追问

**先向量化还是先打包槽？** 先让标量结果和参考核一致，再把内层循环改成 `vload` 加 `valu`。槽打包不改变结果，只减少周期。两条一起改，对不上时不知道是打包读了旧值，还是向量下标错了。

**同一周期的依赖怎么排？** 生产者和消费者不能放进同一条指令。中间值留在 scratch，下一条再用。周期结束才写回，就是为了让你显式排出这条依赖。
