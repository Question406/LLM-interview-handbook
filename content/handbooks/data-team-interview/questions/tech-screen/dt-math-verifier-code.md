---
id: dt-math-verifier-code
section: tech-screen
order: 22
level: A
title: CoderPad：数学合成怎么验， boxed 答案怎么抽，过程假怎么办？
quick: "从模型输出中抽最后的 `\\boxed{}` 或最终数字，规范化后与独立标准答案比较。无法解析或答案不符的样本不要留。最终答案正确、过程自相矛盾的，也不能直接作为 SFT 正例；模型不能凭自我评分代替独立金标。"
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
updatedAt: 2026-10-12
sources:
  - title: "Training Verifiers to Solve Math Word Problems (GSM8K)"
    url: https://arxiv.org/abs/2110.14168
    type: primary
  - title: "Let's Verify Step by Step"
    url: https://arxiv.org/abs/2305.20050
    type: primary
  - title: DeepSeek-R1
    url: https://arxiv.org/abs/2501.12948
    type: primary
---

我会先写：从输出里抽最后的 `\boxed{}` 或最终数字，和金标做规范化比较。抽不到或对不上就扔。答案对、中间步骤自相矛盾，不能当 监督微调（SFT） 正例。没有独立金标就不要用模型给自己判对。`dt-rejection-sample-code` 的 `oracle(y)` 在数学上要能写出来。别写 `if "correct" in judge(y)`。

GSM8K 公开做法是抽最终数字。R1 后来少用神经 PRM，可执行 / 可核对的用规则。

## 抽出答案，再规范化

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

### 可执行测试

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

金标本身也走 `canon_num`。`1/2` 和 `0.5` 应当过。单位、`\%`、千分位逗号是常见假阴。

## 过程假

如果中间把 3 写成 5，后来又凑出正确答案，只检查最终答案的验证器仍会判通过。过程监督需要进一步检查这些步骤：

1. 有独立计算器 / 代码执行：步骤里的等式可以再验，验不过当负例，见 `dt-prm-steps`。
2. 没有：宁可少留，不要把凑答案的链进 SFT。R1 蒸馏也是只留对的，过程胡编会教小模型说空话。
3. 抽不到 boxed：当失败，不要用第一处出现的数字（题面里的 2020 年会中招）。

$k$ 条全错：这题对当前模型太难，换题或降难度，不要把 $k$ 加到 256 硬刷，见 `dt-rejection-sample-code`。

## 追问

- **符号答案（$\pi/2$）？** 数字解析不够。能走符号库就走；否则只收精确字符串匹配，扩召回靠规范化表。
- **教师是 70B，学生 3B？** 过 verifier 的链才能蒸。端侧蒸馏见 `dt-ondevice-distill-data`。
- **用 LLM 当 verifier？** 可以标种子，不能当这轮 oracle。judge 会偏长、偏自信。
