---
id: dt-rejection-sample-code
section: tech-screen
order: 5
level: A
title: CoderPad：手写拒绝采样，verifier 和 $k$ 怎么选？
quick: "同一道题采 $k$ 条回答，用独立 oracle 判对错，只留对的；生成器和验证器要分开。代码要处理全错、全对和过程假三种情况。$k$ 由当前 pass@$1$ 决定；没有 oracle 就不要写 `if judge(y): keep`。"
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
updatedAt: 2026-10-12
sources:
  - title: "STaR: Bootstrapping Reasoning With Reasoning"
    url: https://arxiv.org/abs/2203.14465
    type: primary
  - title: Training language models to follow instructions with human feedback
    url: https://arxiv.org/abs/2203.02155
    type: primary
  - title: Apple Intelligence Foundation Language Models Tech Report 2025
    url: https://machinelearning.apple.com/research/apple-foundation-models-tech-report-2025
    type: primary
---

拒绝采样就是：同一道题采 $k$ 条回答，用独立的 oracle 判对错，只留对的。生成器和验证器要分开，没有 oracle 就不要写 `if judge(y): keep`。代码要处理全错、全对和过程假三种情况；$k$ 也要由当前 pass@$1$ 决定。只写一个 $k=64$，却不谈空组和完全失败的题怎么处理，是这题最常见的缺口。

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

### 可执行测试

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

代码里的几种情况要逐个讲：

1. `verify` 的实现是执行、符号计算、标准答案或环境状态。AFM 在数学和代码上写的是 execution 和 ground truth。LLM-as-judge 可以当弱门，但不能当这个函数的默认实现，见 `dt-judge-bias`。
2. 全错：`kept` 为空。不要把「最像对的」塞进去，这类题应该降难度或换教师，见 `dt-self-improve`。
3. 全对：可以只留 1 条进监督微调（SFT），其余放进多样性备份，避免同一道题占满梯度。
4. 答案对、过程假：`verify` 要能返回 `reason="final_ok_process_bad"`。进 SFT 时只监督最终答案，或者直接丢掉。推理数据管线见 `dt-synth-reasoning`。

## $k$ 怎么选

设当前 pass@$1=p$，$k$ 条里至少一条成功的概率是 $1-(1-p)^k$。$p=0.2$ 时，$k=8$ 大约是 0.83；$p=0.02$ 时，$k=8$ 只有 0.15，大部分生成预算拿不到正确样本。所以现场先报 $p$，再选 $k$，不要上来就写 64。

失败的轨迹也有用。其他尝试路径可以拿去做偏好数据或恢复类 SFT，工具树那条见 `dt-synth-tool-mm`。拒绝采样本身不用负例，所以没有充分利用同一组回答之间的相对优劣。

## 追问

- **温度怎么设？** 过滤前略高一点，增加碰到正确推理链的机会；过门之后再看是否过长或过乱。温度不能代替验证器（verifier）。
- **多进程怎么写？** 生成可以并行。`verify` 如果用到共享数据库，要做隔离；工具环境必须能重置，否则并行会写脏状态。
- **为什么不直接拿教师的一条回答做 SFT？** 也可以。拒绝采样的价值在于从**当前学生**自己的分布里，留下它偶尔能做对的样本，可学性更好，见 `dt-teacher-bias`。
