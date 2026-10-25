---
id: baidu-qwen2-sft-implementation
section: rl-coding
order: 2
level: A
title: 百度文心后训练：用 Transformers / PyTorch 实现 Qwen2 的 SFT 训练
quick: "核心是数据契约：用 Qwen2 的 chat template 生成整段 input_ids 和 attention_mask，labels 里只有助手目标 token 保留真实 id，其余位置设 -100。在这之上写批次整理、因果语言模型前向（shift 由 HF 内部做）、BF16 加梯度累积、按 step 存检查点和留出集评测，就是最小训练闭环。"
tags:
  - Baidu
  - ERNIE
  - Qwen2
  - SFT
  - PyTorch
realInterview: true
status: published
format: markdown
updatedAt: 2026-08-21
sources:
  - title: 百度 - 大模型后训练实习生 二面（候选人原帖）
    url: https://www.nowcoder.com/discuss/864605093486682112
    type: candidate-first-hand
---

## 题目描述

实现一个Qwen2风格SFT训练中独立的label构造练习，只监督assistant指定位置，并演示把batch交给已提供的模型。本题不要求下载权重、搭建完整训练器或复刻Qwen2架构。

下面的函数接口、输入表示和边界口径是本卡采用的手册练习约定；公开面经未披露完整题干的部分，不视为面试官原文。默认输入满足约束，无需额外编写非法输入校验。

### 接口与输入

实现 `build_sft_labels(input_ids,assistant_mask,pad_id=-100)`，`input_ids`为[B,T]整数token张量，`assistant_mask`为同形布尔张量；`pad_id`是实际padding token编号，若使用默认-100则只屏蔽值等于-100的位置。另实现 `sft_step(model,batch)`，batch含`input_ids`、`attention_mask`、labels。

### 输出与约束

label与`input_ids`同形，`assistant_mask`为True且不是`pad_id`的位置复制原token编号，其余设为-100；不得改动`input_ids`。`sft_step`将三个字段原样传给提供的model并返回model输出的loss，不另做shift；shift由语言模型内部处理。

### 示例

```text
input_ids=[[10,20,30,0]], assistant_mask=[[False,False,True,True]], pad_id=0
labels=[[-100,-100,30,-100]]
原input_ids仍为[[10,20,30,0]]。
```

## 解题思路与参考答案

## 真题记录

- 公司：百度
- 团队 / 岗位：文心一言后训练
- 届别 / 流程：实习；二面
- 面试时间：2026-03-20
- 来源类型与可信度：牛客候选人原帖，A
- 原始措辞：**“使用transformers，pytorch实现Qwen2模型的SFT训练”**

这题的关键是监督微调（SFT）的数据契约：`input_ids` 仍然是整段对话，`labels` 里只有 assistant 的目标 token 保留真实 id，其余位置一律 $-100$。把这一点讲清楚，再搭出 collator、前向、精度、存档和评测，就是一个能跑的最小闭环。常见的错法有两种：把 prompt 整段截掉再训，用这个代替逐 token 标出损失范围；或者用错 Qwen2 的 chat template，special token 对不齐。

## 数据契约：template、labels=-100、多轮

先用这个模型自己的 `apply_chat_template` 把 messages 串起来，tokenize 之后 `labels = input_ids.clone()`，再把 system、user、role 分隔符、padding，以及不希望学习的 tool 观测结果（observation）都置成 `-100`。多轮对话每一段 assistant 都要标上，只留最后一轮会浪费前面的示范。超过 max length 要截断时，先保证 answer 还在，答案被截光了，这一步就是零梯度。

```python
def build_sft_labels(input_ids, assistant_mask, pad_id=-100):
    labels = input_ids.clone()
    labels[~assistant_mask] = -100
    labels[input_ids == pad_id] = -100  # if pad_id is a real token id
    return labels

def sft_step(model, batch):
    out = model(
        input_ids=batch["input_ids"],
        attention_mask=batch["attention_mask"],
        labels=batch["labels"],
    )
    return out.loss
```

`assistant_mask` 要对齐 template 算出来的字符或 token 跨度，别用「prompt 字符串长度 / 平均 token」去估。比如 Qwen2 的 `<|im_start|>` 这类 special token 必须和 tokenizer 版本一致，错一个 bos，整段都会错位。

## 训练闭环：collator、精度、eval、resume

collator 做动态 padding 或者 packing，`attention_mask` 和 labels 同步处理。用 BF16 加 gradient accumulation 来模拟大 batch。`AutoModelForCausalLM(..., labels=labels)` 内部已经做了 shift，也就是 logits[..., :-1] 对 labels[..., 1:]，自己别再 shift 一次。优化器配 cosine warmup，按 step 存 ckpt，能从 `global_step` resume。

留出集一定要有，instruction 格式、拒绝、工具调用各准备一个小评测集。train 损失（loss）在降、eval 格式却崩了，通常是 mask 把分隔符学进去了，或者 pad 进了 loss。常见的坑还有：template 不匹配、截断切掉了 answer、`pad_token` 没设导致 eos 被当成 pad、packing 跨样本没有切断 attention。现场把 mask 讲清楚就够了，Trainer 的参数表不用展示。

## 简单测试怎么写

把上面的实现保存为 `solution.py`，以下测试放在实现之后。数值测试使用参考实现相同的 PyTorch 或 NumPy 环境；浮点结果用带容差的比较。运行 `python3 solution.py`，成功时输出 `simple tests passed`，失败时按断言报错行定位。不要加 `-O`，它会跳过 `assert`。

用四个 token 区分 user、assistant 与 padding：只保留 assistant 的真实 token，其余写 -100。另检查原 input_ids 没被原地改写。这里测试标签构造，不需要加载模型。

```python
import torch
ids = torch.tensor([[10, 20, 30, 0]])
mask = torch.tensor([[False, False, True, True]])
labels = build_sft_labels(ids, mask, pad_id=0)
assert labels.tolist() == [[-100, -100, 30, -100]]
assert ids.tolist() == [[10, 20, 30, 0]]
print("simple tests passed")
```

## 追问

**只喂 answer 为什么不行？**
条件前缀必须在 context 里，否则模型学的是无条件语言模型，推理时和 user 对不上。Loss 不学输入提示（prompt），但输入里仍然要有 prompt。

**shift 由谁来做？**
HF 的 causal LM 内部会做。只有手写交叉熵损失（CE）时才自己写 `logits[:, :-1]` 对 `labels[:, 1:]`，见 `pdd-ce-handwrite`。

**多轮只训最后一轮行不行？**
可以当消融，但默认应该训所有 assistant 轮，只训最后一轮会浪费前面的示范。

**Qwen2 和 Qwen2.5 的 template 能混用吗？**
不能，template 必须跟 checkpoint 绑定。im_start 的规则一混用，mask 就全错了。

**loss 正常，但模型不听指令？**
查 mask 是不是把 user 也训了（数据泄漏成了续写），再查 eval 是不是用了同一个 template。

相关：`byte-sft-vs-grpo-objective`
