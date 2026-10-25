---
id: dt-pref-pair-code
section: tech-screen
order: 16
level: A
title: CoderPad：偏好对怎么滤，margin、长度、差不多的对谁扔掉？
quick: "偏好对要先过滤再用：丢掉 $y_w\\approx y_l$ 的对、长度差过大的对，以及标注员自己标了「难分」的对。能执行的任务用独立 verifier 的结果当 margin，不让生成模型给自己打分。Llama 3 公开的排序是 edited > chosen > rejected，弱档不进 DPO。"
companies:
  - apple
tags:
  - Apple
  - CoderPad
  - Preference
  - DPO
realInterview: false
status: published
format: markdown
updatedAt: 2026-10-12
sources:
  - title: The Llama 3 Herd of Models
    url: https://arxiv.org/abs/2407.21783
    type: primary
  - title: Direct Preference Optimization
    url: https://arxiv.org/abs/2305.18290
    type: primary
  - title: Apple Intelligence Foundation Language Models Tech Report 2025
    url: https://machinelearning.apple.com/research/apple-foundation-models-tech-report-2025
    type: primary
---

## 题目描述

本题采用手册重构练习约定；下列接口、边界和样例是为了独立完成练习而明确的要求，不代表面试帖逐字题面。

对已经形成的偏好对执行过滤，保留具有有效偏好信号的 chosen/rejected 对。拒绝某对是正常输出，不属于非法函数参数。

### 输入与接口

- 输入 `Pair(prompt,win,lose,margin,tie,n_edit=0)`：win 是偏好回答，lose 是非偏好回答，margin 是评分差，tie 表示平局，`n_edit` 为人工修改 win 的次数。
- 实现 `ntok(s)` 和 `keep_pair(pair,min_margin=0.25,max_len_ratio=2.5,min_lose=8)`。ntok 按空白分词计数且至少为 1。

### 输出与约束

`keep_pair` 返回 `(是否保留,原因)`。必须依次检查：平局返回 tie；去首尾空白后回答相同返回 identical；lose 词数小于 `min_lose` 返回 `trivial_lose`；win/lose 词数比大于 `max_len_ratio` 返回 `length_hack`；分差不足且没有人工修改返回 `weak_margin`；其余返回 ok。

等于长度比上限或分差下限时不拒绝。`n_edit` 大于 0 只放宽 margin 检查，不绕过前四项。输入对象和文本不被修改。

### 示例

```text
p=Pair("q","one two three four","a b c d",margin=0.6,tie=False)
keep_pair(p,min_lose=2) -> (True,"ok")
p.tie=True
keep_pair(p,min_lose=2) -> (False,"tie")
```

## 解题思路与参考答案

每一对 `(prompt, y1, y2, vote)` 我先查三项：是不是平局、两个回答的长度比、margin 够不够。$y_w\approx y_l$ 的对、长度差过大的对、标注员自己标了「难分」的对，都丢掉。能执行的任务用 verifier 的结果当 margin，不用模型给自己打分。

比如 chosen 是把同一段正确答案重复了三遍，rejected 是一句不太确定的错答案，margin 0.9 看着很强，可这对教给模型的主要是「写长一点」。RM 和人都会偏爱长回答（见 `dt-length-hack-data`），这个偏差要在过滤时明确查，损失函数不会自动消掉它。Llama 3 的公开做法是让人把 chosen 再编辑成更好的答案，弱档不进 DPO。Panel 版 `dt-reward-pref` 问的是选 RM 还是 DPO，这里是把数据门写出来。

## 先长度，后 margin

检查顺序是平局、完全相同、平凡负例、长度比、margin。人工改写过的 chosen 更可信，margin 门放宽。

```python
from dataclasses import dataclass


@dataclass
class Pair:
    prompt: str
    win: str
    lose: str
    margin: float  # 人分差、RM 分差、或 verifier 0/1
    tie: bool
    n_edit: int = 0  # 人工改写 chosen 的次数


def ntok(s):
    return max(len(s.split()), 1)


def keep_pair(pair, min_margin=0.25, max_len_ratio=2.5, min_lose=8):
    """返回 (是否保留, 原因)。顺序：平局、相同、平凡负例、长度比、margin。"""
    if pair.tie:
        return False, "tie"
    if pair.win.strip() == pair.lose.strip():
        return False, "identical"
    if ntok(pair.lose) < min_lose:
        return False, "trivial_lose"
    ratio = ntok(pair.win) / ntok(pair.lose)
    if ratio > max_len_ratio:
        return False, "length_hack"
    # 人工改写过的 chosen 更可信，margin 门放宽
    if pair.margin < min_margin and pair.n_edit == 0:
        return False, "weak_margin"
    return True, "ok"
```

