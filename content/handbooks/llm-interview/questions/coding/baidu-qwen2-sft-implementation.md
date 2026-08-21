---
id: baidu-qwen2-sft-implementation
section: coding
order: 100
level: A
title: 百度文心后训练：用 Transformers / PyTorch 实现 Qwen2 的 SFT 训练
quick: >-
  面试里先写清 chat template 后的 input_ids、attention_mask 与 labels：只让 assistant target token 参与 loss，其余设为 -100；再给出
  batch collator、causal-LM forward、梯度累积 / precision、checkpoint 和 held-out eval 的最小训练闭环。
tags:
  - Baidu
  - ERNIE
  - Qwen2
  - SFT
  - PyTorch
realInterview: true
status: published
format: markdown
updatedAt: 2026-08-19
sources:
  - title: 百度 - 大模型后训练实习生 二面（候选人原帖）
    url: https://www.nowcoder.com/discuss/864605093486682112
    type: candidate-first-hand
---

## 真题记录

- 公司：百度
- 团队 / 岗位：文心一言后训练
- 届别 / 流程：实习；二面
- 面试时间：2026-03-20
- 来源类型与可信度：牛客候选人原帖，A
- 原始措辞：**“使用transformers，pytorch实现Qwen2模型的SFT训练”**

陷阱是「把 prompt 整段截掉再训」代替 **逐 token loss mask**，或用错 Qwen2 chat template 导致 special token 对不齐。SFT 的数据契约是：`input_ids` 仍是整段对话，`labels` 里只有 assistant 目标为真实 id，其余 $-100$。后训练目标对比见 `byte-sft-vs-grpo-objective`；本题要的是能跑的最小闭环。

## 数据契约：template、labels=-100、多轮

用该模型的 `apply_chat_template` 串行化 messages，tokenize 后 `labels = input_ids.clone()`，把 system、user、role 分隔符、padding、以及不希望学习的 tool observation 置为 `-100`。多轮则 **每段 assistant 都标**，不能只留最后一轮。截断发生在 max length 时，先保证 answer 还在；把答案截光等于这步零梯度。

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

`assistant_mask` 应对齐 template 算出的字符/token 跨度，不要用「prompt 字符串长度 / 平均 token」估。Qwen2 的 `<|im_start|>` 等必须与 tokenizer 版本一致，错一个 bos 就会整段错位。

## 训练闭环：collator、精度、eval、resume

动态 padding 或 packing；`attention_mask` 与 labels 同步。BF16 + gradient accumulation 模拟大 batch。`AutoModelForCausalLM(..., labels=labels)` 内部已做 shift：logits[..., :-1] 对 labels[..., 1:]，不要自己再 shift 一次。Optimizer / cosine warmup、按 step 存 ckpt、从 `global_step` resume。

**必须有 held-out**：instruction 格式、拒绝、工具调用各一薄集。train loss 下降但 eval 格式崩，通常是 mask 把分隔符学进去了，或 pad 进了 loss。常见坑：template 不匹配、截断切掉 answer、`pad_token` 未设导致 eos 当 pad、packing 跨样本没有切断 attention。面试把 mask 讲清楚，比展示 Trainer 参数表更像做过文心后训练。

## 追问

- **为什么不能只喂 answer？** 条件前缀必须在 context 里，否则模型学的是无条件语言模型，推理时对不上 user。Loss 不学 prompt，输入仍要 prompt。
- **shift 谁做？** HF causal LM 内部做。手写 CE 才自己 `logits[:, :-1]` 对 `labels[:, 1:]`，见 `pdd-ce-handwrite`。
- **多轮只训最后一轮？** 可以当消融，但默认应训所有 assistant。只训最后一轮会浪费前面示范。
- **Qwen2 和 Qwen2.5 template？** 必须跟 checkpoint 绑定。混用 im_start 规则会让 mask 全错。
- **loss 正常但不会听指令？** 查 mask 是否把 user 也训了（数据泄漏成续写），以及 eval 是否用同一 template。
