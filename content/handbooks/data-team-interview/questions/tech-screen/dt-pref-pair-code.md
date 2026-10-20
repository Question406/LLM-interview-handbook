---
id: dt-pref-pair-code
section: tech-screen
order: 16
level: A
title: CoderPad：偏好对怎么滤，margin、长度、差不多的对谁扔掉？
quick: "我会丢掉 $y_w\\approx y_l$ 的对、长度差过大的对、以及标注员自己标「难分」的对。能执行的任务，用独立 verifier 的结果计算 margin，不让生成模型给自己打分。 Llama 3 公开：edited > chosen > rejected，弱档不进 直接偏好优化（DPO）。"
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

先检查三项：标注是否为平局（tie）、回答长度比，以及偏好分差（margin）。丢掉 $y_w\approx y_l$ 的对、长度差过大的对、标注员自己标「难分」的对。能执行的任务用 验证器（verifier） 当 margin，不用模型自打分。`dt-reward-pref` 是 Panel 选 奖励模型（RM） 还是 直接偏好优化（DPO）；这里给你一堆 `(prompt, y1, y2, vote)`，别 `if vote: keep`。

Llama 3 公开：人对 chosen 再 edit 成更好的答案，弱档不进 DPO。长度：RM / 人都会偏长，见 `dt-length-hack-data`。过滤时要明确检查长度，不能指望损失函数自动消除偏差。

## 三道门，先长度后 margin

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

### 可执行测试

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

`trivial_lose`：rejected 是空、乱码、明显截断，模型只学「别输出空」。这种对可以进极小的安全桶，不要占 DPO 主集。

`n_edit>0`：有人改过 chosen，margin 可以放宽。这是 Llama 说 edited 更值钱的工程翻译。

## 可验证任务

数学 / 代码 / 工具状态：`margin` 来自独立 oracle，不是 RM。一对里 win 过测、lose 不过测，margin 记 1。两个都过或都不过，这对不进偏好，进 `dt-rejection-sample-code` 或扔掉。过程假（答案对、推理胡编）当 lose 可以，但 win 必须过程也过门，见 `dt-math-verifier-code`。

工具轨迹按 message 标，不要整段一个 vote，见 `dt-tool-turn-pref`。

## 追问

- **长度归一以后还滤 ratio 吗？** 仍滤。归一解决的是 RM 训练，滤 ratio 解决的是人标偏差已经写进对里。
- **RM 分差当 margin？** 可以当候选排序，门禁仍要人抽查。RM 如果偏爱长回答，分差也可能强化 `length_hack`。
- **丢掉弱对是不是浪费标注？** 弱对进 监督微调（SFT） 当「两种都可」或拿去改协议。把不确定的偏好强行用于 DPO，会给训练增加噪声。
