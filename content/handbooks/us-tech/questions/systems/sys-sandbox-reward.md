---
id: sys-sandbox-reward
section: systems
order: 55
level: A
title: 系统：沙箱奖励用哪一次运行的结果，不稳定的测试怎么处理？
quick: "一次提交的奖励取自这一次运行的退出码和测试汇总，超时、编译失败、崩溃都记为失败。相同代码和测试若重复运行结果不一致，应移出可验证训练集，避免把随机波动或重试成功当奖励。"
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

沙箱奖励要取自本次运行的退出码和测试汇总。一次提交对应一次运行，不能相信模型对 diff 的自我评价，也不能失败后反复重试直到通过。隔离执行的做法见 `sys-sandbox`。

奖励可以是全对得 1、否则得 0，也可以是通过测试数除以总数。部分通过时，要让不同题的奖励处在同一尺度：组里其他样本是 0/1，一条得到 0.3 仍可比较；测试数不同就先换算成比例。

超时、编译失败、运行时崩溃都是有效的失败结果，记最低档。若当作“没有评测”直接丢弃，会缩短 GRPO 的组、改变均值分母，和记 0 的训练含义不同。

可验证奖励还要求同一程序、同一测试的结果稳定。依赖当前时间、网络、未初始化内存或测试顺序的题可能重复运行就翻转，模型学到的是噪声。预处理时跑两遍，不一致就移出可验证集合，改用其他奖励或不用这道题。训练中某次超时也不重试到成功，否则慢程序和偶然成功反倒得到奖励。

下面返回本次通过比例，并把已识别的不稳定题标为不可用：

```python
def reward_once(run_tests, code, tests):
    result = run_tests(code, tests)  # one shot; do not retry a timeout
    if result.n_runs > 1 and result.passed != result.passed_again:
        return None  # flaky task, drop it
    return result.passed / result.total
```

## 追问

**公开测试还是隐藏测试用于奖励？**
奖励用隐藏测试。公开测试可放在提示中说明接口，但不进入奖励，避免模型背断言或只改打印来迎合公开用例。
