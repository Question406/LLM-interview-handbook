---
id: dt-math-verifier-code
section: tech-screen
order: 22
level: A
title: CoderPad：数学合成怎么验， boxed 答案怎么抽，过程假怎么办？
quick: >-
  从模型输出里抽最后一个 `\boxed{}` 或最终数字，规范化后和独立的标准答案比较，抽不到或对不上就扔。最终答案对、过程自相矛盾的样本，也别直接当
  SFT 正例。没有独立 gold labels 时，不能让模型给自己判对。
companies:
  - apple
tags:
  - Apple
  - CoderPad
  - Verifier
  - Math
realInterview: false
status: published
format: markdown
updatedAt: 2026-10-12T00:00:00.000Z
sources:
  - title: Training Verifiers to Solve Math Word Problems (GSM8K)
    url: 'https://arxiv.org/abs/2110.14168'
    type: primary
  - title: Let's Verify Step by Step
    url: 'https://arxiv.org/abs/2305.20050'
    type: primary
  - title: DeepSeek-R1
    url: 'https://arxiv.org/abs/2501.12948'
    type: primary
---

## 题目描述

本题采用手册重构练习约定；下列接口、edge cases 和样例是为了独立完成练习而明确的要求。

实现一个限定格式的数学答案 verifier：从模型回答中提取最终答案，允许同一个有理数用整数、小数或分数表示，并给出能定位的判定原因。本题不要求通用代数推理。

### 输入与接口

- `last_boxed(text)` 接受回答字符串，优先取最后一个不含嵌套花括号的 `\boxed{...}` 内容；没有 boxed 时取去掉千分位逗号后的最后一个数字片段。
- `canon_num(s)` 接受裸答案字符串，将可解析的有理数规范成最简分数字符串。
- `math_ok(pred,gold)` 接受预测回答和标准答案；gold 可以是裸答案或带 boxed 的文本。

### 输出与约束

`last_boxed` 找不到答案返回 None。`canon_num` 去掉首尾空白、逗号和美元符号；不能作为有理数解析的内容转为小写字符串供精确比较。`math_ok` 返回 `(bool,reason)`：一致为 ok，不一致为 mismatch，抽不到预测答案为 unparsed。

支持带正负号的整数、十进制小数和分数；不同数值即使文本相近也不能判对。符号表达式只做规范化后的精确字符串比较，不负责证明等价。

### 示例

```text
last_boxed("先得到 1，修正后 \boxed{2}") -> "2"
canon_num("0.5") -> "1/2"
math_ok("答案是 \boxed{0.5}","1/2") -> (True,"ok")
math_ok("无法确定","2") -> (False,"unparsed")
```

## 解题思路与参考答案

我会从输出里抽最后一个 `\boxed{}`，没有就取最后一个数字，规范化之后和 gold labels 比，抽不到或对不上就扔。这题就是把 `dt-rejection-sample-code` 里的 `oracle(y)` 在数学上写出来，别写成 `if "correct" in judge(y)`，没有独立 gold labels 时也不能让模型给自己判对。

举个例子，输出是「In 2020 we had 3 apples, so \boxed{5}」，要拿到的是 5。抽不到 boxed 就退回取第一处出现的数字的话，题面里的「2020 年」就成了答案。抽最终数字是 GSM8K 的公开做法；R1 后来也少用神经 PRM，凡是可执行、可核对的，都用规则来判。

## 抽出答案，再规范化

规范化用 `Fraction`，这样 `1/2`、`0.5`、`4/2` 和 `2` 都能落到同一个值上，解析不了的符号答案退回小写字符串精确匹配。

```python
import re
from fractions import Fraction

BOXED = re.compile(r"\\boxed\{([^{}]*)\}")
NUMBER = re.compile(r"[-+]?(?:\d+\.\d+|\d+)/\d+|[-+]?\d+\.\d+|[-+]?\d+")


def last_boxed(text):
    """优先取最后一个 \\boxed{}；没有时退回最后一个数字；都没有返回 None。"""
    found = BOXED.findall(text)
    if found:
        return found[-1].strip()
    numbers = NUMBER.findall(text.replace(",", ""))
    return numbers[-1] if numbers else None


def canon_num(s):
    """把数字答案规范成最简分数字符串：1/2、0.5、4/2 和 2 各自对得上。

    解析不了的答案（符号表达式）退回小写字符串，只能精确匹配。
    """
    s = s.strip().replace(",", "").replace("$", "")
    try:
        value = Fraction(s)
    except (ValueError, ZeroDivisionError):
        return s.lower()
    return str(value)


def math_ok(pred, gold):
    """返回 (是否正确, 原因)。gold 可以是裸答案，也可以带 \\boxed{}。"""
    predicted = last_boxed(pred)
    expected = last_boxed(gold) if "\\boxed" in gold else gold
    if predicted is None or expected is None:
        return False, "unparsed"
    if canon_num(predicted) == canon_num(expected):
        return True, "ok"
    return False, "mismatch"
```

