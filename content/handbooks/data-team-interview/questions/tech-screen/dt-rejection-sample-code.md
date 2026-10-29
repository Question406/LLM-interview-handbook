---
id: dt-rejection-sample-code
section: tech-screen
order: 5
level: A
title: CoderPad：手写 rejection sampling，verifier 和 $k$ 怎么选？
quick: >-
  同一道题采 $k$ 条回答，用独立 oracle 判对错，只留对的；生成器和 verifier 要分开。代码要处理全错、全对和过程假三种情况。$k$ 由当前
  pass@$1$ 决定；没有 oracle 就别写 `if judge(y): keep`。
companies:
  - apple
tags:
  - Apple
  - CoderPad
  - Rejection Sampling
  - Verifier
realInterview: false
status: published
format: markdown
updatedAt: 2026-10-12T00:00:00.000Z
sources:
  - title: 'STaR: Bootstrapping Reasoning With Reasoning'
    url: 'https://arxiv.org/abs/2203.14465'
    type: primary
  - title: Training language models to follow instructions with human feedback
    url: 'https://arxiv.org/abs/2203.02155'
    type: primary
  - title: Apple Intelligence Foundation Language Models Tech Report 2025
    url: >-
      https://machinelearning.apple.com/research/apple-foundation-models-tech-report-2025
    type: primary
---

## 题目描述

本题采用手册重构练习约定；下列接口、edge cases 和样例是为了独立完成练习而明确的要求。

为一个 prompt 生成多个候选回答，并按 verifier 结果分成可保留样本和失败样本。

### 输入与接口

实现 Sample(prompt, completion, ok, reason) 数据记录，以及 `rejection_sample`(prompt, generate, verify, k=8)。prompt 为字符串；generate(prompt) 每次返回一个候选字符串；verify(prompt, completion) 返回 (是否通过, 原因字符串)；k 为正整数。

### 输出与约束

返回 {"kept": Sample 列表, "failures": Sample 列表}。每条记录保留对应 prompt、原始 completion 和验证结果。两个列表分别保持候选的生成顺序。

必须恰好生成并验证 k 次，首次成功后也继续。全部失败时 kept 为空，全部成功时 failures 为空。生成器和 verifier 的行为由调用者提供，本函数不另加随机性或 deduplication。

### 示例

```text
prompt="2+2"，k=4
generate 依次返回 ["4","5","4","3"]
verify 对 "4" 返回 (True,"ok")，其他返回 (False,"wrong_answer")
结果 kept 的 completion 为 ["4","4"]
结果 failures 的 completion 为 ["5","3"]，reason 均为 "wrong_answer"
```

## 解题思路与参考答案

我会对同一道题采 $k$ 条回答，用独立的 oracle 判对错，只留对的，生成器和 verifier 分开写。没有 oracle 就别写 `if judge(y): keep`。

这题最常见的缺口是只写一个 $k=64$，却不谈空组和完全失败的题怎么处理。比如一道题采了 8 条全错，`kept` 就是空的，这时候别把「最像对的」塞进去；反过来 8 条全对，也没必要 8 条都进 SFT。还有答案对、过程假的情况，verifier 要能单独报出来。所以代码要分别处理全错、全对和过程假，$k$ 也要由当前 pass@$1$ 决定。

## 生成与验证分开

```python
from dataclasses import dataclass


@dataclass
class Sample:
    prompt: str
    completion: str
    ok: bool
    reason: str


def rejection_sample(prompt, generate, verify, k=8):
    """对同一题采 k 条，用独立验证器分成通过和失败两组。

    generate(prompt) -> str；verify(prompt, y) -> (ok, reason)。
    返回 {"kept": [...], "failures": [...]}；全错时 kept 为空，由调用方决定换题或降难度。
    """
    if k <= 0:
        raise ValueError("k must be positive")
    kept = []
    failures = []
    for _ in range(k):
        completion = generate(prompt)
        ok, reason = verify(prompt, completion)
        row = Sample(prompt, completion, ok, reason)
        if ok:
            kept.append(row)
        else:
            failures.append(row)
    return {"kept": kept, "failures": failures}
```

测试用两个测试桩覆盖混合、全错、全对和过程假：

