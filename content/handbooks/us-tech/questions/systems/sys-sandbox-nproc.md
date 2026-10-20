---
id: sys-sandbox-nproc
section: systems
order: 69
level: A
title: 系统：沙箱除了超时，还要限制进程数、内存和磁盘
quick: "只限制实际耗时，挡不住 fork 把机器打满，也挡不住把磁盘写满。 进程数、地址空间、可写磁盘都要有上限。杀掉的是整个进程组，不是只杀一开始那个 PID。"
tags:
  - Sandbox
  - Post-train
realInterview: false
status: published
format: markdown
updatedAt: 2026-09-24
sources:
  - title: DeepSeekMath
    url: https://arxiv.org/abs/2402.03300
    type: primary
---

## 题怎么来的

`sys-sandbox` 写了网络、只读测试和超时。这道补资源上限。模型生成的程序可以在超时前把宿主机拖死。

## 三项

进程数：一个程序可以在一秒内 fork 出远超 CPU 核数的进程。上限设成个位数到几十，够测试框架拉起子进程，不够用来占满进程表。

内存：地址空间上限按这道题该有的量设，不要按整台机器的内存设。超了由内核杀掉，奖励记失败。不要等 OOM killer 去挑训练进程。

磁盘：可写目录有配额。程序可以生成巨大文件就算「在工作」。配额满了当成失败，目录照样删。

## 进程组

超时和超限时，向进程组发信号，而不是只向当初 spawn 的那个 PID。那个 PID 可以已经退出，子进程还在。沙箱用新的进程组或新的命名空间起进程，训练进程和它不在一组里，避免误杀训练。

这些限制在沙箱里生效。不要只在 Python 里 `try` 住 `MemoryError`。本机内存耗尽时，训练进程会先收到冲击。

## 代码

```python
import subprocess

def _limits():
    import resource
    resource.setrlimit(resource.RLIMIT_NPROC, (32, 32))
    resource.setrlimit(resource.RLIMIT_AS, (2 * 2**30, 2 * 2**30))
    resource.setrlimit(resource.RLIMIT_FSIZE, (64 * 2**20, 64 * 2**20))

def spawn(cmd):
    return subprocess.Popen(cmd, preexec_fn=_limits, start_new_session=True)
```

## 追问

**并行评很多条，上限怎么加？** 每条自己的上限，再加上这台机器上同时跑的沙箱个数。个数乘单条内存，要小于这台机器扣掉训练之后剩的内存。
