---
id: sys-sandbox-reward
section: systems
order: 55
level: A
title: 系统：沙箱奖励用哪一次运行的结果，不稳定的测试怎么处理？
quick: >-
  奖励来自这一次运行的退出码和测试汇总，不来自模型对 diff 的自我评价。
  同一份代码跑两次结果不同，就不能当可验证奖励。这种题从训练集里拿掉，不要靠多跑几次取平均来掩盖不稳定性。
tags:
  - Post-train
  - Sandbox
  - Reward
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

沙箱隔离见 `sys-sandbox`。这道问奖励定义。可验证奖励假设「同一程序、同一测试，结果稳定」。

## 记哪一次

一次提交对应一次运行。通过的测试数除以总数，或直接 0 和 1。部分通过可以用通过比例，但比例的尺度要和全对全错的组放在一起看：一组里如果别人是 0/1，你是 0.3，优势仍然有意义；如果测试数量不同，先换成同一尺度。

超时、编译失败、运行时崩溃，都是这一次的结果，写成最低档，不要当成「没评测所以丢掉样本」。丢掉和记 0 对 GRPO 不一样：丢掉会让这组变短，均值的分母变了。

## 不稳定

依赖当前时间、网络、未初始化内存、或测试顺序的题目，跑两次会翻转。这种奖励会让模型学习随机噪声。预处理时把题跑两遍，不一致就移出可验证集合，改成别的奖励或不用。

训练中途不要因为「这次超时了再跑一次直到过」。那是在奖励慢和幸运，不是在奖励正确。

## 代码

```python
def reward_once(run_tests, code, tests):
    result = run_tests(code, tests)  # one shot; do not retry a timeout
    if result.n_runs > 1 and result.passed != result.passed_again:
        return None  # flaky task, drop it
    return result.passed / result.total
```

## 追问

**隐藏测试和公开测试？** 奖励用隐藏测试，否则模型可以背公开断言。公开测试可以放进提示里当接口说明，但不进奖励，避免只改打印去迎合公开用例。
