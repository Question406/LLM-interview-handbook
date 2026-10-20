---
id: stepfun-gpu-deadlock
section: systems
order: 183
level: A
title: 阶跃星辰：GPU 死锁是什么，训练里常见怎么踩到？
quick: >-
  一组 rank 互相等待对方的通信或同步，谁也无法前进。常见于 NCCL
  集合通信参与集合不一致、一边先卡在 CPU、显存分配在 collective
  前后顺序不同。排查看哪一 rank 没进入同一通信、是否有隐式同步和 OOM 重试。
tags:
  - StepFun
  - GPU
  - Deadlock
  - NCCL
realInterview: true
status: published
format: markdown
updatedAt: 2026-08-21
sources:
  - title: 阶跃星辰大模型算法实习面经 好难
    url: https://www.nowcoder.com/feed/main/detail/933afb27edd84b438682fd5bba95fbb3
    type: candidate-first-hand
---

## 真题记录

- 公司：阶跃星辰（StepFun）
- 团队 / 岗位：大模型算法实习
- 来源类型与可信度：牛客候选人原帖，B
- 原始措辞：**“GPU死锁是什么？”**

常见误区是：把 OOM、单卡 kernel 长尾或 NCCL 超时都叫死锁。死锁是循环等待：一组 rank 互相等对方的通信或同步，谁也无法前进，GPU 利用率掉到接近 0。训练里最常见的是集合通信契约破了：`allreduce` / `allgather` 要求全员到达，有一个 rank 走了不同分支，其余卡一直等。同面 DeepSpeed / BF16 已有卡，这题要落到「集体通信契约」，见 `sys-distributed-hang`。

## 集合通信死锁长什么样

`allreduce` 不是「谁先到谁先算完」，是栅栏。任一 rank 没进同一 collective，整个 group hang。诱因：

- data-dependent 控制流：有的 rank 因空 batch / 过滤提前 `return`，没进通信
- 只给一个进程打断点或 `print`+`input`，其余卡堵在 NCCL
- ZeRO-3 / 自定义算子的同步点不一致，有的 rank 先 all-gather、有的还在 host 分配
- 显存分配在 collective 前后顺序不同，一 rank OOM 重试、另一 rank 已进通信

NCCL 超时看起来像 hang，根因可能是死锁，也可能是慢或掉网。先分清「没进去」还是「进去了极慢」。

## 和 OOM、慢怎么对比

| | 死锁 | OOM | 长尾慢 |
| --- | --- | --- | --- |
| 现象 | 多卡互相等，利用率掉到 0 | 某 rank 分配失败 | GPU 仍在算，step 时间长 |
| 推进 | 谁都不动 | 进程可能退出 | 还能往前 |
| 关键证据 | 各 rank 卡在不同调用栈 | allocator 报错 | kernel / 通信耗时 |

排查看：哪个 rank 没进入同一通信、是否有隐式同步（CPU allocator、打印锁）、OOM 重试是否插在 collective 中间。NCCL 日志里的 `Timeout` 只说明等太久，要用每 rank 的调用栈对齐到同一个 op 名和同一个 `seq`，才能判断是没进去还是进去了极慢。

## 追问

- **单卡会不会死锁？** 单卡自己和自己一般不构成分布式死锁；多流 + 事件环等待少见。面试默认答多卡 collective。
- **dynamic sampling 的 filter 带随机会怎样？** 不同 rank 丢掉不同组，下一步 collective 参与数不一致，见 `slime-dynamic-partial`。
- **NCCL timeout 等于死锁吗？** 不等于。先看调用栈是否卡在同一 op，再看网络和 straggler。
- **怎么避免？** 控制流跨 rank 一致，collective 前后不要插可能失败的分配，调试不要只挂一个进程。
- **ZeRO-3 为什么更容易踩？** 每层都有 AG/RS，同步点比普通 DP 密得多，自定义 hook 漏一个 rank 就会挂，见 `sys-zero`。
