---
id: sys-sandbox-nproc
section: systems
order: 69
level: A
title: 系统：沙箱除了超时，还要限制进程数、内存和磁盘
quick: 沙箱要同时限制进程数、内存、可写磁盘和实际耗时，超时或超限后清理整个进程组。否则程序可能在超时前 fork 大量子进程、耗尽内存或写满磁盘，拖垮宿主机。
tags:
  - Sandbox
  - Post-train
realInterview: false
status: published
format: markdown
updatedAt: 2026-09-24T00:00:00.000Z
sources:
  - title: DeepSeekMath
    url: 'https://arxiv.org/abs/2402.03300'
    type: primary
---

沙箱除了超时，还要限制进程数、内存和可写磁盘，并在结束时清掉整个进程组。程序可能在一秒内 fork 出远超 CPU 核数的进程，等到超时才处理，宿主机已经被占满。network access 和 read-only test permissions 见 `sys-sandbox`，这里补资源限制。

进程数可以设在个位数到几十，给测试框架留出启动子进程的余量，又不足以占满进程表。内存按题目需要设置地址空间上限，超限由内核处理、奖励记失败，避免等整机 OOM killer 去选择训练进程。可写目录也要有配额，写满视为失败，结束后照样删除目录。

清理时向进程组发信号。最初启动的 PID 可能已经退出，子进程却还在运行，只杀那个 PID 清不干净。因此用新进程组或新命名空间启动沙箱，并与训练进程分开，避免误杀。限制要在沙箱层生效，单在 Python 中 `try` 并捕获 `MemoryError` 挡不住整机内存耗尽。

下面示意独立会话和资源上限：

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

**同时评很多条，怎么配额度？**
每条设自己的上限，同时限制宿主机上并发沙箱数。并发数乘单条内存上限，要低于扣除训练后剩余的内存。