```python
import itertools


def scripted_generator(outputs):
    """测试桩：按顺序吐出预设回答的生成器。"""
    it = itertools.cycle(outputs)
    return lambda prompt: next(it)


def exact_verifier(gold):
    """测试桩：和标准答案精确比较的验证器。"""
    return lambda prompt, y: (True, "ok") if y == gold else (False, "wrong_answer")


# 混合结果：对的进 kept，错的带原因进 failures
generator = scripted_generator(["4", "5", "4", "3"])
result = rejection_sample("2+2?", generator, exact_verifier("4"), k=4)
assert [s.completion for s in result["kept"]] == ["4", "4"]
assert [s.reason for s in result["failures"]] == ["wrong_answer", "wrong_answer"]

# 全错：kept 为空，不把「最像对的」塞进去
result = rejection_sample("hard", scripted_generator(["x"]), exact_verifier("y"), k=3)
assert result["kept"] == []
assert len(result["failures"]) == 3

# 全对：k 条都保留，调用方再决定只取 1 条
result = rejection_sample("easy", scripted_generator(["y"]), exact_verifier("y"), k=3)
assert len(result["kept"]) == 3

# 验证器可以返回更细的失败原因，例如过程假
process_check = lambda prompt, y: (False, "final_ok_process_bad")
result = rejection_sample("p", scripted_generator(["y"]), process_check, k=1)
assert result["failures"][0].reason == "final_ok_process_bad"
```

写完我会逐个讲这几种情况。`verify` 的实现是执行、符号计算、标准答案或环境状态，AFM 在数学和代码上写的是 execution 和 ground truth；LLM-as-judge 可以当弱门，但不能当这个函数的默认实现，见 `dt-judge-bias`。全错时 `kept` 为空，这类题该降难度或换 teacher，见 `dt-self-improve`。全对时可以只留 1 条进 SFT，其余放进多样性备份，免得同一道题占满 gradient。答案对、过程假时，`verify` 返回 `reason="final_ok_process_bad"`，进 SFT 时只监督最终答案，或者直接丢掉，推理 data pipeline 见 `dt-synth-reasoning`。

## $k$ 怎么选

设当前 pass@$1=p$，$k$ 条里至少一条成功的概率是 $1-(1-p)^k$。$p=0.2$ 时，$k=8$ 大约是 0.83；$p=0.02$ 时，$k=8$ 只有 0.15，大部分生成预算拿不到正确样本。所以现场先报 $p$，再选 $k$，别上来就写 64。成本基本就是 $k$ 次生成加 $k$ 次验证。

失败的 trajectories 也有用，其他尝试路径可以拿去做 preference data 或恢复类 SFT，工具树那条见 `dt-synth-tool-mm`。rejection sampling 本身不用负例，所以没有充分利用同一组回答之间的相对优劣。

## 简单测试怎么写

把完整参考实现和题中的可执行测试按顺序放进 `solution.py`，运行 `python3 solution.py`。测试依赖的库与参考实现相同。

例如，测试中的 `assert [s.completion for s in result["kept"]] == ["4", "4"]` 就是一条结果检查；连同它前面的输入准备一起运行，不能只复制 assertion 这一行。

把一次完整的操作序列当作一个测试：新建对象、执行操作，再检查返回值和操作后的状态。下一个独立场景重新建对象，避免历史状态掩盖错误。

先确认一个小场景的预期值，再运行题中的完整测试；出现 assertion 失败时，从第一条失败的检查定位。assertion 全部通过只说明已覆盖的场景通过，还需要按本题约束补充 edge-case tests。

## 追问

**温度怎么设？**
过滤前略高一点，增加碰到正确 chain-of-thought 的机会；通过检查后再看是否过长或过乱。温度代替不了 verifier。

**多进程怎么写？**
生成可以并行。`verify` 如果用到共享数据库，要做隔离；工具环境必须能重置，不然并行会写脏状态。

**为什么不直接拿 teacher 的一条回答做 SFT？**
也可以。rejection sampling 的价值在于从**当前 student**自己的分布里，留下它偶尔能做对的样本，learnability 更好，见 `dt-teacher-bias`。

**能用 LLM judge 当 verify 吗？**
只能当弱门。默认实现应该是执行、符号计算、标准答案或环境状态，judge 的偏差见 `dt-judge-bias`。

相关：`dt-judge-bias`、`dt-self-improve`、`dt-synth-reasoning`、`dt-synth-tool-mm`、`dt-teacher-bias`
