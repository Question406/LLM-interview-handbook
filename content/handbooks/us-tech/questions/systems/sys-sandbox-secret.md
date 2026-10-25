---
id: sys-sandbox-secret
section: systems
order: 68
level: A
title: 系统：沙箱里的报错会不会把密钥和数据路径漏给模型？
quick: "沙箱报错会作为观察回到模型，因此可能泄露路径、环境变量、密钥和隐藏测试。只向模型返回截断、脱敏的失败摘要；密钥与评分信息留在沙箱外，环境变量用白名单传入。"
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

会泄露。失败堆栈、标准输出只要回到模型上下文，就成了它下一轮能读到的信息。因此必须把评分结果与供模型纠错的失败摘要分开处理。进程隔离本身见 `sys-sandbox`，这里关注返回信息的边界。

例如异常里可能带绝对路径、用户名和内部主机名；如果沙箱继承训练进程的环境变量，生成的程序还能把密钥打印出来。测试框架再原样回传 stdout，密钥就进入了下一轮观察。隐藏测试的断言文本也会暴露输入和期望值，让模型记住断言；返回“第 3 个测试失败”即可。

我会给沙箱一份白名单环境，避免直接继承训练进程的 `environ`。stdout、stderr 截断到固定字节并去除绝对路径，密钥和评分用的隐藏测试留在沙箱外。外部评分进程对照隐藏用例，把通过与否送入奖励，只把处理后的摘要送入下一轮观察，两者不用同一个字符串。

完整失败日志可以留给人排查，但不能再写进 rollout 消息。下面是简化的摘要处理，重点是回传前先限制和脱敏：

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

**模型故意打印环境变量怎么办？**
白名单里没有密钥，它就读不到。输出仍要截断，防止超长打印耗尽评测器资源。
