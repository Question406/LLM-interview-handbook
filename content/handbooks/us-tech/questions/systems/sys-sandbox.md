---
id: sys-sandbox
section: systems
order: 54
level: S
title: 系统：代码奖励的沙箱要隔离开什么？
quick: >-
  每个样本一个短命环境：没有外网，文件系统只给这份代码和测试，CPU、内存、时间有上限。
  超时杀掉进程，奖励记失败。不要在训练机上直接 subprocess 跑模型写出来的程序。
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

## 题怎么来的

用单测做奖励时，infra 题会从算法转到「这段代码跑在哪」。按代码执行类 强化学习（RL） 的常见隔离要求拟的。浏览器 agent 的沙箱是另一类，见 `design-browser-agent`。

## 边界

模型生成的程序和评测脚本放进一个新环境。网络关掉，否则程序可以下载答案或打内网。工作目录里只有题目允许的文件，跑完就删。不能挂上训练集群的密钥、数据集或 checkpoint 目录。

CPU 时间和内存设上限。超时就杀进程树，包括它拉起的子进程。只杀父进程，子进程还在写磁盘。奖励记为失败或 0，并记一条超时，不要重试到成功为止。重试会让「偶发跑得慢」变成稳定的高奖励。

并行度和训练卡分开。沙箱队列满了，生成侧要停下来等空位，而不是在训练机上无限制地起进程。一台机器被打满，GPU 步时间会跟着抖。

## 不能信的输出

标准输出要截断。程序可以打出几 GB 日志，使评测器超出资源上限。退出码和测试框架的汇总才是奖励。把模型自己打印的 "all tests passed" 当成奖励，等于没跑测试。

## 代码

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

**测试本身会不会被模型改掉？** 会，如果测试文件可写。测试只读挂载，程序写在别的目录。评分用挂载进来的那份，不用程序目录里同名的文件。
