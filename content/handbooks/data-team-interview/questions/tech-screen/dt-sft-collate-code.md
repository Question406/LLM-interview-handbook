---
id: dt-sft-collate-code
section: tech-screen
order: 31
level: S
title: CoderPad：把变长对话组成 SFT batch，截断后还能保住监督信号吗？
quick: >-
  先按明确的截断规则裁剪，再按 token 位置构造 attention mask 和 labels；padding 与 prompt 不参与
  loss。不能通过 token 是否等于 pad_id 判断 padding，因为真实 token 也可能使用相同 ID。
companies:
  - apple
tags:
  - Apple
  - AFM 专项 2026-10
  - 完整编程练习
  - 题面补全 2026-10-27
realInterview: false
status: published
format: markdown
collapseAnswer: true
updatedAt: '2026-10-27'
sources:
  - title: PyTorch pad_sequence
    url: >-
      https://docs.pytorch.org/docs/2.14/generated/torch.nn.utils.rnn.pad_sequence.html
    type: primary
---

## 题目描述

本题为依据面试方向设计的原创练习，接口与数字均为练习约定。建议限时 25 分钟。

给一组已分词的单轮对话，构造 PyTorch SFT batch。每条样本含非空 prompt 和非空 response；不自动插入 BOS/EOS。先优先保留回答，再保留紧邻回答的 prompt 尾部，且至少保留一个 prompt token。

### 输入与接口

实现 `collate_sft(examples, max_length, pad_id=0)`。examples 是非空列表，元素为 `{"prompt": list[int], "response": list[int]}`。token ID 非负，允许真实 token 与 pad_id 相同；max_length 至少为 2。

### 输出与约束

返回含 `input_ids`、`attention_mask`、`labels` 的字典，均为 CPU long tensor，形状 `[B,L]`，L 为裁剪后 batch 内最大长度，且不超过 max_length。

对每条样本，令回答长度为 `r=min(len(response), max_length-1)`，保留 response 前 r 个 token；再保留 prompt 最后 `min(len(prompt), max_length-r)` 个 token。右侧补 pad。attention_mask 在真实位置为 1、补齐位置为 0；labels 在回答位置为对应 token，在 prompt 和补齐位置为 -100。本函数不 shift labels，下游 causal LM loss 负责 shift。不修改输入。

### 字段含义与不需要实现的部分

prompt 是模型的已知上下文，response 是希望模型学习生成的目标回答；两者的 token IDs 已经由 tokenizer 给出。`labels=-100` 的位置供后续 loss 忽略，不是新增 token ID。这里的 attention_mask 只是 `[B,L]` 的有效位置标记，不要求生成 `[B,L,L]` causal attention mask，也不调用模型或计算 loss。返回字典必须保留 input_ids、attention_mask、labels 三个字段，不能只返回拼接结果。

### 示例

```text
examples=[{prompt:[5,6,7],response:[8,9]}, {prompt:[2],response:[3]}]
max_length=4
input_ids     = [[6,7,8,9],[2,3,0,0]]
attention_mask= [[1,1,1,1],[1,1,0,0]]
labels        = [[-100,-100,8,9],[-100,3,-100,-100]]
```

## 解题思路与参考答案

先对每条样本完成截断并记录 prompt 长度，再统一分配 tensor。监督位置由结构决定，不由某个 token ID 决定。保留至少一个 prompt token，使第一个回答 token 仍有前一个位置的 logits 来预测。

```python
import torch


def collate_sft(examples, max_length, pad_id=0):
    rows = []
    for example in examples:
        response = example["response"][: max_length - 1]
        prompt = example["prompt"][-(max_length - len(response)) :]
        rows.append((prompt + response, len(prompt)))
    length = max(len(tokens) for tokens, _ in rows)
    ids = torch.full((len(rows), length), pad_id, dtype=torch.long)
    attention = torch.zeros_like(ids)
    labels = torch.full_like(ids, -100)
    for i, (tokens, prompt_length) in enumerate(rows):
        n = len(tokens)
        ids[i, :n] = torch.tensor(tokens)
        attention[i, :n] = 1
        labels[i, prompt_length:n] = ids[i, prompt_length:n]
    return {"input_ids": ids, "attention_mask": attention, "labels": labels}
```

分配和填充成本为 $O(BL)$。这只是 batch 构造器；attention_mask 只表示补齐位置，causal attention 由模型负责。

## 简单测试怎么写

将参考实现和下面测试依次放入 `solution.py`，运行 `python3 solution.py`，需要 PyTorch。先核对题面例子，再检查真实 pad ID、过长回答和输入未被修改。

```python
import copy

examples = [{"prompt": [5, 6, 7], "response": [8, 9]}, {"prompt": [2], "response": [3]}]
original = copy.deepcopy(examples)
batch = collate_sft(examples, 4)
assert batch["input_ids"].tolist() == [[6, 7, 8, 9], [2, 3, 0, 0]]
assert batch["attention_mask"].tolist() == [[1, 1, 1, 1], [1, 1, 0, 0]]
assert batch["labels"].tolist() == [[-100, -100, 8, 9], [-100, 3, -100, -100]]
assert examples == original
edge = collate_sft([{"prompt": [4, 0], "response": [0, 2, 3, 4]}], 3)
assert edge["input_ids"].tolist() == [[0, 0, 2]]
assert edge["attention_mask"].tolist() == [[1, 1, 1]]
assert edge["labels"].tolist() == [[-100, 0, 2]]
assert all(value.dtype == torch.long for value in edge.values())
minimum = collate_sft([{"prompt": [1, 2], "response": [3, 4]}], 2)
assert minimum["input_ids"].tolist() == [[2, 3]]
```

## 面试追问

**优先保留回答一定最好吗？** 不一定。工具参数可能依赖 prompt 开头的 schema，本题截断会损失它。生产中可以拒绝过长样本、结构化截断或切成有完整上下文的多条样本；需要按任务比较保留率和质量。

**mask 掉 prompt 能保证隐私吗？** 不能。prompt 仍参与 forward 计算并影响回答的 gradient，模型也可能记忆上下文。loss mask 不是数据授权、去标识或隐私机制的替代品。

**为什么这里没有手动 shift？** 常见 causal LM 接口在内部 shift；如果外部手写 loss 才对齐 `logits[:, :-1]` 与 `labels[:, 1:]`。重复 shift 会训练错位。