测试覆盖取最后一个 boxed、千分位、分数小数整数、除零和端到端：

```python
# 取最后一个 boxed，而不是题面里先出现的数字
assert last_boxed(r"In 2020 we had 3 apples, so \boxed{5}") == "5"
assert last_boxed(r"\boxed{1} then corrected: \boxed{2}") == "2"

# 没有 boxed 时退回最后一个数字，千分位逗号先去掉
assert last_boxed("The total is 1,234 dollars") == "1234"
assert last_boxed("no answer here") is None

# 分数、小数、整数写法规范到同一个值
assert canon_num("1/2") == canon_num("0.5")
assert canon_num("4/2") == canon_num("2")
assert canon_num("2.0") == canon_num("2")
assert canon_num("$1,000") == canon_num("1000")

# 除零和符号答案不崩，退回字符串比较
assert canon_num("1/0") == "1/0"
assert canon_num(r"\pi/2") == r"\pi/2"

# 端到端：对、错、抽不到答案
assert math_ok(r"... so the answer is \boxed{0.5}", "1/2") == (True, "ok")
assert math_ok(r"... \boxed{3}", r"\boxed{4/2}") == (False, "mismatch")
assert math_ok("I am not sure", "2") == (False, "unparsed")
```

每条输出只扫一遍正则，成本可以忽略。gold labels 本身也要过 `canon_num`，`1/2` 和 `0.5` 应当判为相同。单位、`\%`、千分位逗号是最常见的假阴性来源。

## 答案对，过程是假的

如果中间把 3 写成 5，后来又凑出了正确答案，只检查最终答案的 verifier 照样判通过。怎么处理看手里有没有能核对步骤的工具。有独立的计算器或代码执行，步骤里的等式可以逐个再验，验不过就当负例，见 `dt-prm-steps`。没有的话只留能确认的样本，凑答案的 chain-of-thought 不进 SFT；R1 distillation 也只留做对的样本，过程胡编的链会教 small model 说空话。

如果某题采的 $k$ 条全错，说明这题对当前模型太难，该换题或降难度，$k$ 不必加到 256 硬刷，见 `dt-rejection-sample-code`。

## 简单测试怎么写

把完整参考实现和题中的可执行测试按顺序放进 `solution.py`，运行 `python3 solution.py`。测试依赖的库与参考实现相同。

例如，测试中的 `assert last_boxed(r"In 2020 we had 3 apples, so \boxed{5}") == "5"` 就是一条结果检查；连同它前面的输入准备一起运行，不能只复制 assertion 这一行。

先手算一个普通输入，再补题目允许的最小输入和一个容易写错的分支。每条 assertion 都写出明确预期值；只打印结果还需要人眼判断，`assert` 能在不符合预期时直接报错。

先确认一个小场景的预期值，再运行题中的完整测试；出现 assertion 失败时，从第一条失败的检查定位。assertion 全部通过只说明已覆盖的场景通过，还需要按本题约束补充 edge-case tests。

## 追问

**符号答案（比如 $\pi/2$）怎么判？**
数字解析处理不了。能用符号库就用；不能的话只收精确字符串匹配，召回靠规范化表来扩。

**teacher 是 70B、student 是 3B，怎么蒸？**
只有过了 verifier 的链才能拿去蒸。distillation 阶段该用哪些数据见 `dt-ondevice-distill-data`。

**能用 LLM 当 verifier 吗？**
可以用来标 seed 数据，别当这一轮的 oracle，因为 judge 会偏向更长、更自信的回答。

**答案对、过程错的样本能当负例吗？**
有工具能逐步验算时可以，验不过的步骤就当负例；没有工具时只留能确认的样本，这类链不进 SFT。

相关：`dt-rejection-sample-code`、`dt-prm-steps`、`dt-ondevice-distill-data`
