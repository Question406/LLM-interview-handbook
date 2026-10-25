---
id: sys-sandbox
section: systems
order: 54
level: S
title: 系统：代码奖励的沙箱要隔离开什么？
quick: "每个代码样本放进独立的短命沙箱，关闭外网、只提供允许文件和只读测试，并限制 CPU、内存与时间。超时清理整棵进程树、奖励记失败；评分读取退出码和测试汇总，输出要截断。"
tags:
  - Post-train
  - Sandbox
  - RLVR
realInterview: false
status: published
format: markdown
updatedAt: 2026-09-24
sources:
  - title: DeepSeekMath
    url: https://arxiv.org/abs/2402.03300
    type: primary
---

代码奖励要在独立、短命的沙箱里执行每个样本。关闭网络，只提供题目允许的文件和只读测试，再限制 CPU、内存与时间，才能避免生成的程序影响训练环境。这是按代码执行类强化学习（RL）的常见隔离需求拟成，浏览器 agent 的沙箱另见 `design-browser-agent`。

网络关闭是为了防止程序下载答案或访问内网。工作目录只放允许的代码和测试，跑完就删除，不挂载训练集群的密钥、数据集或 checkpoint 目录。测试本身必须只读，避免模型修改评分依据。

超时要杀掉整棵进程树，包括程序拉起的子进程。只结束父进程，子进程可能继续写磁盘。奖励记失败或 0，并记录超时；不重试到成功，否则偶发慢程序会被算成稳定高奖励。

沙箱并发数要独立于训练卡数控制。队列满时让生成侧等待空位，避免无限制地在训练机启动进程，拖慢 GPU 的步时间。输出也要截断，几 GB 的日志就可能打满评测器。真正的奖励取退出码和测试框架汇总，程序自己打印的 "all tests passed" 不作为通过依据。

下面示意带超时、无网络和只读测试的执行入口：

```python
import subprocess

def run_tests(code, tests, timeout_s=5):
    # tests are mounted read-only; no network; fresh work dir
    proc = subprocess.run(
        ["sandbox-run", "--net", "none", "--timeout", str(timeout_s), "--tests", tests],
        input=code.encode(),
        capture_output=True,
        timeout=timeout_s + 1,
    )
    if proc.returncode != 0:
        return 0.0
    return 1.0
```

## 追问

**模型能修改测试吗？**
文件可写就能修改，所以测试要只读挂载，程序写在另一个目录。评分使用挂载的那份测试，避免误读程序目录里的同名文件。
