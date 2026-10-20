---
id: sys-sandbox-secret
section: systems
order: 68
level: A
title: 系统：沙箱里的报错会不会把密钥和数据路径漏给模型？
quick: >-
  堆栈、环境变量、挂载路径会随「测试失败」回到训练。模型下一轮能看见这些字符串。
  返回给模型的只能是截断过的失败摘要。评分用的隐藏测试和密钥留在沙箱外面。
tags:
  - Sandbox
  - Post-train
  - Security
realInterview: false
status: published
format: markdown
updatedAt: 2026-09-24
sources:
  - title: DeepSeekMath，奖励来自可执行的检查
    url: https://arxiv.org/abs/2402.03300
    type: primary
---

## 题怎么来的

隔离进程见 `sys-sandbox`。这道问的是信息从沙箱流回模型的那一条。按「失败信息也是观察」来拟。

## 会漏的东西

异常里常有绝对路径、用户名、内部主机名。环境变量若被传进沙箱，程序可以读出来打印，测试框架再把标准输出送回。模型于是在下一轮的上下文里看到密钥。

隐藏测试的断言文本如果原样返回，模型可以记住断言而不是写对实现。返回「第 3 个测试失败」就够。不要返回期望值和输入。

## 怎么切

沙箱进程的环境是一份白名单，不是训练进程的 `environ`。标准输出和标准错误截断到固定字节，去掉绝对路径。评分进程在沙箱外对照隐藏用例，只把通过与否送进奖励，把摘要送进下一轮观察。两份内容不要共用一个字符串。

训练日志可以留全量失败，供人查。那份日志不要写进 采样轨迹（rollout） 的消息。

## 代码

```python
import os

def failure_summary(stdout, max_bytes=512):
    text = stdout.decode(errors="replace")[:max_bytes]
    for secret in (os.environ.get("API_KEY", ""), "/data/", "/ckpt/"):
        if secret:
            text = text.replace(secret, "[redacted]")
    return text
```

## 追问

**模型故意打印环境变量呢？** 白名单里没有密钥，打印也没用。仍要截断，避免它用超长输出把评测器打满。