测试覆盖正常对、平局、相同、平凡负例、长度 hack 和改写放行：

```python
answer = "the capital of france is paris and it has been since the middle ages"
worse = "i think the capital of france might be lyon but i am not sure about it"

# 正常的对：长度相近、margin 足够
assert keep_pair(Pair("q", answer, worse, margin=0.6, tie=False)) == (True, "ok")

# 平局和两边完全相同的对丢掉
assert keep_pair(Pair("q", answer, worse, margin=0.6, tie=True)) == (False, "tie")
assert keep_pair(Pair("q", answer, answer + " ", margin=0.6, tie=False)) == (False, "identical")

# rejected 是空或极短：模型只学到「别输出空」
assert keep_pair(Pair("q", answer, "", margin=1.0, tie=False)) == (False, "trivial_lose")

# chosen 比 rejected 长太多：疑似长度偏好
long_answer = " ".join([answer] * 3)
assert keep_pair(Pair("q", long_answer, worse, margin=0.9, tie=False)) == (False, "length_hack")

# margin 弱的对丢掉，但人工改写过的 chosen 可以放行
assert keep_pair(Pair("q", answer, worse, margin=0.1, tie=False)) == (False, "weak_margin")
assert keep_pair(Pair("q", answer, worse, margin=0.1, tie=False, n_edit=1)) == (True, "ok")
```

每对常数时间，扫一遍就完。`trivial_lose` 指 rejected 是空、乱码或明显截断，这种对只能教会模型「别输出空」，可以放进一个极小的安全桶，别占 DPO 主集。`n_edit>0` 表示有人改过 chosen，margin 可以放宽，这就是 Llama 说 edited 更值钱的工程实现。

## 可验证任务

数学、代码和工具状态这类任务，`margin` 来自独立的 oracle。一对里 win 过了测试、lose 没过，margin 记 1；两个都过或都不过，这对不进偏好数据，转去 `dt-rejection-sample-code` 或者扔掉。过程是假的（答案对、推理胡编）可以当 lose，但 win 必须过程也过门，见 `dt-math-verifier-code`。工具轨迹要按 message 标注，别整段一个 vote，见 `dt-tool-turn-pref`。

## 简单测试怎么写

把完整参考实现和题中的可执行测试按顺序放进 `solution.py`，运行 `python3 solution.py`。测试依赖的库与参考实现相同。

例如，测试中的 `assert keep_pair(Pair("q", answer, worse, margin=0.6, tie=False)) == (True, "ok")` 就是一条结果检查；连同它前面的输入准备一起运行，不能只复制断言这一行。

把一次完整的操作序列当作一个测试：新建对象、执行操作，再检查返回值和操作后的状态。下一个独立场景重新建对象，避免历史状态掩盖错误。

先确认一个小场景的预期值，再运行题中的完整测试；出现断言失败时，从第一条失败的检查定位。断言全部通过只说明已覆盖的场景通过，还需要按本题约束补边界。

## 追问

**做了长度归一化，还要按长度比过滤吗？**
要。归一化解决的是 RM 训练时的偏差；按比例过滤处理的是人标偏差已经写进了这些对里。

**能用 RM 分差当 margin 吗？**
可以拿来给候选排序，门禁仍要人抽查。RM 如果偏爱长回答，分差也可能强化 `length_hack`。

**丢掉弱对是不是浪费标注？**
弱对可以进 SFT，当作「两种都可以」，或者拿去改协议。把不确定的偏好硬塞进 DPO，只会给训练加噪声。

**代码题两个回答都过了测试，怎么办？**
这对不进偏好数据，转去 rejection sampling 或者扔掉，见 `dt-rejection-sample-code`。

相关：`dt-reward-pref`、`dt-length-hack-data`、`dt-rejection-sample-code`、`dt-math-verifier-code`、`dt-tool-turn-pref`
